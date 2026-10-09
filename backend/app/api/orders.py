from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderStatusUpdate,
    OrderResponse,
)
from app.services import order_service, workspace_service

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


def verify_workspace_membership(db: Session, workspace_id: int, user_id: int):
    member = workspace_service.get_member(db, workspace_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return member


@router.post(
    "/workspaces/{workspace_id}/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    workspace_id: int,
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create an order with server-calculated totals."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return order_service.create_order(db, workspace_id, order_data)


@router.get(
    "/workspaces/{workspace_id}/orders",
    response_model=List[OrderResponse],
)
def list_orders(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all orders in a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return order_service.get_orders_by_workspace(db, workspace_id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get an order by ID."""
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    verify_workspace_membership(db, order.workspace_id, current_user.id)
    return order


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an order's details."""
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    verify_workspace_membership(db, order.workspace_id, current_user.id)
    return order_service.update_order(db, order, order_data)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an order's status."""
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    verify_workspace_membership(db, order.workspace_id, current_user.id)
    return order_service.update_order_status(db, order, status_data)