from datetime import datetime

from sqlalchemy.orm import Session

from src.models.movement import Movement


def create(db: Session, movement: Movement) -> Movement:
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def get_by_id(db: Session, movement_id: int) -> Movement | None:
    return db.query(Movement).filter(Movement.id == movement_id).first()


def list_by_product(
    db: Session,
    product_id: int,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> list[Movement]:
    query = db.query(Movement).filter(Movement.product_id == product_id)
    if fecha_inicio is not None:
        query = query.filter(Movement.fecha >= fecha_inicio)
    if fecha_fin is not None:
        query = query.filter(Movement.fecha <= fecha_fin)
    return query.order_by(Movement.fecha.asc(), Movement.id.asc()).all()


def list_all(db: Session) -> list[Movement]:
    return db.query(Movement).order_by(Movement.fecha.asc(), Movement.id.asc()).all()
