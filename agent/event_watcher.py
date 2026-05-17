"""
agent/event_watcher.py
Monitors real signals and fires the agent only when something worth
researching actually happens. This is what makes volume legitimate —
every run is justified by an external trigger, not a timer.

Triggers:
  - Price move > threshold on major tokens
  - New hour (time-based but anchored to fresh trending data)
  - Manual topic injection (from Telegram bot or CLI)
  - Solana slot milestone (every N slots = new data worth indexing)
"""

import os
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from typing import Callable, Awaitable

from services.topic_engine import TopicEngine


# How often to check for events (in seconds)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))  # 5 min default

# Minimum gap between full agent runs (prevents back-to-back spam)
MIN_RUN_GAP_MINUTES = int(os.getenv("MIN_RUN_GAP_MINUTES", "30"))


class EventWatcher:
    def __init__(self, on_trigger: Callable[[list[str], str], Awaitable[None]]):
        """
        on_trigger: async callback that receives (topics, reason) and fires the agent.
        """
        self.on_trigger = on_trigger
        self.topic_engine = TopicEngine()
        self.last_run: datetime | None = None
        self.running = False
        self._manual_queue: list[str] = []

    # ──────────────────────────────────────────
    #  Main watch loop
    # ──────────────────────────────────────────

    async def start(self):
        """Start the event watch loop."""
        self.running = True
        logger.info(f"[EventWatcher] Started — polling every {POLL_INTERVAL}s")

        # Always run once immediately on start
        await self._fire_run(reason="initial_startup")

        while self.running:
            await asyncio.sleep(POLL_INTERVAL)
            await self._check_triggers()

    def stop(self):
        self.running = False
        logger.info("[EventWatcher] Stopped.")

    # ──────────────────────────────────────────
    #  Manual topic injection (Telegram / CLI)
    # ──────────────────────────────────────────

    def inject_topic(self, topic: str):
        """
        Inject a user-provided topic (from Telegram bot or CLI).
        This immediately queues a run with that topic — real user demand.
        """
        self._manual_queue.append(topic)
        logger.info(f"[EventWatcher] Manual topic queued: {topic}")

    # ──────────────────────────────────────────
    #  Trigger evaluation
    # ──────────────────────────────────────────

    async def _check_triggers(self):
        """Check all signal sources and fire if warranted."""

        # 1. Manual injection always takes priority
        if self._manual_queue:
            topics = self._manual_queue.copy()
            self._manual_queue.clear()
            await self._fire_run(topics=topics, reason="user_request")
            return

        # 2. Respect minimum gap between runs
        if not self._gap_ok():
            logger.debug("[EventWatcher] Too soon since last run, skipping.")
            return

        # 3. Check for price events
        events = await self.topic_engine.detect_price_events()
        if events:
            event_topics = [e["topic"] for e in events]
            reason = f"price_event:{','.join(e['token'] for e in events)}"
            await self._fire_run(topics=event_topics, reason=reason)
            return

        # 4. Check if a new hour has started (time-anchored, not spam)
        if self._new_hour():
            await self._fire_run(reason="hourly_trending_refresh")
            return

    def _gap_ok(self) -> bool:
        if self.last_run is None:
            return True
        gap = (datetime.utcnow() - self.last_run).total_seconds() / 60
        return gap >= MIN_RUN_GAP_MINUTES

    def _new_hour(self) -> bool:
        """True if we haven't run since the current hour started."""
        if self.last_run is None:
            return True
        current_hour_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        return self.last_run < current_hour_start

    # ──────────────────────────────────────────
    #  Fire a run
    # ──────────────────────────────────────────

    async def _fire_run(self, topics: list[str] | None = None, reason: str = "event"):
        """Build topics (if not injected) and invoke the agent callback."""
        if topics is None:
            topics = await self.topic_engine.build_run_topics()

        if not topics:
            logger.warning("[EventWatcher] No topics generated, skipping run.")
            return

        self.last_run = datetime.utcnow()
        logger.success(
            f"[EventWatcher] Firing agent | reason={reason} | topics={topics}"
        )
        await self.on_trigger(topics, reason)
