import os

import django
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from app.auth.router import router as auth_router
from app.products.router import router as products_router
from config.wsgi import application as django_application


app = FastAPI(
    title="Desafio Técnico – Think Technology",
    description=(
        "API REST para autenticação de usuários e gerenciamento de produtos, "
        "com PostgreSQL, MongoDB e Django Admin."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_content(code: int, message: str, details=None) -> dict:
    error = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error["details"] = jsonable_encoder(details)
    return {"error": error}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_content(exc.status_code, str(exc.detail)),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content=error_content(
            422,
            "Dados da requisição inválidos.",
            exc.errors(),
        ),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error_content(
            500,
            "Erro interno do servidor.",
        ),
    )


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(products_router)

app.mount(
    "/static",
    StaticFiles(directory="/app/staticfiles"),
    name="static",
)

# O Django é utilizado exclusivamente para a interface administrativa.
app.mount(
    "/admin",
    WSGIMiddleware(django_application),
)
