from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


def create_service(db: Session, workspace_id: int, service_data: ServiceCreate) -> Service:
    new_service = Service(
        workspace_id=workspace_id,
        name=service_data.name,
        description=service_data.description,
        duration_minutes=service_data.duration_minutes,
        capacity=service_data.capacity,
        price=service_data.price,
        currency=service_data.currency,
        status="active",
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


def get_services_by_workspace(db: Session, workspace_id: int) -> List[Service]:
    return (
        db.query(Service)
        .filter(Service.workspace_id == workspace_id)
        .order_by(Service.created_at.desc())
        .all()
    )


def get_service_by_id(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.id == service_id).first()


def update_service(db: Session, service: Service, service_data: ServiceUpdate) -> Service:
    update_data = service_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service