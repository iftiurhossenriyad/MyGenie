from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.workspace import Workspace, WorkspaceMember
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceMemberCreate


def create_workspace(
    db: Session,
    owner_user_id: int,
    workspace_data: WorkspaceCreate,
) -> Workspace:
    """Create a new workspace and add the owner as a member."""
    new_workspace = Workspace(
        owner_user_id=owner_user_id,
        name=workspace_data.name,
        type=workspace_data.type,
        status="active",
    )
    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)

    owner_member = WorkspaceMember(
        workspace_id=new_workspace.id,
        user_id=owner_user_id,
        role="owner",
        status="active",
    )
    db.add(owner_member)
    db.commit()

    return new_workspace


def create_personal_workspace(db: Session, user: User) -> Workspace:
    """Create a personal workspace for a newly registered user."""
    personal_workspace = Workspace(
        owner_user_id=user.id,
        name=f"{user.name}'s Personal Workspace",
        type="personal",
        status="active",
    )
    db.add(personal_workspace)
    db.commit()
    db.refresh(personal_workspace)

    owner_member = WorkspaceMember(
        workspace_id=personal_workspace.id,
        user_id=user.id,
        role="owner",
        status="active",
    )
    db.add(owner_member)
    db.commit()

    return personal_workspace


def get_user_workspaces(db: Session, user_id: int) -> List[Workspace]:
    """Get all workspaces where the user is a member."""
    return (
        db.query(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user_id)
        .filter(WorkspaceMember.status == "active")
        .filter(Workspace.status == "active")
        .all()
    )


def get_workspace_by_id(db: Session, workspace_id: int) -> Optional[Workspace]:
    """Get a workspace by ID."""
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_member(
    db: Session,
    workspace_id: int,
    user_id: int,
) -> Optional[WorkspaceMember]:
    """Check if a user is a member of a workspace."""
    return (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id)
        .filter(WorkspaceMember.user_id == user_id)
        .filter(WorkspaceMember.status == "active")
        .first()
    )


def add_member(
    db: Session,
    workspace_id: int,
    member_data: WorkspaceMemberCreate,
) -> WorkspaceMember:
    """Add a new member to a workspace."""
    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=member_data.user_id,
        role=member_data.role,
        status="active",
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member