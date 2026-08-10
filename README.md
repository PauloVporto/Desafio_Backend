# Desafio Backend - Think Technology

Projeto desenvolvido para o desafio técnico de Backend da Think Technology.

A aplicação consiste em uma API REST para autenticação de usuários e gerenciamento de produtos. O projeto foi desenvolvido em Python utilizando FastAPI, Django Admin, PostgreSQL e MongoDB.

## Tecnologias utilizadas

* Python 3.11
* FastAPI
* Django / Django Admin
* PostgreSQL
* MongoDB
* SQLAlchemy
* Pydantic
* JWT / OAuth2
* Docker e Docker Compose
* Pytest
* GitHub Actions

## Como funciona

A aplicação utiliza dois bancos de dados.

O **PostgreSQL** é utilizado para armazenar os usuários, credenciais e permissões.

O **MongoDB** é utilizado para armazenar os produtos.

A API foi desenvolvida com FastAPI e o Django Admin foi integrado ao projeto para permitir a administração dos usuários e a consulta dos produtos cadastrados.

Os produtos exibidos pelo Django Admin são somente para leitura. O cadastro, alteração e exclusão são feitos pela API.

## Estrutura do projeto

```text
Desafio_Backend/
├── app/
│   ├── auth/
│   ├── products/
│   └── main.py
├── config/
├── docs/
├── reports/
├── templates/
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── users/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Executando o projeto

Para executar o projeto é necessário ter Docker e Docker Compose instalados.

Primeiro crie o arquivo `.env` utilizando o exemplo disponível no projeto:

```bash
cp .env.example .env
```

No Windows também é possível simplesmente copiar o `.env.example` e renomear a cópia para `.env`.

Depois execute:

```bash
docker compose up -d --build
```

Para verificar se os containers estão funcionando:

```bash
docker compose ps
```

A API ficará disponível em:

```text
http://localhost:8000
```

## Swagger

A documentação da API pode ser acessada em:

```text
http://localhost:8000/docs
```

Por ela é possível testar o cadastro, login e todas as operações de produtos.

## Endpoints

### Autenticação

| Método | Endpoint         | Descrição                    |
| ------ | ---------------- | ---------------------------- |
| POST   | `/auth/register` | Cadastro de usuário          |
| POST   | `/auth/login`    | Login e geração do token JWT |
| GET    | `/auth/me`       | Dados do usuário autenticado |

### Produtos

| Método | Endpoint         | Descrição           |
| ------ | ---------------- | ------------------- |
| GET    | `/products`      | Lista os produtos   |
| GET    | `/products/{id}` | Busca um produto    |
| POST   | `/products`      | Cadastra um produto |
| PUT    | `/products/{id}` | Atualiza um produto |
| DELETE | `/products/{id}` | Exclui um produto   |

Também existe um endpoint para verificar se a aplicação está funcionando:

```text
GET /health
```

Resposta:

```json
{
  "status": "ok"
}
```

## Autenticação e permissões

A autenticação utiliza OAuth2 Password Flow com JWT.

Após realizar o login, a API retorna um `access_token`, que deve ser utilizado nos endpoints protegidos.

Existem dois níveis de acesso:

* usuário comum;
* administrador.

Usuários comuns podem consultar produtos, mas não podem criar, alterar ou excluir.

Essas operações são permitidas somente para administradores.

Dessa forma, a API também trata corretamente situações de usuário não autenticado (`401`) e usuário autenticado sem permissão (`403`).

## Django Admin

O painel administrativo está disponível em:

```text
http://localhost:8000/admin/
```

Ele é utilizado para gerenciamento dos usuários e permissões.

Os produtos armazenados no MongoDB também podem ser consultados pelo painel, porém ficam disponíveis somente para leitura.

## Testes

Os testes automatizados foram desenvolvidos utilizando Pytest.

Atualmente a suíte possui **64 testes**, cobrindo os principais fluxos da aplicação, incluindo:

* cadastro de usuários;
* login;
* autenticação JWT;
* tokens inválidos e expirados;
* permissões de usuário e administrador;
* CRUD de produtos;
* validação dos dados;
* tratamento de erros;
* produtos inexistentes;
* testes de regressão.

Para executar:

```bash
docker compose exec api pytest -v
```

Resultado atual:

```text
64 passed
0 failed
```

## Relatório dos testes

Também foi utilizado o `pytest-html` para gerar um relatório da execução.

O relatório atual está disponível em:

```text
reports/test-report.html
```

Para gerar novamente:

```bash
docker compose exec api pytest -v --html=/app/reports/test-report.html --self-contained-html
```

## Integração contínua

O projeto utiliza GitHub Actions para executar os testes automaticamente.

O workflow é executado em pushes e pull requests para a branch `main`.

Assim, alterações no projeto passam pela suíte de testes antes de serem consideradas válidas.

## Variáveis de ambiente

O arquivo `.env` não é versionado.

As variáveis necessárias para executar o projeto estão documentadas no:

```text
.env.example
```

Para executar localmente, basta criar o `.env` a partir desse arquivo e ajustar os valores caso seja necessário.

## Parando o projeto

Para parar os containers:

```bash
docker compose down
```

Para remover também os volumes:

```bash
docker compose down -v
```

## Resultado

O projeto possui:

* API REST com FastAPI;
* autenticação JWT;
* controle de acesso por usuário;
* PostgreSQL para usuários;
* MongoDB para produtos;
* CRUD de produtos;
* Django Admin;
* Docker Compose;
* documentação Swagger;
* 64 testes automatizados;
* relatório HTML dos testes;
* integração contínua com GitHub Actions.

Status atual dos testes:

```text
64/64 testes aprovados
```
