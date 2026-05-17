"""
utils/report_generator.py
Compiles pipeline results into a structured research report.
Saved to /output for demo purposes.
"""

import os
import json
import aiofiles
from datetime import datetime
from loguru import logger


class ReportGenerator:

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def generate(self, topic: str, pipeline_data: dict, payment_summary: dict) -> str:
        """Generate a full research report from pipeline results."""

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/report_{topic.replace(' ', '_')}_{timestamp}.md"

        search = pipeline_data.get("search", {})
        summary = pipeline_data.get("summary", {})
        sentiment = pipeline_data.get("sentiment", {})
        entities = pipeline_data.get("entities", {})

        sentiment_emoji = {
            "positive": "🟢",
            "negative": "🔴",
            "neutral": "🟡",
        }.get(sentiment.get("sentiment", "neutral"), "🟡")

        sources = "\n".join([
            f"- [{r.get('title', 'Source')}]({r.get('url', '#')})"
            for r in search.get("results", [])[:5]
        ])

        entity_list = "\n".join([
            f"- **{e.get('text')}** ({e.get('type')})"
            for e in entities.get("entities", [])[:10]
        ])

        report = f"""# Research Report: {topic}
**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
**Agent:** ResearchBot-v1 (Autonomous · SAP Mainnet)

---

## Summary
{summary.get("summary", "No summary available.")}

---

## Sentiment Analysis
{sentiment_emoji} **{sentiment.get("sentiment", "neutral").title()}**
- Score: `{sentiment.get("score", 0)}`
- Confidence: `{sentiment.get("confidence", 0)}`

---

## Key Entities Detected
{entity_list or "None extracted."}

---

## Sources ({search.get("total", 0)} found)
{sources or "No sources found."}

---

## Payment Settlement
- Total payments this run: **{payment_summary.get("total_payments", 0)}**
- Total volume: **${payment_summary.get("total_volume_usdc", 0):.4f} USDC**
- Protocol: x402 via AceDataCloud Facilitator + Synapse RPC

---
*Autonomous agent — no human input required. Powered by SAP + Ace Data Cloud.*
"""

        async with aiofiles.open(filename, "w") as f:
            await f.write(report)

        logger.success(f"Report saved: {filename}")
        return filename

    async def save_json_log(self, run_data: dict) -> str:
        """Save raw JSON log of a full agent run for transparency/demo."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/run_log_{timestamp}.json"

        async with aiofiles.open(filename, "w") as f:
            await f.write(json.dumps(run_data, indent=2, default=str))

        logger.info(f"Run log saved: {filename}")
        return filename
