from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, workspace_id: int, product_data: ProductCreate) -> Product:
    new_product = Product(
        workspace_id=workspace_id,
        name=product_data.name,
        description=product_data.description,
        name_bn=product_data.name_bn,
        name_en=product_data.name_en,
        description_bn=product_data.description_bn,
        description_en=product_data.description_en,
        sku=product_data.sku,
        price=product_data.price,
        currency=product_data.currency,
        stock_quantity=product_data.stock_quantity,
        is_available=product_data.is_available,
        image_url=product_data.image_url,
        language=product_data.language,
        status="active",
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_products_by_workspace(db: Session, workspace_id: int) -> List[Product]:
    return (
        db.query(Product)
        .filter(Product.workspace_id == workspace_id)
        .order_by(Product.created_at.desc())
        .all()
    )


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product: Product, product_data: ProductUpdate) -> Product:
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def adjust_stock(db: Session, product: Product, quantity_change: int) -> Product:
    """Adjust stock quantity. Prevents negative stock."""
    new_quantity = product.stock_quantity + quantity_change
    if new_quantity < 0:
        raise ValueError("Stock quantity cannot be negative")
    product.stock_quantity = new_quantity
    product.is_available = new_quantity > 0 and product.status == "active"
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()