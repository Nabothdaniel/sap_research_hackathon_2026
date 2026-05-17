"""
main.py
Entry point for the autonomous SAP Research Agent.

Modes:
  python main.py                        # single run, fresh trending topics
  python main.py --watch                # event-driven mode (price moves + hourly trending)
  python main.py --watch --telegram     # event-driven + Telegram bot for user requests
  python main.py --topic "Sui vs Sol"   # single custom topic
"""

import asyncio
import argparse
import os
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel

load_dotenv()

from agent.orchestrator import ResearchAgentOrchestrator
from agent.event_watcher import EventWatcher
from services.topic_engine import TopicEngine
from utils.telegram_bot import TelegramBot

console = Console()


def print_banner():
    console.print(Panel(
        "[bold cyan]SAP Research Agent[/bold cyan]\n"
        "[dim]Event-driven · On-chain · Zero artificial loops[/dim]\n\n"
        "Every run is triggered by real market/trend signals.\n"
        "Stack: SAP + Ace Data Cloud (4 APIs) + x402 + Synapse RPC",
        title="🤖 ResearchBot-v1",
        border_style="cyan",
    ))


async def run_once(topic=None):
    """Run once — either for a custom topic or fresh trending topics."""
    agent = ResearchAgentOrchestrator()
    if topic:
        await agent.setup()
        await agent.run_once(topic)
    else:
        engine = TopicEngine()
        topics = await engine.build_run_topics()
        console.print(f"\n[bold]Fresh topics this run:[/bold] {', '.join(topics)}\n")
        await agent.run_all_topics(topics=topics, trigger_reason="cli_single_run")


async def run_watch_mode(use_telegram=False):
    """
    Event-driven mode:
    - Fires on price moves > 4%
    - Fires on fresh trending topics each new hour
    - Fires on user requests via Telegram (if enabled)
    No artificial loops — every run has a genuine trigger.
    """
    agent = ResearchAgentOrchestrator()

    async def on_trigger(topics, reason):
        await agent.run_all_topics(topics=topics, trigger_reason=reason)

    watcher = EventWatcher(on_trigger=on_trigger)

    if use_telegram:
        bot = TelegramBot(on_topic=watcher.inject_topic)
        if bot.enabled():
            console.print("[green]✓ Telegram bot enabled[/green]")
            await asyncio.gather(watcher.start(), bot.start())
        else:
            console.print("[yellow]⚠ TELEGRAM_BOT_TOKEN not set — running without Telegram.[/yellow]")
            await watcher.start()
    else:
        await watcher.start()


def main():
    parser = argparse.ArgumentParser(description="Autonomous SAP Research Agent")
    parser.add_argument("--watch", action="store_true",
        help="Event-driven mode: fires on price moves + hourly trending")
    parser.add_argument("--telegram", action="store_true",
        help="Enable Telegram bot for user-triggered research")
    parser.add_argument("--topic", type=str,
        help="Research a single specific topic and exit")
    args = parser.parse_args()

    print_banner()

    if args.watch:
        mode = "Event-driven watch" + (" + Telegram" if args.telegram else "")
        console.print(f"\n[bold green]Mode: {mode}[/bold green]")
        console.print("[dim]Triggers: price events · hourly trending · user requests[/dim]")
        console.print("[dim]Press Ctrl+C to stop.\n[/dim]")
        asyncio.run(run_watch_mode(use_telegram=args.telegram))
    else:
        console.print("\n[bold green]Mode: Single run[/bold green]")
        asyncio.run(run_once(topic=args.topic))


if __name__ == "__main__":
    main()
