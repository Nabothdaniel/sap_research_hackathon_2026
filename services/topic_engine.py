"""
services/topic_engine.py
Generates fresh, unique research topics each run by:
  1. Pulling trending crypto/AI/Web3 topics from Ace Data Cloud web search
  2. Detecting on-chain events (price moves, new protocols, volume spikes)
  3. Extracting topics from search results so every run is genuinely different

This is what separates legitimate volume from artificial loops.
Every call has a real reason to exist.
"""

import os
import re
import httpx
import asyncio
from datetime import datetime
from loguru import logger
from typing import Optional


# Seed queries that surface genuinely different results each time
SEED_QUERIES = [
    "crypto breaking news today",
    "solana ecosystem new projects",
    "DeFi protocol launches this week",
    "AI blockchain integration latest",
    "Web3 developer activity trending",
    "on-chain metrics unusual activity",
    "new token launches solana",
    "blockchain funding rounds announced",
]

# Price change threshold to trigger event-based research
PRICE_MOVE_THRESHOLD = 0.04  # 4% move triggers a deep dive


class TopicEngine:
    def __init__(self):
        self.ace_api_key = os.getenv("ACE_API_KEY")
        self.ace_base_url = os.getenv("ACE_BASE_URL", "https://api.acedata.cloud")
        self.headers = {
            "Authorization": f"Bearer {self.ace_api_key}",
            "Content-Type": "application/json",
        }
        self._used_topics: set[str] = set()  # avoid repeating within a session

    # ──────────────────────────────────────────
    #  Pull trending topics from live web search
    # ──────────────────────────────────────────

    async def fetch_trending_topics(self, max_topics: int = 6) -> list[str]:
        """
        Search for what's actually trending right now and extract
        specific topics from the results. Every run returns different topics
        because the web changes.
        """
        today = datetime.utcnow().strftime("%B %d %Y")
        topics: list[str] = []

        # Pick 2 seed queries at random (based on current minute — deterministic but varied)
        minute = datetime.utcnow().minute
        seed_a = SEED_QUERIES[minute % len(SEED_QUERIES)]
        seed_b = SEED_QUERIES[(minute + 3) % len(SEED_QUERIES)]

        for seed in [seed_a, seed_b]:
            extracted = await self._search_and_extract(f"{seed} {today}")
            topics.extend(extracted)

        # Deduplicate and remove already-used topics this session
        unique = []
        for t in topics:
            normalized = t.lower().strip()
            if normalized not in self._used_topics and t not in unique:
                unique.append(t)
                self._used_topics.add(normalized)

        result = unique[:max_topics]
        logger.info(f"[TopicEngine] Fetched {len(result)} fresh trending topics")
        return result

    async def _search_and_extract(self, query: str) -> list[str]:
        """Run a web search and pull specific topic strings from titles/snippets."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ace_base_url}/web-search",
                    headers=self.headers,
                    json={"query": query, "max_results": 8, "include_snippets": True},
                    timeout=20,
                )
                response.raise_for_status()
                results = response.json().get("results", [])

            topics = []
            for r in results:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                extracted = self._extract_topic_from_text(title + " " + snippet)
                if extracted:
                    topics.append(extracted)

            return topics

        except Exception as e:
            logger.warning(f"[TopicEngine] Search failed for '{query}': {e}")
            return self._fallback_topics()

    def _extract_topic_from_text(self, text: str) -> Optional[str]:
        """
        Pull a clean, specific topic phrase from a title or snippet.
        Looks for named projects, tokens, events.
        """
        # Match patterns like: "Solana hits $200", "Uniswap v4 launch", "LayerZero airdrop"
        patterns = [
            r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})\s+(?:hits|launches|announces|surges|drops|integrates|releases|upgrades)',
            r'\b([A-Z][a-zA-Z]{2,}(?:\s+v?\d)?)\s+(?:protocol|network|chain|token|dao|dex|bridge)',
            r'(?:new|latest)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+(?:update|feature|partnership)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                topic = match.group(1).strip()
                if len(topic) > 3 and topic.lower() not in {"the", "this", "that", "with"}:
                    return topic
        return None

    def _fallback_topics(self) -> list[str]:
        """Sensible fallbacks if search fails — still varied by time."""
        hour = datetime.utcnow().hour
        base = [
            "Solana validator performance",
            "DeFi liquidity trends",
            "AI agent token economy",
            "Cross-chain bridge security",
            "Layer 2 adoption metrics",
            "NFT market recovery signals",
            "DAO governance participation",
            "Stablecoin depeg risk analysis",
        ]
        # Rotate based on hour so fallbacks vary across runs
        rotated = base[hour % len(base):] + base[:hour % len(base)]
        return rotated[:3]

    # ──────────────────────────────────────────
    #  Event-driven triggers
    # ──────────────────────────────────────────

    async def detect_price_events(self, tokens: list[str] = None) -> list[dict]:
        """
        Check if any major tokens have moved significantly.
        If yes, those become priority research topics.
        Returns list of {token, change_pct, direction} dicts.
        """
        tokens = tokens or ["SOL", "BTC", "ETH", "JUP", "BONK", "WIF"]
        events = []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ace_base_url}/web-search",
                    headers=self.headers,
                    json={
                        "query": f"crypto price movement {' '.join(tokens)} 24h change today",
                        "max_results": 5,
                    },
                    timeout=20,
                )
                response.raise_for_status()
                results = response.json().get("results", [])

            # Extract price move signals from snippets
            for r in results:
                text = r.get("snippet", "") + r.get("title", "")
                detected = self._parse_price_event(text, tokens)
                events.extend(detected)

        except Exception as e:
            logger.warning(f"[TopicEngine] Price event detection failed: {e}")

        logger.info(f"[TopicEngine] Detected {len(events)} price events")
        return events

    def _parse_price_event(self, text: str, tokens: list[str]) -> list[dict]:
        """Look for percentage moves in text for known tokens."""
        events = []
        for token in tokens:
            # Match patterns like "SOL up 7.3%" or "BTC drops 5%"
            pattern = rf'\b{token}\b.{{0,30}}?(up|down|surge|drop|gains?|loses?).{{0,20}}?(\d+\.?\d*)\s*%'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                direction = match.group(1).lower()
                pct = float(match.group(2)) / 100
                if pct >= PRICE_MOVE_THRESHOLD:
                    events.append({
                        "token": token,
                        "change_pct": pct,
                        "direction": "up" if direction in ("up", "surge", "gain", "gains") else "down",
                        "topic": f"{token} price {direction} {match.group(2)}% analysis",
                    })
        return events

    # ──────────────────────────────────────────
    #  Master topic list builder
    # ──────────────────────────────────────────

    async def build_run_topics(self) -> list[str]:
        """
        Build the final topic list for one agent run.
        Combines: trending topics + price event topics.
        Every run is different because it's anchored to real-time data.
        """
        # Run both in parallel
        trending_task = self.fetch_trending_topics(max_topics=4)
        events_task = self.detect_price_events()

        trending, events = await asyncio.gather(trending_task, events_task)

        # Priority: event-driven topics first, then trending
        event_topics = [e["topic"] for e in events]
        all_topics = event_topics + [t for t in trending if t not in event_topics]

        # Cap at 6 — enough volume without looking spammy
        final = all_topics[:6]

        logger.success(
            f"[TopicEngine] Run topics ({len(final)}): {final}"
        )
        return final
