from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingStatusUpdate,
    BookingResponse,
)
from app.services import (
    service_service,
    booking_service,
    workspace_service,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


def verify_workspace_membership(db: Session, workspace_id: int, user_id: int):
    member = workspace_service.get_member(db, workspace_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return member


# ============ Services ============

@router.post(
    "/workspaces/{workspace_id}/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    workspace_id: int,
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_workspace_membership(db, workspace_id, current_user.id)
    return service_service.create_service(db, workspace_id, service_data)


@router.get(
    "/workspaces/{workspace_id}/services",
    response_model=List[ServiceResponse],
)
def list_services(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_workspace_membership(db, workspace_id, current_user.id)
    return service_service.get_services_by_workspace(db, workspace_id)


@router.patch("/services/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = service_service.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    verify_workspace_membership(db, service.workspace_id, current_user.id)
    return service_service.update_service(db, service, service_data)


# ============ Bookings ============

@router.post(
    "/workspaces/{workspace_id}/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    workspace_id: int,
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a booking. Backend checks availability before confirming."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    try:
        return booking_service.create_booking(db, workspace_id, booking_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/workspaces/{workspace_id}/bookings",
    response_model=List[BookingResponse],
)
def list_bookings(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_workspace_membership(db, workspace_id, current_user.id)
    return booking_service.get_bookings_by_workspace(db, workspace_id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = booking_service.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    verify_workspace_membership(db, booking.workspace_id, current_user.id)
    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = booking_service.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    verify_workspace_membership(db, booking.workspace_id, current_user.id)
    return booking_service.update_booking(db, booking, booking_data)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a booking."""
    booking = booking_service.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    verify_workspace_membership(db, booking.workspace_id, current_user.id)
    status_data = BookingStatusUpdate(status="cancelled")
    return booking_service.update_booking_status(db, booking, status_data)