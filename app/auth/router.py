from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from django.contrib.auth.hashers import make_password

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.security import create_access_token, verify_password
from app.database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


def _public_user(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"] or "",
        "is_active": row["is_active"],
        "is_staff": row["is_staff"],
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome de usuário não pode ser vazio.",
        )

    try:
        row = db.execute(
            text(
                """
                INSERT INTO users
                    (
                        username,
                        email,
                        password,
                        is_active,
                        is_staff,
                        is_superuser,
                        date_joined
                    )
                VALUES
                    (
                        :username,
                        :email,
                        :password,
                        TRUE,
                        FALSE,
                        FALSE,
                        NOW()
                    )
                RETURNING
                    id,
                    username,
                    email,
                    is_active,
                    is_staff
                """
            ),
            {
                "username": username,
                "email": str(data.email) if data.email else "",
                "password": make_password(data.password),
            },
        ).mappings().first()

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuário já cadastrado.",
        )

    return _public_user(row)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = form_data.username.strip()
    password = form_data.password

    row = db.execute(
        text(
            """
            SELECT
                username,
                password,
                is_active
            FROM users
            WHERE username = :username
            """
        ),
        {
            "username": username,
        },
    ).mappings().first()

    if (
        not row
        or not row["is_active"]
        or not verify_password(password, row["password"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    token = create_access_token(row["username"])

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user=Depends(get_current_user),
):
    return _public_user(user)