import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api_bridge import app

client = TestClient(app)

def test_ping():
    """Test the healthy check endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "message": "Stay awake!"}

def test_state_endpoint():
    """Test that the dashboard state endpoint returns expected fields."""
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "reputation_score" in data
    assert "total_earning" in data
