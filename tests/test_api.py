import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core import settings
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


def _admin_headers(client):
    token = _admin_token(client)

    return {
        "Authorization": f"Bearer {token}"
    }


def _register_user(client, test_user_data):
    response = client.post(
        "/auth/register",
        json=test_user_data,
    )

    assert response.status_code == 201, response.text

    return response


def _user_headers(client, test_user_data):
    _register_user(client, test_user_data)

    token = _login(
        client,
        test_user_data["username"],
        test_user_data["password"],
    )

    return {
        "Authorization": f"Bearer {token}"
    }


def _create_product(client, headers, **changes):
    data = {
        "name": f"Produto teste {uuid.uuid4().hex[:8]}",
        "description": "Produto criado durante os testes",
        "price": 99.90,
        "status": "Ativo",
    }

    data.update(changes)

    response = client.post(
        "/products",
        headers=headers,
        json=data,
    )

    assert response.status_code == 201, response.text

    return response.json()


def _cleanup_product(product_id):
    repo = ProductRepository()

    try:
        repo.delete(product_id)
    finally:
        repo.close()


def test_verificar_saude_api():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_verificar_saude_api_multiple_requests():
    with TestClient(app) as client:
        for _ in range(3):
            response = client.get("/health")

            assert response.status_code == 200
            assert response.json()["status"] == "ok"


def test_cadastrar_usuario(test_user_data):
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json=test_user_data,
        )

        assert response.status_code == 201

        body = response.json()

        assert body["username"] == test_user_data["username"]
        assert body["email"] == test_user_data["email"]
        assert body["is_active"] is True
        assert body["is_staff"] is False
        assert "id" in body
        assert "password" not in body


def test_cadastrar_logar_e_consultar_usuario(test_user_data):
    with TestClient(app) as client:
        register = client.post(
            "/auth/register",
            json=test_user_data,
        )

        assert register.status_code == 201, register.text

        token = _login(
            client,
            test_user_data["username"],
            test_user_data["password"],
        )

        me = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        assert me.status_code == 200

        body = me.json()

        assert body["username"] == test_user_data["username"]
        assert body["email"] == test_user_data["email"]
        assert body["is_active"] is True
        assert body["is_staff"] is False


def test_usuario_duplicado_retorna_409(test_user_data):
    with TestClient(app) as client:
        first = client.post(
            "/auth/register",
            json=test_user_data,
        )

        assert first.status_code == 201, first.text

        duplicate = client.post(
            "/auth/register",
            json=test_user_data,
        )

        body = duplicate.json()

        assert duplicate.status_code == 409
        assert body["error"]["code"] == 409
        assert body["error"]["message"] == "Usu\u00e1rio j\u00e1 cadastrado."


def test_cadastrar_usuarioname_too_short():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": "ab",
                "password": "Senha123!",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_username_muito_longo_retorna_422():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": "a" * 151,
                "password": "Senha123!",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_cadastrar_usuarioname_only_spaces():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": "   ",
                "password": "Senha123!",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_senha_muito_curta_retorna_422():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": f"teste_{uuid.uuid4().hex[:8]}",
                "password": "12345",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_cadastro_sem_username_retorna_422():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "password": "Senha123!",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_cadastro_sem_senha_retorna_422():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={
                "username": f"teste_{uuid.uuid4().hex[:8]}",
                "email": "teste@example.com",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_login_retorna_token_bearer(test_user_data):
    with TestClient(app) as client:
        _register_user(client, test_user_data)

        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert "access_token" in body
        assert body["access_token"]
        assert body["token_type"] == "bearer"


def test_login_invalido_retorna_401():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            data={
                "username": "usuario_inexistente",
                "password": "senha_invalida",
            },
        )

        body = response.json()

        assert response.status_code == 401
        assert body["error"]["code"] == 401
        assert body["error"]["message"] == "Usu\u00e1rio ou senha inv\u00e1lidos."


def test_login_com_senha_incorreta_retorna_401(test_user_data):
    with TestClient(app) as client:
        _register_user(client, test_user_data)

        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "SenhaErrada123",
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_login_exige_dados_formulario():
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={
                "username": "usuario",
                "password": "senha",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_consultar_usuario_sem_token_retorna_401():
    with TestClient(app) as client:
        response = client.get("/auth/me")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_token_invalido_retorna_401():
    with TestClient(app) as client:
        response = client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer token_invalido"
            },
        )

        assert response.status_code == 401

        body = response.json()

        assert body["error"]["code"] == 401
        assert body["error"]["message"] == "Token inv\u00e1lido ou expirado."


