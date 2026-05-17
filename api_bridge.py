# api_bridge.py
import os
import json
import webbrowser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SAP Research Agent Bridge")

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the dashboard folder at the root
app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")

@app.get("/")
async def root():
    """Redirect root to the dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard/index.html")

# --- State Model ---

class AgentState(BaseModel):
    agent_id: str = "research-bot-dev"
    reputation_score: int = 713
    total_earning: float = 350.0
    today_reward: float = 50.0
    ip_address: str = "127.0.0.1"
    connected: bool = True
    cpu_load: int = 75
    storage_used: int = 600
    storage_total: int = 800

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

if __name__ == "__main__":
    import uvicorn
    # Auto-open the browser
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
