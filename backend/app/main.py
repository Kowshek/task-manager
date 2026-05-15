import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    import app.database as db_module
    db_module.Base.metadata.create_all(bind=db_module.engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    description="Task Manager REST API built with FastAPI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