def test_token_expirado_retorna_401():
    with TestClient(app) as client:
        payload = {
            "sub": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
        }

        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        response = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_token_sem_usuario_retorna_401():
    with TestClient(app) as client:
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
        }

        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        response = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_token_de_usuario_inexistente_retorna_401():
    with TestClient(app) as client:
        payload = {
            "sub": f"inexistente_{uuid.uuid4().hex}",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        }

        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        response = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_listar_produtos_exige_autenticacao():
    with TestClient(app) as client:
        response = client.get("/products")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_criar_produto_sem_autenticacao_retorna_401():
    with TestClient(app) as client:
        response = client.post(
            "/products",
            json={
                "name": "Produto sem token",
                "description": "Teste",
                "price": 10.00,
                "status": "Ativo",
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_atualizar_produto_sem_autenticacao_retorna_401():
    with TestClient(app) as client:
        response = client.put(
            "/products/000000000000000000000001",
            json={
                "name": "Produto",
                "description": "Teste",
                "price": 10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_excluir_produto_sem_autenticacao_retorna_401():
    with TestClient(app) as client:
        response = client.delete(
            "/products/000000000000000000000001"
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == 401


def test_usuario_comum_pode_listar_produtos(test_user_data):
    with TestClient(app) as client:
        headers = _user_headers(client, test_user_data)

        response = client.get(
            "/products",
            headers=headers,
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_usuario_comum_nao_pode_criar_produto(test_user_data):
    with TestClient(app) as client:
        headers = _user_headers(client, test_user_data)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto teste",
                "description": "Teste",
                "price": 10.50,
                "status": "Ativo",
            },
        )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == 403


def test_usuario_comum_nao_pode_atualizar_produto(test_user_data):
    with TestClient(app) as client:
        admin_headers = _admin_headers(client)

        product = _create_product(
            client,
            admin_headers,
        )

        product_id = product["id"]

        try:
            user_headers = _user_headers(
                client,
                test_user_data,
            )

            response = client.put(
                f"/products/{product_id}",
                headers=user_headers,
                json={
                    "name": "Tentativa alteraÃ§Ã£o",
                    "description": "Sem permissÃ£o",
                    "price": 150,
                    "status": "Inativo",
                },
            )

            assert response.status_code == 403
            assert response.json()["error"]["code"] == 403

        finally:
            _cleanup_product(product_id)


def test_usuario_comum_nao_pode_excluir_produto(test_user_data):
    with TestClient(app) as client:
        admin_headers = _admin_headers(client)

        product = _create_product(
            client,
            admin_headers,
        )

        product_id = product["id"]

        try:
            user_headers = _user_headers(
                client,
                test_user_data,
            )

            response = client.delete(
                f"/products/{product_id}",
                headers=user_headers,
            )

            assert response.status_code == 403
            assert response.json()["error"]["code"] == 403

        finally:
            _cleanup_product(product_id)


def test_usuario_comum_pode_consultar_produto(test_user_data):
    with TestClient(app) as client:
        admin_headers = _admin_headers(client)

        product = _create_product(
            client,
            admin_headers,
        )

        product_id = product["id"]

        try:
            user_headers = _user_headers(
                client,
                test_user_data,
            )

            response = client.get(
                f"/products/{product_id}",
                headers=user_headers,
            )

            assert response.status_code == 200
            assert response.json()["id"] == product_id

        finally:
            _cleanup_product(product_id)


def test_admin_pode_criar_produto():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
            name="Notebook teste",
            price=2500.50,
        )

        product_id = product["id"]

        try:
            assert product["name"] == "Notebook teste"
            assert float(product["price"]) == 2500.50
            assert product["status"] == "Ativo"
            assert "created_at" in product
            assert product_id

        finally:
            _cleanup_product(product_id)


def test_admin_pode_listar_produtos():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            response = client.get(
                "/products",
                headers=headers,
            )

            assert response.status_code == 200

            products = response.json()

            assert isinstance(products, list)

            assert any(
                item["id"] == product_id
                for item in products
            )

        finally:
            _cleanup_product(product_id)


def test_admin_pode_consultar_produto_por_id():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            response = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert response.status_code == 200
            assert response.json()["id"] == product_id
            assert response.json()["name"] == product["name"]

        finally:
            _cleanup_product(product_id)


def test_admin_pode_atualizar_produto():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            response = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": "Produto alterado",
                    "description": "DescriÃ§Ã£o alterada",
                    "price": 199.90,
                    "status": "Inativo",
                },
            )

            assert response.status_code == 200

            body = response.json()

            assert body["id"] == product_id
            assert body["name"] == "Produto alterado"
            assert body["description"] == "DescriÃ§Ã£o alterada"
            assert float(body["price"]) == 199.90
            assert body["status"] == "Inativo"

        finally:
            _cleanup_product(product_id)


def test_atualizacao_mantem_data_de_criacao():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]
        created_at = product["created_at"]

        try:
            response = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": "Produto atualizado",
                    "description": "Teste regressÃ£o",
                    "price": 200,
                    "status": "Ativo",
                },
            )

            assert response.status_code == 200
            assert response.json()["created_at"] == created_at

        finally:
            _cleanup_product(product_id)


