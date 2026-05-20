from sqlalchemy.orm import Session

from src.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, usuario_id: int) -> User | None:
    return db.query(User).filter(User.id == usuario_id).first()


def exists_by_email(db: Session, email: str) -> bool:
    return db.query(User.id).filter(User.email == email).first() is not None


def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
