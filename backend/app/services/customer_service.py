from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(db: Session, workspace_id: int, customer_data: CustomerCreate) -> Customer:
    new_customer = Customer(
        workspace_id=workspace_id,
        display_name=customer_data.display_name,
        phone=customer_data.phone,
        email=customer_data.email,
        address=customer_data.address,
        consent_status=customer_data.consent_status,
        notes=customer_data.notes,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def get_customers_by_workspace(db: Session, workspace_id: int) -> List[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.workspace_id == workspace_id)
        .order_by(Customer.created_at.desc())
        .all()
    )


def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def update_customer(db: Session, customer: Customer, customer_data: CustomerUpdate) -> Customer:
    update_data = customer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer