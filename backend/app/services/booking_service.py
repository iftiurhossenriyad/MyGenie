from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.customer import Customer
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate


def check_availability(
    db: Session,
    service_id: int,
    starts_at: datetime,
    ends_at: datetime,
    workspace_id: int,
    capacity: int,
    exclude_booking_id: Optional[int] = None,
) -> bool:
    """Check that overlapping active bookings do not exceed service capacity."""
    query = (
        db.query(Booking)
        .filter(Booking.service_id == service_id)
        .filter(Booking.workspace_id == workspace_id)
        .filter(Booking.status.in_(["requested", "confirmed"]))
        .filter(
            (Booking.starts_at < ends_at) & (Booking.ends_at > starts_at)
        )
    )
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)
    return query.count() < capacity


def validate_booking_interval(starts_at: datetime, ends_at: datetime) -> None:
    if (starts_at.utcoffset() is None) != (ends_at.utcoffset() is None):
        raise ValueError("Booking start and end times must use the same timezone format")
    if ends_at <= starts_at:
        raise ValueError("Booking end time must be after its start time")


def create_booking(
    db: Session, workspace_id: int, booking_data: BookingCreate
) -> Booking:
    """Create a booking after checking availability."""
    validate_booking_interval(booking_data.starts_at, booking_data.ends_at)

    service = (
        db.query(Service)
        .filter(
            Service.id == booking_data.service_id,
            Service.workspace_id == workspace_id,
        )
        .with_for_update()
        .first()
    )
    if not service:
        raise ValueError("Service not found in this workspace")
    if service.status != "active":
        raise ValueError("Service is not available for booking")

    if booking_data.customer_id is not None:
        customer = (
            db.query(Customer)
            .filter(
                Customer.id == booking_data.customer_id,
                Customer.workspace_id == workspace_id,
            )
            .first()
        )
        if not customer:
            raise ValueError("Customer not found in this workspace")

    available = check_availability(
        db,
        service.id,
        booking_data.starts_at,
        booking_data.ends_at,
        workspace_id,
        service.capacity,
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
    starts_at = update_data.get("starts_at", booking.starts_at)
    ends_at = update_data.get("ends_at", booking.ends_at)
    validate_booking_interval(starts_at, ends_at)

    is_active_booking = update_data.get("status", booking.status) in {
        "requested",
        "confirmed",
    }
    reschedules_booking = (
        "starts_at" in update_data or "ends_at" in update_data
    )
    if is_active_booking and reschedules_booking:
        service = (
            db.query(Service)
            .filter(
                Service.id == booking.service_id,
                Service.workspace_id == booking.workspace_id,
            )
            .with_for_update()
            .first()
        )
        if not service or service.status != "active":
            raise ValueError("Service is not available for booking")
        if not check_availability(
            db,
            service.id,
            starts_at,
            ends_at,
            booking.workspace_id,
            service.capacity,
            exclude_booking_id=booking.id,
        ):
            raise ValueError("Time slot is not available")

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