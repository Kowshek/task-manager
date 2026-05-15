# Task Manager — FastAPI + Vanilla JS

A full-stack Task Manager web application built with **FastAPI** (backend) and **plain HTML/CSS/JS** (frontend). Built as part of the Weboin Tech Python Developer Internship assignment.

**Live Demo:** `https://your-app.onrender.com` ← replace after deployment  
**API Docs:** `https://your-app.onrender.com/docs`

---

## Features

- JWT-based authentication (register / login / logout)
- Full task CRUD (create, view, update, delete)
- Mark tasks as completed
- Pagination and filtering by completion status
- User isolation — users only see their own tasks
- Interactive API docs at `/docs` (Swagger UI)
- Responsive single-page frontend

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | FastAPI, SQLAlchemy, Pydantic     |
| Auth      | JWT (python-jose), bcrypt (passlib) |
| Database  | SQLite (local) / configurable     |
| Frontend  | HTML5, CSS3, Vanilla JavaScript   |
| Testing   | pytest, FastAPI TestClient        |
| Deploy    | Render (Docker)                   |

---

## Project Structure

```
task-manager/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        # Settings (pydantic-settings)
│   │   │   ├── security.py      # bcrypt + JWT helpers
│   │   │   └── dependencies.py  # get_current_user dependency
│   │   ├── routers/
│   │   │   ├── auth.py          # /register, /login
│   │   │   └── tasks.py         # /tasks CRUD
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── models.py            # User + Task ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── main.py              # FastAPI app, routers, static mount
│   ├── tests/
│   │   ├── conftest.py          # Fixtures (test DB, client, auth)
│   │   ├── test_auth.py         # Auth endpoint tests
│   │   └── test_tasks.py        # Task CRUD tests
│   └── requirements.txt
├── frontend/
│   └── index.html               # Single-page app (no framework)
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/task-manager.git
cd task-manager

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Set up environment variables
cp ../.env.example .env
# Edit .env — at minimum, change SECRET_KEY

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` — the frontend loads automatically.  
API docs: `http://localhost:8000/docs`

---

## Environment Variables

| Variable                     | Default                        | Description                          |
|------------------------------|--------------------------------|--------------------------------------|
| `SECRET_KEY`                 | `changeme-...`                 | JWT signing key — **change in prod** |
| `ALGORITHM`                  | `HS256`                        | JWT algorithm                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `1440` (24h)                   | Token lifetime                       |
| `DATABASE_URL`               | `sqlite:///./task_manager.db`  | SQLAlchemy DB connection string      |
| `DEBUG`                      | `False`                        | Enable debug mode                    |

> **Never commit `.env`** — use `.env.example` as the template.  
> Generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## API Endpoints

### Authentication

| Method | Endpoint    | Description              | Auth Required |
|--------|-------------|--------------------------|---------------|
| POST   | `/register` | Register a new user      | No            |
| POST   | `/login`    | Login, receive JWT token | No            |

### Tasks

| Method | Endpoint        | Description                            | Auth Required |
|--------|-----------------|----------------------------------------|---------------|
| POST   | `/tasks`        | Create a task                          | Yes           |
| GET    | `/tasks`        | List tasks (paginated + filterable)    | Yes           |
| GET    | `/tasks/{id}`   | Get a specific task                    | Yes           |
| PUT    | `/tasks/{id}`   | Update task (title, desc, completed)   | Yes           |
| DELETE | `/tasks/{id}`   | Delete a task                          | Yes           |

#### Query params for `GET /tasks`
- `?completed=true` — filter completed tasks
- `?completed=false` — filter pending tasks
- `?page=1&limit=10` — pagination (default: page 1, 10 per page)

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Expected output: all tests pass (auth + task CRUD coverage).

---

## Docker

```bash
# Build
docker build -t task-manager .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  task-manager
```

---

## Deployment (Render)

1. Push code to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Environment:** Docker
   - **Dockerfile path:** `./Dockerfile`
5. Add environment variables in Render dashboard:
   - `SECRET_KEY` → generate a strong random key
   - `DATABASE_URL` → `sqlite:///./task_manager.db` (or PostgreSQL URL)
6. Deploy — Render builds and hosts the app
7. Your live URL + `/docs` will be accessible publicly

---

## How to Use (Quick Flow)

1. Open the live URL
2. Click **Register** → create your account
3. **Login** with your credentials
4. **Add tasks** using the form
5. Click the **checkbox** to mark a task complete
6. Use **filter buttons** to view All / Pending / Completed
7. Click **Delete** to remove a task
8. Click **Logout** when done
