from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


def create_appointment(
    db: Session,
    user_id: int,
    appointment_data: AppointmentCreate,
) -> Appointment:
    """Create a new appointment for a user."""
    new_appointment = Appointment(
        user_id=user_id,
        workspace_id=appointment_data.workspace_id,
        title=appointment_data.title,
        notes=appointment_data.notes,
        starts_at=appointment_data.starts_at,
        ends_at=appointment_data.ends_at,
        status="scheduled",
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


def get_user_appointments(db: Session, user_id: int) -> List[Appointment]:
    """Get all appointments for a user."""
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == user_id)
        .order_by(Appointment.starts_at.asc())
        .all()
    )


def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[Appointment]:
    """Get an appointment by ID."""
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def update_appointment(
    db: Session,
    appointment: Appointment,
    appointment_data: AppointmentUpdate,
) -> Appointment:
    """Update an appointment."""
    update_data = appointment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db: Session, appointment: Appointment) -> None:
    """Delete an appointment."""
    db.delete(appointment)
    db.commit()