import os
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.products.repository import ProductRepository


def _login(client, username, password):
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _admin_token(client):
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123456")
    return _login(client, username, password)


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_register_login_and_me(test_user_data):
    with TestClient(app) as client:
        register = client.post("/auth/register", json=test_user_data)
        assert register.status_code == 201, register.text
        assert register.json()["username"] == test_user_data["username"]

        token = _login(client, test_user_data["username"], test_user_data["password"])
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert me.status_code == 200
        assert me.json()["username"] == test_user_data["username"]


def test_duplicate_user_returns_standard_error(test_user_data):
    with TestClient(app) as client:
        first = client.post("/auth/register", json=test_user_data)
        assert first.status_code == 201, first.text

        duplicate = client.post("/auth/register", json=test_user_data)
        body = duplicate.json()

        assert duplicate.status_code == 409
        assert body["error"]["code"] == 409
        assert body["error"]["message"] == "Usuário já cadastrado."


def test_invalid_login_returns_standard_error():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            data={"username": "usuario_inexistente", "password": "senha_invalida"},
        )
        body = response.json()

        assert response.status_code == 401
        assert body["error"]["code"] == 401
        assert body["error"]["message"] == "Usuário ou senha inválidos."


def test_product_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/products")
        body = response.json()

        assert response.status_code == 401
        assert body["error"]["code"] == 401


def test_regular_user_cannot_create_product(test_user_data):
    with TestClient(app) as client:
        client.post("/auth/register", json=test_user_data)
        token = _login(client, test_user_data["username"], test_user_data["password"])

        response = client.post(
            "/products",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Produto teste",
                "description": "Teste",
                "price": 10.50,
                "status": "Ativo",
            },
        )
        body = response.json()

        assert response.status_code == 403
        assert body["error"]["code"] == 403


def test_product_crud_with_admin():
    with TestClient(app) as client:
        token = _admin_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        name = f"Produto {uuid.uuid4().hex[:8]}"

        created = client.post(
            "/products",
            headers=headers,
            json={
                "name": name,
                "description": "Produto criado no teste",
                "price": 99.90,
                "status": "Ativo",
            },
        )
        assert created.status_code == 201, created.text
        product = created.json()
        product_id = product["id"]

        try:
            listed = client.get("/products", headers=headers)
            assert listed.status_code == 200
            assert any(item["id"] == product_id for item in listed.json())

            fetched = client.get(f"/products/{product_id}", headers=headers)
            assert fetched.status_code == 200

            updated = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": name,
                    "description": "Descrição alterada",
                    "price": 120.00,
                    "status": "Inativo",
                },
            )
            assert updated.status_code == 200
            assert updated.json()["status"] == "Inativo"

            deleted = client.delete(f"/products/{product_id}", headers=headers)
            assert deleted.status_code == 204

            missing = client.get(f"/products/{product_id}", headers=headers)
            assert missing.status_code == 404
            assert missing.json()["error"]["code"] == 404
        finally:
            cleanup = ProductRepository()
            try:
                cleanup.delete(product_id)
            finally:
                cleanup.close()


def test_invalid_product_price_returns_standard_error():
    with TestClient(app) as client:
        token = _admin_token(client)
        response = client.post(
            "/products",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Produto inválido",
                "description": "",
                "price": 0,
                "status": "Ativo",
            },
        )
        body = response.json()

        assert response.status_code == 422
        assert body["error"]["code"] == 422
        assert body["error"]["message"] == "Dados da requisição inválidos."
        assert body["error"]["details"][0]["type"] == "greater_than"


def test_invalid_product_status_returns_standard_error():
    with TestClient(app) as client:
        token = _admin_token(client)
        response = client.post(
            "/products",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Produto inválido",
                "description": "",
                "price": 10,
                "status": "Qualquer",
            },
        )
        body = response.json()

        assert response.status_code == 422
        assert body["error"]["code"] == 422
        assert body["error"]["message"] == "Dados da requisição inválidos."


def test_empty_product_name_returns_standard_error():
    with TestClient(app) as client:
        token = _admin_token(client)
        response = client.post(
            "/products",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "   ",
                "description": "",
                "price": 10,
                "status": "Ativo",
            },
        )
        body = response.json()

        assert response.status_code == 422
        assert body["error"]["code"] == 422
