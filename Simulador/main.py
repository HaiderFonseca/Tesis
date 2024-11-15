import time
from fastapi import FastAPI
from pydantic import BaseModel, NonNegativeInt

from state import State

app = FastAPI()
state = State()

class RestartParams(BaseModel):
    """Parameters for restarting the server"""
    dataset_name: str
    tick_interval: NonNegativeInt


@app.get("/info")
def server_info():
    """Get server information"""
    return {
        "last_restart": f"{time.time() - state.last_restart:.0f} seconds ago",
        "dataset_name": state.dataset_name,
        "tick_interval": state.tick_interval,
        "change_on_demand": state.change_on_demand,
        "is_done": state.is_done(),
        "dataset_metadata": state.get_dataset_metadata(),
    }

@app.post("/restart")
def server_restart(params: RestartParams):
    """Restart the server"""
    state.restart(params.dataset_name, params.tick_interval)
    return {
        "message": "Restarted",
        "dataset_name": state.dataset_name,
        "tick_interval": state.tick_interval,
        "change_on_demand": state.change_on_demand,
    }

@app.get("/api/courses")
def read_courses():
    """Get all courses (mock)"""
    return state.get_data()
