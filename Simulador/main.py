import time
from fastapi import FastAPI
from pydantic import BaseModel, NonNegativeInt

from state import State
from utils import normalize_text

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
def read_courses(nameInput: str | None = None):
    """Get all courses (mock)"""
    courses = state.get_data()
    if not nameInput:
        return courses
    
    # Normalizar la entrada
    name_input_normalized = normalize_text(nameInput)

    # Filtrar los datos
    filtered_courses = []
    for course_data in courses:
        # Normalizar valores de búsqueda: NRC y class+course
        nrc_normalized = normalize_text(course_data["nrc"])
        course_code_normalized = normalize_text(course_data["class"] + course_data["course"])

        # Comparar con la entrada normalizada
        if name_input_normalized in nrc_normalized or name_input_normalized in course_code_normalized:
            filtered_courses.append(course_data)

    return filtered_courses