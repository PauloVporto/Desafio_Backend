# Desafio Backend - Think Technology

API REST desenvolvida em Python como parte do desafio técnico para Backend Developer.

O projeto utiliza FastAPI para disponibilização da API, Django para o painel administrativo, PostgreSQL para usuários e autenticação e MongoDB para armazenamento dos produtos.

Toda a aplicação é executada com Docker Compose.

## Tecnologias utilizadas

* Python 3.11
* FastAPI
* Django
* PostgreSQL
* MongoDB
* JWT
* Docker
* Docker Compose
* Pytest
* GitHub Actions

## Estrutura do projeto

```text
Desafio_Backend/
├── .github/
│   └── workflows/
├── app/
│   ├── auth/
│   ├── products/
│   └── main.py
├── config/
├── docs/
├── reports/
├── templates/
├── tests/
├── users/
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── Makefile
├── manage.py
├── pytest.ini
├── README.md
└── requirements.txt
```

A aplicação foi separada em módulos para manter as responsabilidades organizadas.

O FastAPI é responsável pela API REST e o Django é utilizado para o painel administrativo.

A persistência também é separada de acordo com a responsabilidade de cada dado:

* PostgreSQL: usuários e autenticação;
* MongoDB: produtos.

## Como executar

### Pré-requisitos

É necessário ter instalado:

* Docker
* Docker Compose

### 1. Clone o repositório

```bash
git clone https://github.com/PauloVporto/Desafio_Backend.git
cd Desafio_Backend
```

### 2. Inicie a aplicação

```bash
docker compose up
```

O projeto possui valores padrão para o ambiente de desenvolvimento, portanto não é necessário criar um arquivo `.env` para iniciar a aplicação.

Caso seja necessário alterar alguma configuração, o arquivo `.env.example` pode ser utilizado como referência.

Na primeira execução o Docker irá construir a imagem da aplicação e iniciar os serviços:

```text
API FastAPI
PostgreSQL
MongoDB
```

Para executar em segundo plano:

```bash
docker compose up -d
```

Para reconstruir a imagem:

```bash
docker compose up --build
```

## Acessando a aplicação

Após os containers iniciarem, a API estará disponível em:

```text
http://localhost:8000
```

### Swagger

A documentação interativa da API pode ser acessada em:

```text
http://localhost:8000/docs
```

### Health Check

```text
GET http://localhost:8000/health
```

Retorno esperado:

```json
{
  "status": "ok"
}
```

### Django Admin

O painel administrativo pode ser acessado em:

```text
http://localhost:8000/admin/
```

O Django Admin é utilizado para administração dos usuários e visualização dos produtos.

O cadastro e gerenciamento dos produtos são realizados pela API FastAPI.

## Autenticação

A autenticação da aplicação utiliza JWT.

### Cadastro

```http
POST /auth/register
```

Exemplo:

```json
{
  "username": "usuario",
  "email": "usuario@email.com",
  "password": "123456"
}
```

### Login

```http
POST /auth/login
```

O login utiliza `application/x-www-form-urlencoded`.

Exemplo:

```text
username=usuario
password=123456
```

Após a autenticação é retornado um token JWT.

Exemplo:

```json
{
  "access_token": "TOKEN_JWT",
  "token_type": "bearer"
}
```

Para acessar uma rota protegida:

```http
Authorization: Bearer TOKEN_JWT
```

### Usuário autenticado

```http
GET /auth/me
```

Retorna as informações do usuário associado ao token.

## Produtos

Os produtos são armazenados no MongoDB.

Cada produto possui:

* ID;
* nome;
* descrição;
* preço;
* status;
* data de criação.

### Rotas

| Método | Endpoint         | Descrição           |
| ------ | ---------------- | ------------------- |
| POST   | `/products`      | Cadastra um produto |
| GET    | `/products`      | Lista os produtos   |
| GET    | `/products/{id}` | Busca um produto    |
| PUT    | `/products/{id}` | Atualiza um produto |
| DELETE | `/products/{id}` | Remove um produto   |

As rotas de produtos exigem autenticação via JWT.

## Permissões

A aplicação diferencia usuários comuns e administradores.

Usuários autenticados podem consultar os produtos.

Operações de criação, alteração e exclusão são protegidas por controle de permissão.

Quando o usuário não está autenticado, a API retorna:

```text
401 Unauthorized
```

Quando está autenticado, mas não possui a permissão necessária:

```text
403 Forbidden
```

## Validações

A API possui validações para os principais dados recebidos.

Entre elas:

* campos obrigatórios;
* nome do produto não vazio;
* preço maior que zero;
* usuário duplicado;
* autenticação inválida;
* token JWT inválido ou expirado;
* produto inexistente;
* controle de permissões.

Os erros são retornados utilizando uma estrutura padronizada.

## Testes

Os testes automatizados foram implementados utilizando Pytest.

Para executar:

```bash
docker compose exec api pytest
```

Para uma saída mais detalhada:

```bash
docker compose exec api pytest -v
```

Os testes cobrem cenários relacionados a:

* cadastro de usuários;
* login;
* autenticação JWT;
* autorização;
* permissões;
* CRUD de produtos;
* validações;
* tratamento de erros;
* cenários de regressão.

## Relatório de testes

O projeto também possui geração de relatório HTML dos testes.

Os relatórios ficam armazenados no diretório:

```text
reports/
```

Isso permite consultar de forma visual os testes executados e seus resultados.

## CI/CD

O repositório possui integração contínua utilizando GitHub Actions.

O workflow executa automaticamente a suíte de testes para validar alterações realizadas no projeto.

A configuração está disponível em:

```text
.github/workflows/
```

Dessa forma, alterações enviadas ao repositório podem ser verificadas automaticamente antes de serem consideradas válidas.

## Docker

A aplicação utiliza Docker Compose para executar todos os componentes necessários.

Os principais serviços são:

```text
api
postgres
mongo
```

Os bancos possuem `healthcheck`, permitindo que a API aguarde os serviços necessários estarem disponíveis antes da inicialização.

### Verificar os containers

```bash
docker compose ps
```

### Visualizar os logs

```bash
docker compose logs -f
```

### Parar a aplicação

```bash
docker compose down
```

### Remover containers e volumes

```bash
docker compose down -v
```

## Arquitetura

A aplicação foi organizada buscando separar as responsabilidades entre API, autenticação, regras relacionadas aos produtos e persistência.

O FastAPI concentra a API REST enquanto o Django fica responsável pela interface administrativa.

Os dados também são separados entre os bancos conforme o objetivo de cada um:

```text
PostgreSQL
└── Usuários e autenticação

MongoDB
└── Produtos
```

Essa separação evita que a camada responsável pelas rotas fique diretamente ligada aos detalhes de persistência.

## Endpoints principais

```text
GET    /health

POST   /auth/register
POST   /auth/login
GET    /auth/me

POST   /products
GET    /products
GET    /products/{id}
PUT    /products/{id}
DELETE /products/{id}
```

A documentação completa e os schemas podem ser consultados pelo Swagger:

```text
http://localhost:8000/docs
```