def test_admin_pode_excluir_produto():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        response = client.delete(
            f"/products/{product_id}",
            headers=headers,
        )

        assert response.status_code == 204

        response_get = client.get(
            f"/products/{product_id}",
            headers=headers,
        )

        assert response_get.status_code == 404


def test_crud_completo_produto_com_admin():
    with TestClient(app) as client:
        headers = _admin_headers(client)

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
            listed = client.get(
                "/products",
                headers=headers,
            )

            assert listed.status_code == 200

            assert any(
                item["id"] == product_id
                for item in listed.json()
            )

            fetched = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert fetched.status_code == 200

            updated = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": name,
                    "description": "DescriÃ§Ã£o alterada",
                    "price": 120.00,
                    "status": "Inativo",
                },
            )

            assert updated.status_code == 200
            assert updated.json()["status"] == "Inativo"

            deleted = client.delete(
                f"/products/{product_id}",
                headers=headers,
            )

            assert deleted.status_code == 204

            missing = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert missing.status_code == 404
            assert missing.json()["error"]["code"] == 404

        finally:
            _cleanup_product(product_id)


def test_consultar_produto_inexistente_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.get(
            "/products/000000000000000000000001",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_atualizar_produto_inexistente_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.put(
            "/products/000000000000000000000001",
            headers=headers,
            json={
                "name": "Produto inexistente",
                "description": "Teste",
                "price": 100,
                "status": "Ativo",
            },
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_excluir_produto_inexistente_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.delete(
            "/products/000000000000000000000001",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_id_produto_invalido_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.get(
            "/products/id-invalido",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_atualizar_id_produto_invalido_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.put(
            "/products/id-invalido",
            headers=headers,
            json={
                "name": "Produto",
                "description": "Teste",
                "price": 50,
                "status": "Ativo",
            },
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_excluir_id_produto_invalido_retorna_404():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.delete(
            "/products/id-invalido",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == 404


def test_preco_produto_invalido_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto invÃ¡lido",
                "description": "",
                "price": 0,
                "status": "Ativo",
            },
        )

        body = response.json()

        assert response.status_code == 422
        assert body["error"]["code"] == 422
        assert body["error"]["message"] == "Dados da requisi\u00e7\u00e3o inv\u00e1lidos."


def test_preco_produto_negativo_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto",
                "description": "",
                "price": -10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_preco_com_mais_de_duas_casas_decimais_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto",
                "description": "",
                "price": 10.999,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_preco_produto_acima_limite_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto",
                "description": "",
                "price": 1234567890123.00,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_status_produto_invalido_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto invÃ¡lido",
                "description": "",
                "price": 10,
                "status": "Qualquer",
            },
        )

        body = response.json()

        assert response.status_code == 422
        assert body["error"]["code"] == 422
        assert body["error"]["message"] == "Dados da requisi\u00e7\u00e3o inv\u00e1lidos."


def test_nome_produto_vazio_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "   ",
                "description": "",
                "price": 10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_nome_produto_acima_150_caracteres_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "a" * 151,
                "description": "",
                "price": 10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_descricao_acima_1000_caracteres_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto",
                "description": "a" * 1001,
                "price": 10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_produto_sem_nome_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "description": "Produto sem nome",
                "price": 10,
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_produto_sem_preco_retorna_422():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto sem preÃ§o",
                "description": "Teste",
                "status": "Ativo",
            },
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == 422


def test_nome_produto_remove_espacos_extras():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
            name="   Notebook Dell   ",
        )

        product_id = product["id"]

        try:
            assert product["name"] == "Notebook Dell"

        finally:
            _cleanup_product(product_id)


