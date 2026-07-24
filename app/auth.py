from fastapi import HTTPException, Request, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.lower().strip()))
    if user and password_hash.verify(password, user.password_hash):
        return user
    return None


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    return db.get(User, user_id) if user_id else None


def require_user(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def require_admin(request: Request, db: Session) -> User:
    user = require_user(request, db)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user
