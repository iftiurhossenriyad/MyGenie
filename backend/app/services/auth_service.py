from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Find a user by phone."""
    if not phone:
        return None
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with a hashed password and a personal workspace."""
    from app.services import workspace_service

    hashed_pw = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_pw,
        status="active",
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    workspace_service.create_personal_workspace(db, new_user)

    return new_user


def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, login_data.email)
    if not user:
        return None
    if not verify_password(login_data.password, user.password_hash):
        return None
    return user