import sys
import os

# --- AGGRESSIVE DIAGNOSTICS ---
print("\n--- CI DEBUG INFO ---")
print(f"Current Working Dir: {os.getcwd()}")
print(f"File Path: {__file__}")
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"Calculated Project Root: {project_root}")
print(f"Root Contents: {os.listdir(project_root) if os.path.exists(project_root) else 'NOT FOUND'}")
sys.path.insert(0, project_root)
print(f"Final sys.path: {sys.path[:3]}")
print("----------------------\n")

from fastapi.testclient import TestClient
try:
    from api_bridge import app
except ImportError as e:
    print(f"Failed to import api_bridge: {e}")
    # Attempt secondary fallback
    sys.path.append(os.getcwd())
    from api_bridge import app

client = TestClient(app)

def test_ping():
    """Test the health check endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_state_endpoint():
    """Test that the dashboard state endpoint returns expected fields."""
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "reputation_score" in data
