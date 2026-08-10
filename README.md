# Desafio Backend — Think Technology

API REST desenvolvida em **Python**, utilizando **FastAPI** como framework principal, **Django** exclusivamente para administração (Django Admin), **PostgreSQL** para autenticação/usuários e **MongoDB** para o cadastro de produtos.

## Arquitetura

![Arquitetura da aplicação]([docs/arquitetura.png](https://github.com/PauloVporto/Desafio_Backend/blob/main/docs/arquitetura_thinktechnology.png))

| Componente | Responsabilidade |
|---|---|
| **FastAPI** | API REST: autenticação, autorização, validação e CRUD de produtos |
| **Django Admin** | Administração de usuários e consulta (somente leitura) de produtos |
| **PostgreSQL** | Persistência de usuários, credenciais e permissões |
| **MongoDB** | Persistência de produtos, acessado via `ProductRepository` |
| **JWT / OAuth2** | Autenticação e autorização das rotas |
| **Docker Compose** | Orquestração dos três serviços (API, Postgres, Mongo) |

O `ProductRepository` isola o acesso ao MongoDB do restante da aplicação, reduzindo o acoplamento entre a API e a camada de persistência.

## Tecnologias

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| API REST | FastAPI + Uvicorn |
| Administração | Django / Django Admin |
| Banco relacional | PostgreSQL |
| Banco NoSQL | MongoDB |
| Validação | Pydantic |
| Segurança | OAuth2 Password Flow / JWT |
| Infraestrutura | Docker / Docker Compose |
| Documentação | Swagger / OpenAPI |
| Testes | Pytest + pytest-html |

## Como executar

**Pré-requisitos:** Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up
```

A API sobe em `http://localhost:8000`.

| Recurso | URL |
|---|---|
| Swagger / OpenAPI | http://localhost:8000/docs |
| Django Admin | http://localhost:8000/admin/ |
| Health check | http://localhost:8000/health |

## Endpoints

**Autenticação**

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/register` | Cadastra um novo usuário |
| POST | `/auth/login` | Autentica e retorna o JWT |
| GET | `/auth/me` | Retorna os dados do usuário autenticado |

**Produtos** (todas exigem JWT)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/products` | Cadastra um produto |
| GET | `/products` | Lista os produtos |
| GET | `/products/{id}` | Consulta um produto por ID |
| PUT | `/products/{id}` | Atualiza um produto |
| DELETE | `/products/{id}` | Exclui um produto |

## Autenticação e permissões

O login segue o fluxo **OAuth2 Password Flow**: o usuário envia usuário/senha, a API valida contra o PostgreSQL e retorna um **JWT**, que deve ser enviado como Bearer token nas rotas protegidas.

- Usuário sem token → `401 Unauthorized`
- Usuário autenticado sem permissão (ex.: usuário comum tentando criar/editar/excluir produto) → `403 Forbidden`
- Apenas administradores podem criar, atualizar ou excluir produtos; qualquer usuário autenticado pode listar/consultar.

Os produtos exibidos no Django Admin são **somente leitura** — o cadastro é feito exclusivamente pela API FastAPI.

## Validações e erros

Validações realizadas via Pydantic: campos obrigatórios, nome não vazio, preço maior que zero, status restrito a `Ativo`/`Inativo`. Erros seguem um formato padronizado (`{"error": {"code": ..., "message": ..., "details": ...}}`), com os códigos HTTP apropriados (`401`, `403`, `404`, `409`, `422`).

## Testes

```bash
docker compose exec api pytest -v
```

Suíte atual: **10/10 testes aprovados**, cobrindo health check, cadastro/login/JWT, usuário duplicado, credenciais inválidas, autenticação/autorização em rotas protegidas, CRUD completo de produtos e validações de preço/status/nome.

Para gerar o relatório HTML:

```bash
docker compose exec api pytest -v --html=/tmp/test-report.html --self-contained-html
docker cp desafio-api:/tmp/test-report.html ./reports/test-report.html
```

## Estrutura do projeto

```
app/
├── auth/          # rotas, schemas e segurança (JWT)
└── products/      # rotas, schemas e ProductRepository (MongoDB)
config/            # settings do Django
users/             # app Django (modelo de usuário / Admin)
tests/             # suíte de testes (Pytest)
docs/              # diagrama de arquitetura
reports/           # relatório HTML dos testes
docker-compose.yml
Dockerfile
requirements.txt
```

## Segurança

`.env` não é versionado — use `.env.example` como referência para as variáveis necessárias.

---

Um roteiro passo a passo para apresentação do projeto está em [`docs/APRESENTACAO.md`](docs/APRESENTACAO.md).
