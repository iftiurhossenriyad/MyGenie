from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    InventoryAdjustment,
)
from app.services import product_service, workspace_service

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


def verify_workspace_membership(db: Session, workspace_id: int, user_id: int):
    member = workspace_service.get_member(db, workspace_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return member


@router.post(
    "/workspaces/{workspace_id}/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    workspace_id: int,
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new product in a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return product_service.create_product(db, workspace_id, product_data)


@router.get(
    "/workspaces/{workspace_id}/products",
    response_model=List[ProductResponse],
)
def list_products(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all products in a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return product_service.get_products_by_workspace(db, workspace_id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a product by ID."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    verify_workspace_membership(db, product.workspace_id, current_user.id)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a product."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    verify_workspace_membership(db, product.workspace_id, current_user.id)
    return product_service.update_product(db, product, product_data)


@router.post("/{product_id}/inventory-adjustments", response_model=ProductResponse)
def adjust_inventory(
    product_id: int,
    adjustment: InventoryAdjustment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adjust product stock. Prevents negative stock."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    verify_workspace_membership(db, product.workspace_id, current_user.id)
    try:
        return product_service.adjust_stock(db, product, adjustment.quantity_change)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a product."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    verify_workspace_membership(db, product.workspace_id, current_user.id)
    product_service.delete_product(db, product)
    return None