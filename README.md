# 🤖 SAP Autonomous Research Agent
> **Competing in: Ace Data Cloud Usage Category**

An advanced, on-chain autonomous agent that monitors market signals, performs deep research via Ace Data Cloud, and settles micro-payments using x402 on the Solana network. 

Built for the **OOBE Protocol × Ace Data Cloud Hackathon**, this agent operates with **zero human intervention**, reacting purely to real-time market data and trending signals.

---

## 💎 Features & Capabilities

-   **Autonomous Discovery**: Uses the Synapse Agent Protocol (SAP) to discover and select the best tools for research tasks.
-   **Multi-API Pipeline**: Integrates **4 distinct Ace Data Cloud services** (Search, Summarization, Sentiment Analysis, and Entity Extraction).
-   **Event-Driven Execution**: Triggered by price moves (>4%), hourly trending shifts, or user requests.
-   **On-Chain Settlement**: Uses **x402 payment workflows** via the AceDataCloud facilitator and Synapse RPC.
-   **Premium Dashboard**: A real-time, glassmorphic dashboard visualizing the agent's autonomy integrity, tool load, and throughput.

---

## 🛠️ Tech Stack

-   **Core**: Python 3.12, FastAPI (API Bridge)
-   **Protocols**: Synapse Agent Protocol (SAP), x402 Micropayments
-   **APIs**: Ace Data Cloud (Search/NLP), Synapse RPC
-   **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (Real-time polling)

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
git clone https://github.com/your-username/sap-research-agent.git
cd sap-research-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Fill in the following:
- `ACE_API_KEY`: Your key from [platform.acedata.cloud](https://platform.acedata.cloud)
- `SAP_API_KEY`: Your key from [synapse.oobeprotocol.ai](https://synapse.oobeprotocol.ai)
- `SOLANA_PRIVATE_KEY`: Your base58 wallet private key.

### 3. Running the Agent
**Start the Dashboard Bridge:**
```bash
python api_bridge.py
```
**Start the Researcher (Watch Mode):**
```bash
python main.py --watch
```

---

## 🌐 Deployment (Render)

This project is configured for **Auto-Deployment on Render** via the `render.yaml` blueprint.
- **Web Service**: Hosts the API Bridge and Dashboard.
- **Cron Job**: Automates `main.py` hourly to ensure continuous on-chain activity.

---

## 🏆 Hackathon Qualification

This submission satisfies all requirements for the **Ace Data Cloud Usage Category**:
- [x] Registered on SAP Mainnet.
- [x] Fully automated workflow (Trigger → Discovery → Pay → Report).
- [x] Uses x402 with the AceDataCloud facilitator.
- [x] Integrated 4 distinct Ace Data APIs.
- [x] Every execution is logged on-chain via Synapse RPC.

---

## 📞 Contact & Demo
- X (Twitter): @dannywebtec
- **Synapse Explorer**: https://sap-research-hackathon-2026.onrender.com/dashboard/index.html
