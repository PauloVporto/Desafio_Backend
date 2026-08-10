import os

import django
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.security import decode_token
from app.database import get_db

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    username = decode_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.execute(
        text(
            """
            SELECT id, username, email, password, is_active, is_staff, is_superuser
            FROM users
            WHERE username = :username
            """
        ),
        {"username": username},
    ).mappings().first()

    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(user=Depends(get_current_user)):
    if not (user["is_staff"] or user["is_superuser"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administrador necessária.",
        )
    return user
