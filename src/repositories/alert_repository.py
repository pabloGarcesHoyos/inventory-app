from sqlalchemy.orm import Session

from src.models.alert import Alert


def create(db: Session, alert: Alert) -> Alert:
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_by_product(db: Session, product_id: int) -> list[Alert]:
    return (
        db.query(Alert)
        .filter(Alert.product_id == product_id)
        .order_by(Alert.created_at.asc(), Alert.id.asc())
        .all()
    )


def list_all(db: Session) -> list[Alert]:
    return db.query(Alert).order_by(Alert.created_at.asc(), Alert.id.asc()).all()
