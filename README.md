# FastAPI Task Manager

A tiny task manager: the backend is [main.py](main.py) and the frontend is [index.html](index.html).

## Start the server

From this folder:

```bash
source venv/bin/activate        # activate the virtual environment
uvicorn main:app --reload       # start the server
```

Then open:

| URL | What it is |
| --- | --- |
| http://127.0.0.1:8000/ | The frontend (task list UI) |
| http://127.0.0.1:8000/docs | Interactive API docs (Swagger), where you can try every endpoint |
| http://127.0.0.1:8000/redoc | Alternative API docs |

`main:app` means "the `app` object in `main.py`". `--reload` restarts the server when you save a `.py` file.

Stop the server with `Ctrl+C`. Leave the virtual environment with `deactivate`.

### Useful options

```bash
uvicorn main:app --reload --port 8001      # use another port if 8000 is taken
uvicorn main:app --reload --host 0.0.0.0   # reachable from other devices on your network
```

## API endpoints

| Method | Path | Does |
| --- | --- | --- |
| GET | `/api/tasks/` | List all tasks |
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/{id}/` | Get one task |
| PATCH | `/api/tasks/{id}/` | Update a task |
| DELETE | `/api/tasks/{id}/` | Delete a task |

Examples with curl:

```bash
curl http://127.0.0.1:8000/api/tasks/

curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "2 liters"}'

curl -X PATCH http://127.0.0.1:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "completed": true}'

curl -X DELETE http://127.0.0.1:8000/api/tasks/1/
```

## Good to know

- **Tasks are kept in memory** (a Python list), so they are lost whenever the server restarts, including every reload after you save a `.py` file.
- Start the server from this folder. The `/` route opens `index.html` by a relative path.

## Setting up from scratch

If the `venv` folder is missing or broken:

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```
