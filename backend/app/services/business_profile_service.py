from typing import Optional

from sqlalchemy.orm import Session

from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate


def get_profile_by_workspace(db: Session, workspace_id: int) -> Optional[BusinessProfile]:
    """Get business profile for a workspace."""
    return db.query(BusinessProfile).filter(BusinessProfile.workspace_id == workspace_id).first()


def create_profile(
    db: Session, workspace_id: int, profile_data: BusinessProfileCreate
) -> BusinessProfile:
    """Create a business profile for a workspace."""
    new_profile = BusinessProfile(
        workspace_id=workspace_id,
        business_name=profile_data.business_name,
        description=profile_data.description,
        address=profile_data.address,
        phone=profile_data.phone,
        email=profile_data.email,
        website=profile_data.website,
        opening_hours=profile_data.opening_hours,
        delivery_info=profile_data.delivery_info,
        policies=profile_data.policies,
        default_language=profile_data.default_language,
        supported_languages=profile_data.supported_languages,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


def update_profile(
    db: Session, profile: BusinessProfile, profile_data: BusinessProfileUpdate
) -> BusinessProfile:
    """Update a business profile."""
    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile