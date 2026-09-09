from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_api_key, PaginationParams
from app.models import Task, TaskCreate, TaskPublic, TaskUpdate, TaskStatus, User
from app.utils import log_completion_report

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[str, Depends(require_api_key)],  # Protected
):
    # Validate user exists before assigning task
    user = session.get(User, task.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {task.user_id} does not exist.",
        )

    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskPublic])
def read_tasks(
    session: Annotated[Session, Depends(get_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    statement = select(Task).offset(pagination.offset).limit(pagination.limit)
    return session.exec(statement).all()


@router.get("/{task_id}", response_model=TaskPublic)
def read_task(task_id: int, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[str, Depends(require_api_key)],  # Protected
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    previous_status = db_task.status

    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # This triggers background task if the task was newly marked as DONE
    if previous_status != TaskStatus.DONE and db_task.status == TaskStatus.DONE:
        background_tasks.add_task(
            log_completion_report,
            task_id=db_task.id,
            task_title=db_task.title,
            user_id=db_task.user_id,
        )

    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[str, Depends(require_api_key)],  # Protected
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(db_task)
    session.commit()
    return None