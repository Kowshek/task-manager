from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import Task, User
from app.schemas import PaginatedTaskResponse, TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    task = Task(
        title=task_in.title,
        description=task_in.description,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get(
    "",
    response_model=PaginatedTaskResponse,
    summary="List all tasks (paginated, filterable)",
)
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all tasks belonging to the authenticated user.

    - **completed**: optional filter (`true` / `false`)
    - **page**: page number, starting from 1
    - **limit**: results per page (1–100)
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    total = query.count()
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return PaginatedTaskResponse(total=total, page=page, limit=limit, tasks=tasks)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task by ID",
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single task. Returns 404 if not found or not owned by the user."""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task (including marking complete)",
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update any field of a task. All fields are optional — only provided
    fields are changed. To mark complete, send `{"completed": true}`.
    """
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete a task. Returns 204 on success, 404 if not found."""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
