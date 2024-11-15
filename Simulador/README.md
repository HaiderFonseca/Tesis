# API Courses Mock Server

Mock server implementation of the [Uniandes Course Offering API](https://ofertadecursos.uniandes.edu.co/api/courses). Used for testing purposes replicating the same API structure with historical data. Developed using FastAPI. Note that this is a _stateful_ server.

## Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
fastapi run
```

## Usage

There are 2 modes of operation:

- **On demand**: The server will tick each time a request is made, updating the data with the next available value in chronological order.
- **Real time**: The server will tick every `tick_interval` seconds, updating the data with the next available value in chronological order.

> **What is a tick?** A tick means going one step forward in time, updating the data with the next available value in chronological order. For example, if the current time is 2021-01-01 14:30 and the next available value is 2021-01-02 14:35, a tick will update the data with the values for 2021-01-02 14:35.

On startup, the server will start in _On demand_ mode with the default dataset. To switch to _Real time_ mode, use the `/restart` endpoint.

### Endpoints

#### Server Restart

Restartes the server data to the initial state with new configuration. The server will start in _On demand_ mode if the `tick_interval` is set to 0, otherwise it will start in _Real time_ mode.

**Example request:**

```bash
curl -X POST "http://localhost:8000/restart" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"dataset_name\":\"2024-20\",\"tick_interval\":300}"
```

**Example response:**

```json
{
  "message": "Restarted",
  "dataset_name": "2024-20",
  "tick_interval": 300,
  "change_on_demand": false
}
```

#### Server Info

Returns the current server configuration and status.

**Example request:**

```bash
curl -X GET "http://localhost:8000/info" -H  "accept: application/json"
```

**Example response:**

```json
{
  "last_restart": "2024-07-31T17:54:34",
  "simulated_time": "2024-07-30T14:30:00",
  "dataset_name": "2024-20",
  "tick_interval": 300,
  "change_on_demand": false,
  "is_done": false
}
```

#### Read Courses

Returns a list of courses with the number of available seats updated to reflect status at the current simulated time. The schema is the same as the original API.

**Example request:**

```bash
curl -X GET "http://localhost:8000/api/courses" -H  "accept: application/json"
```

**Example response:**

```json
[
  {
    "nrc": "39342",
    "class": "ADMI",
    "course": "1101",
    "section": "01",
    "credits": "3",
    "title": "FUNDAMENTOS DE ADMINISTRACION Y GERENCIA (PARA ADMINISTRADORES)",
    "enrolled": "84"
    /* ... */
  }
  /* ... */
]
```

## Docs

### Redoc

```
http://localhost:8000/redoc
```

### Swagger

```
http://localhost:8000/docs
```

---

Happy coding! 🚀
