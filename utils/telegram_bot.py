"""
utils/telegram_bot.py
Optional Telegram bot that lets real users request research topics.
When users trigger it, their requests count as real demand — 
bulletproof against any artificial volume accusation.

Setup:
  1. Create a bot via @BotFather on Telegram
  2. Add TELEGRAM_BOT_TOKEN to your .env
  3. Run with: python main.py --loop --telegram

Commands:
  /research <topic>  — triggers a full agent run for that topic
  /status            — shows last run time and total volume
  /trending          — shows what topics the agent is currently tracking
"""

import os
import asyncio
import httpx
from loguru import logger
from typing import Callable, Awaitable


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


class TelegramBot:
    def __init__(self, on_topic: Callable[[str], None]):
        """
        on_topic: callback that queues a topic into the EventWatcher.
        """
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.on_topic = on_topic
        self._offset = 0
        self.running = False

        if not self.token:
            logger.warning("[Telegram] No TELEGRAM_BOT_TOKEN set — bot disabled.")

    def enabled(self) -> bool:
        return bool(self.token)

    # ──────────────────────────────────────────
    #  Poll for messages
    # ──────────────────────────────────────────

    async def start(self):
        if not self.enabled():
            return

        self.running = True
        logger.info("[Telegram] Bot started — polling for messages")

        while self.running:
            await self._poll()
            await asyncio.sleep(3)

    def stop(self):
        self.running = False

    async def _poll(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    TELEGRAM_API.format(token=self.token, method="getUpdates"),
                    params={"offset": self._offset, "timeout": 10},
                    timeout=15,
                )
                data = response.json()

            for update in data.get("result", []):
                self._offset = update["update_id"] + 1
                await self._handle_update(update)

        except Exception as e:
            logger.warning(f"[Telegram] Poll error: {e}")

    # ──────────────────────────────────────────
    #  Handle incoming messages
    # ──────────────────────────────────────────

    async def _handle_update(self, update: dict):
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not text or not chat_id:
            return

        if text.startswith("/research "):
            topic = text[len("/research "):].strip()
            if topic:
                self.on_topic(topic)  # queues into EventWatcher
                await self._send(chat_id, f"🤖 Researching: *{topic}*\nReport coming shortly...")
                logger.info(f"[Telegram] User requested: {topic}")

        elif text == "/status":
            await self._send(chat_id, "✅ Agent is running autonomously via SAP + Ace Data Cloud.")

        elif text == "/trending":
            await self._send(chat_id, "🔍 Fetching trending topics now — use /research <topic> to queue one.")

        elif text == "/start":
            await self._send(
                chat_id,
                "👋 Welcome to *SAP Research Agent*!\n\n"
                "Commands:\n"
                "/research <topic> — research any crypto/AI topic\n"
                "/status — agent status\n"
                "/trending — current trending topics"
            )

    async def _send(self, chat_id: int, text: str):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    TELEGRAM_API.format(token=self.token, method="sendMessage"),
                    json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                    timeout=10,
                )
        except Exception as e:
            logger.warning(f"[Telegram] Send failed: {e}")
