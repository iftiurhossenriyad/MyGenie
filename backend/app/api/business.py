from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.business_profile import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.schemas.faq import FAQCreate, FAQUpdate, FAQResponse
from app.services import (
    business_profile_service,
    faq_service,
    workspace_service,
)

router = APIRouter(prefix="/api/v1/business", tags=["Business"])


def verify_workspace_membership(db: Session, workspace_id: int, user_id: int):
    """Verify user is a member of the workspace."""
    member = workspace_service.get_member(db, workspace_id, user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return member


# ============ Business Profile ============

@router.post(
    "/workspaces/{workspace_id}/profile",
    response_model=BusinessProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_profile(
    workspace_id: int,
    profile_data: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a business profile for a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    existing = business_profile_service.get_profile_by_workspace(db, workspace_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business profile already exists for this workspace",
        )
    return business_profile_service.create_profile(db, workspace_id, profile_data)


@router.get(
    "/workspaces/{workspace_id}/profile",
    response_model=BusinessProfileResponse,
)
def get_business_profile(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the business profile for a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    profile = business_profile_service.get_profile_by_workspace(db, workspace_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )
    return profile


@router.patch(
    "/workspaces/{workspace_id}/profile",
    response_model=BusinessProfileResponse,
)
def update_business_profile(
    workspace_id: int,
    profile_data: BusinessProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a business profile."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    profile = business_profile_service.get_profile_by_workspace(db, workspace_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found",
        )
    return business_profile_service.update_profile(db, profile, profile_data)


# ============ FAQ ============

@router.post(
    "/workspaces/{workspace_id}/faqs",
    response_model=FAQResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_faq(
    workspace_id: int,
    faq_data: FAQCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new FAQ for a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return faq_service.create_faq(db, workspace_id, faq_data)


@router.get(
    "/workspaces/{workspace_id}/faqs",
    response_model=List[FAQResponse],
)
def list_faqs(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all FAQs for a workspace."""
    verify_workspace_membership(db, workspace_id, current_user.id)
    return faq_service.get_faqs_by_workspace(db, workspace_id)


@router.get("/faqs/{faq_id}", response_model=FAQResponse)
def get_faq(
    faq_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a FAQ by ID."""
    faq = faq_service.get_faq_by_id(db, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    verify_workspace_membership(db, faq.workspace_id, current_user.id)
    return faq


@router.patch("/faqs/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    faq_data: FAQUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a FAQ."""
    faq = faq_service.get_faq_by_id(db, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    verify_workspace_membership(db, faq.workspace_id, current_user.id)
    return faq_service.update_faq(db, faq, faq_data)


@router.delete("/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(
    faq_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a FAQ."""
    faq = faq_service.get_faq_by_id(db, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )
    verify_workspace_membership(db, faq.workspace_id, current_user.id)
    faq_service.delete_faq(db, faq)
    return None