def test_descricao_produto_remove_espacos_extras():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
            description="   DescriÃ§Ã£o do produto   ",
        )

        product_id = product["id"]

        try:
            assert product["description"] == "DescriÃ§Ã£o do produto"

        finally:
            _cleanup_product(product_id)


def test_status_produto_remove_espacos_extras():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
            status="  Ativo  ",
        )

        product_id = product["id"]

        try:
            assert product["status"] == "Ativo"

        finally:
            _cleanup_product(product_id)


def test_produto_utiliza_descricao_padrao():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": f"Produto {uuid.uuid4().hex[:8]}",
                "price": 25,
                "status": "Ativo",
            },
        )

        assert response.status_code == 201, response.text

        product = response.json()
        product_id = product["id"]

        try:
            assert product["description"] == ""

        finally:
            _cleanup_product(product_id)


def test_produto_utiliza_status_padrao():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": f"Produto {uuid.uuid4().hex[:8]}",
                "description": "Teste status padrÃ£o",
                "price": 25,
            },
        )

        assert response.status_code == 201, response.text

        product = response.json()
        product_id = product["id"]

        try:
            assert product["status"] == "Ativo"

        finally:
            _cleanup_product(product_id)


def test_regressao_preco_pode_ser_serializado():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        response = client.post(
            "/products",
            headers=headers,
            json={
                "name": f"Produto decimal {uuid.uuid4().hex[:6]}",
                "description": "Teste de regressÃ£o",
                "price": 3299.90,
                "status": "Ativo",
            },
        )

        assert response.status_code == 201, response.text

        product = response.json()
        product_id = product["id"]

        try:
            assert "price" in product
            assert float(product["price"]) == 3299.90

        finally:
            _cleanup_product(product_id)


def test_regressao_login_utiliza_formulario(test_user_data):
    with TestClient(app) as client:
        _register_user(client, test_user_data)

        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        assert "access_token" in response.json()


def test_regressao_produto_criado_pode_ser_consultado():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            response = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert response.status_code == 200
            assert response.json()["id"] == product_id

        finally:
            _cleanup_product(product_id)


def test_regressao_atualizacao_produto_e_persistida():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            update = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": "Produto regressÃ£o",
                    "description": "Alterado",
                    "price": 500,
                    "status": "Inativo",
                },
            )

            assert update.status_code == 200

            get_product = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert get_product.status_code == 200

            body = get_product.json()

            assert body["name"] == "Produto regressÃ£o"
            assert body["description"] == "Alterado"
            assert float(body["price"]) == 500
            assert body["status"] == "Inativo"

        finally:
            _cleanup_product(product_id)


def test_regressao_produto_excluido_continua_excluido():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        delete = client.delete(
            f"/products/{product_id}",
            headers=headers,
        )

        assert delete.status_code == 204

        first_get = client.get(
            f"/products/{product_id}",
            headers=headers,
        )

        second_get = client.get(
            f"/products/{product_id}",
            headers=headers,
        )

        assert first_get.status_code == 404
        assert second_get.status_code == 404


def test_regressao_usuario_comum_nao_gerencia_produtos(
    test_user_data,
):
    with TestClient(app) as client:
        headers = _user_headers(
            client,
            test_user_data,
        )

        create = client.post(
            "/products",
            headers=headers,
            json={
                "name": "Produto bloqueado",
                "description": "Teste",
                "price": 20,
                "status": "Ativo",
            },
        )

        assert create.status_code == 403


def test_regressao_admin_continua_gerenciando_produtos():
    with TestClient(app) as client:
        headers = _admin_headers(client)

        product = _create_product(
            client,
            headers,
        )

        product_id = product["id"]

        try:
            get_response = client.get(
                f"/products/{product_id}",
                headers=headers,
            )

            assert get_response.status_code == 200

            update_response = client.put(
                f"/products/{product_id}",
                headers=headers,
                json={
                    "name": "Produto admin",
                    "description": "Teste",
                    "price": 100,
                    "status": "Ativo",
                },
            )

            assert update_response.status_code == 200

        finally:
            _cleanup_product(product_id)


