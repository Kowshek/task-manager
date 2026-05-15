# ── Stage 1: base image ─────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Don't write .pyc files, don't buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies first (cached layer)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy frontend (served as static files by FastAPI)
COPY frontend/ ./frontend/

# Set PYTHONPATH so `app` package resolves correctly
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
