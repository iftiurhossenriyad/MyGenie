from typing import List, Optional
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderUpdate


def generate_order_number() -> str:
    """Generate a unique human-readable order number."""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


def create_order(db: Session, workspace_id: int, order_data: OrderCreate) -> Order:
    """Create an order with server-side calculated totals."""
    if order_data.customer_id is not None:
        customer = (
            db.query(Customer)
            .filter(
                Customer.id == order_data.customer_id,
                Customer.workspace_id == workspace_id,
            )
            .first()
        )
        if not customer:
            raise ValueError("Customer not found in this workspace")

    subtotal = Decimal("0")
    order_items = []
    for item_data in order_data.items:
        product = None
        if item_data.product_id is not None:
            product = (
                db.query(Product)
                .filter(
                    Product.id == item_data.product_id,
                    Product.workspace_id == workspace_id,
                    Product.status == "active",
                    Product.is_available.is_(True),
                )
                .first()
            )
            if not product:
                raise ValueError("Product not found or unavailable in this workspace")
            if product.currency != order_data.currency:
                raise ValueError("Order and product currencies must match")

        unit_price = product.price if product else item_data.unit_price_snapshot
        product_name = product.name if product else item_data.product_name_snapshot
        line_total = unit_price * item_data.quantity
        subtotal += line_total
        order_items.append(
            OrderItem(
                product_id=product.id if product else None,
                product_name_snapshot=product_name,
                unit_price_snapshot=unit_price,
                quantity=item_data.quantity,
                line_total=line_total,
            )
        )

    total = subtotal + order_data.delivery_fee

    new_order = Order(
        workspace_id=workspace_id,
        customer_id=order_data.customer_id,
        order_number=generate_order_number(),
        status="requested",
        subtotal=subtotal,
        delivery_fee=order_data.delivery_fee,
        total=total,
        currency=order_data.currency,
        delivery_details=order_data.delivery_details,
        customer_notes=order_data.customer_notes,
        items=order_items,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def get_orders_by_workspace(db: Session, workspace_id: int) -> List[Order]:
    return (
        db.query(Order)
        .filter(Order.workspace_id == workspace_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def update_order(db: Session, order: Order, order_data: OrderUpdate) -> Order:
    """Update order details. Recalculates total if delivery_fee changes."""
    update_data = order_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)

    if "delivery_fee" in update_data:
        order.total = order.subtotal + order.delivery_fee

    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order: Order, status_data: OrderStatusUpdate) -> Order:
    """Update order status."""
    order.status = status_data.status
    db.commit()
    db.refresh(order)
    return order