# api_bridge.py
import os
import json
import webbrowser
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from agent.orchestrator import ResearchAgentOrchestrator
from services.topic_engine import TopicEngine

app = FastAPI(title="SAP Research Agent Bridge")

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Autonomous Activation ---

@app.api_route("/trigger-run", methods=["GET", "POST"])
async def trigger_run(background_tasks: BackgroundTasks):
    """
    Endpoint for external cron services to trigger the autonomous research loop.
    Supports both GET (for manual testing) and POST (for automated services).
    """
    async def run_agent():
        topic_engine = TopicEngine()
        topics = await topic_engine.build_run_topics()
        orchestrator = ResearchAgentOrchestrator()
        await orchestrator.run_all_topics(topics=topics, trigger_reason="external_trigger")
    
    background_tasks.add_task(run_agent)
    return {"status": "Research run triggered in background"}

@app.get("/ping")
async def ping():
    """Simple health check endpoint to prevent server sleep."""
    return {"status": "alive", "message": "Stay awake!"}

@app.get("/")
async def root():
    """Redirect root to the dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard/index.html")

# Serve the dashboard folder at the root
# IMPORTANT: Routes should generally be defined before mounting static files
app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")

# --- State Model ---

class AgentState(BaseModel):
    agent_id: str = "SAP-NODE-EX-992"
    reputation_score: int = 713
    total_earning: float = 350.0
    today_reward: float = 50.0
    balance: float = 2250.0
    rank: str = "Alpha"
    referrals: int = 12
    cpu_load: int = 75
    storage_used: int = 600
    storage_total: int = 800
    volume_history: List[int] = [40, 60, 85, 50, 90, 30, 45]
    volume_transactions: List[dict] = [
        {"topic": "Solana MEV Trends", "bounty": 15.5, "status": "SETTLED", "time": "2m ago"},
        {"topic": "DePIN Network Growth", "bounty": 12.0, "status": "SETTLED", "time": "14m ago"},
        {"topic": "ETH L2 Scalability", "bounty": 22.4, "status": "SETTLED", "time": "28m ago"},
        {"topic": "AI Agent Protocols", "bounty": 18.2, "status": "PROCESSING", "time": "Just now"}
    ]
    connected: bool = True

# --- State Persistence ---

STATE_FILE = "output/agent_state.json"

def load_state() -> AgentState:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return AgentState(**json.load(f))
        except:
            pass
    return AgentState()

# --- Endpoints ---

@app.get("/state")
async def get_state():
    """Returns the current state of the SAP agent for the dashboard."""
    return load_state()

@app.get("/logs")
async def get_logs(limit: int = 10):
    """Returns recent research reports/logs."""
    logs = []
    log_dir = "output"
    if os.path.exists(log_dir):
        # Implementation to list recently created logs
        pass
    return logs

@app.on_event("startup")
async def startup_event():
    """Automatically start a continuous research loop when the server starts."""
    async def continuous_research_loop():
        orchestrator = ResearchAgentOrchestrator()
        topic_engine = TopicEngine()
        
        while True:
            try:
                # 1. Fetch fresh trending topics
                topics = await topic_engine.build_run_topics()
                
                # 2. Run the full orchestrator pipeline (Register -> Discover -> Execute -> Pay -> Report)
                await orchestrator.run_all_topics(topics=topics, trigger_reason="autonomous_background_loop")
                
                # 3. Wait for 30 minutes before the next autonomous cycle
                # This keeps the agent "alive" and generates steady, legitimate volume
                await asyncio.sleep(1800) 
            except Exception as e:
                print(f"Error in background research loop: {e}")
                await asyncio.sleep(60) # Wait a minute before retrying on error

    # Start the "forever loop" in the background
    asyncio.create_task(continuous_research_loop())

if __name__ == "__main__":
    import uvicorn
    # Auto-open the browser
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
