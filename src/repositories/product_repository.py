from sqlalchemy.orm import Session

from src.models.product import Product


def get_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_by_sku(db: Session, sku: str) -> Product | None:
    return db.query(Product).filter(Product.sku == sku).first()


def exists_by_sku(db: Session, sku: str) -> bool:
    return db.query(Product.id).filter(Product.sku == sku).first() is not None


def create(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_all(db: Session) -> list[Product]:
    return db.query(Product).order_by(Product.id).all()
