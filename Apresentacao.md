# Roteiro de apresentação

Sequência sugerida para demonstrar o projeto.

1. **Subir o ambiente**
   `docker compose up -d --build` → `docker compose ps` (mostrar API, PostgreSQL e MongoDB rodando)

2. **Swagger** — `http://localhost:8000/docs`, apresentar endpoints de autenticação e produtos.

3. **Autenticação** — cadastro → login → JWT → `GET /auth/me`. Explicar que os usuários ficam no PostgreSQL.

4. **Permissões** — tentar criar produto com usuário comum (`403 Forbidden`), repetir como admin (sucesso). Mostrar a diferença entre `401` (não autenticado) e `403` (sem permissão).

5. **CRUD de produtos** — `POST` → `GET` → `GET /{id}` → `PUT` → `DELETE`, reforçando que tudo é persistido no MongoDB.

6. **Validações** — enviar produto com preço `0` ou nome vazio, mostrar `422 Unprocessable Entity`.

7. **Django Admin** — `http://localhost:8000/admin/`: usuários, permissões e produtos (somente leitura, já que o cadastro é exclusivo da API).

8. **Arquitetura** — apresentar `docs/arquitetura.png` e explicar a separação de responsabilidades entre FastAPI, PostgreSQL, MongoDB, Django Admin e `ProductRepository`.

9. **Testes** — `docker compose exec api pytest -v`, mostrar os 10 testes passando.

10. **Relatório HTML** — abrir `reports/test-report.html`.

11. **Encerramento** — reforçar os pontos técnicos: FastAPI + Django, PostgreSQL + MongoDB, JWT + OAuth2, Repository Pattern, Docker Compose, Swagger/OpenAPI, Pytest + pytest-html.