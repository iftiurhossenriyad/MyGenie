from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, user_id: int, task_data: TaskCreate) -> Task:
    """Create a new task for a user."""
    new_task = Task(
        user_id=user_id,
        workspace_id=task_data.workspace_id,
        title=task_data.title,
        description=task_data.description,
        due_at=task_data.due_at,
        priority=task_data.priority,
        status="pending",
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_user_tasks(db: Session, user_id: int) -> List[Task]:
    """Get all tasks for a user."""
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .all()
    )


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task: Task, task_data: TaskUpdate) -> Task:
    """Update a task."""
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """Delete a task."""
    db.delete(task)
    db.commit()