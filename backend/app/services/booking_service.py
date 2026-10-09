from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate


def check_availability(
    db: Session, service_id: int, starts_at, ends_at, workspace_id: int
) -> bool:
    """Check if a time slot is available for a service."""
    conflicting = (
        db.query(Booking)
        .filter(Booking.service_id == service_id)
        .filter(Booking.workspace_id == workspace_id)
        .filter(Booking.status.in_(["requested", "confirmed"]))
        .filter(
            (Booking.starts_at < ends_at) & (Booking.ends_at > starts_at)
        )
        .first()
    )
    return conflicting is None


def create_booking(
    db: Session, workspace_id: int, booking_data: BookingCreate
) -> Booking:
    """Create a booking after checking availability."""
    service = db.query(Service).filter(Service.id == booking_data.service_id).first()
    if not service:
        raise ValueError("Service not found")

    available = check_availability(
        db, booking_data.service_id, booking_data.starts_at, booking_data.ends_at, workspace_id
    )
    if not available:
        raise ValueError("Time slot is not available")

    new_booking = Booking(
        workspace_id=workspace_id,
        customer_id=booking_data.customer_id,
        service_id=booking_data.service_id,
        starts_at=booking_data.starts_at,
        ends_at=booking_data.ends_at,
        status="requested",
        notes=booking_data.notes,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


def get_bookings_by_workspace(db: Session, workspace_id: int) -> List[Booking]:
    return (
        db.query(Booking)
        .filter(Booking.workspace_id == workspace_id)
        .order_by(Booking.starts_at.asc())
        .all()
    )


def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.id == booking_id).first()


def update_booking(db: Session, booking: Booking, booking_data: BookingUpdate) -> Booking:
    update_data = booking_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(booking, key, value)
    db.commit()
    db.refresh(booking)
    return booking


def update_booking_status(
    db: Session, booking: Booking, status_data: BookingStatusUpdate
) -> Booking:
    booking.status = status_data.status
    db.commit()
    db.refresh(booking)
    return booking