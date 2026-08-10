# Desafio Backend — Think Technology

API REST desenvolvida como desafio técnico, utilizando **FastAPI**, **Django**, **PostgreSQL** e **MongoDB**.

A aplicação implementa autenticação com **JWT**, controle de acesso, CRUD de produtos, persistência híbrida, painel administrativo com Django Admin, ambiente containerizado com Docker Compose e testes automatizados.

---

## 1. Arquitetura da aplicação

A aplicação utiliza uma arquitetura híbrida, separando as responsabilidades de autenticação, administração, persistência de usuários e gerenciamento de produtos.

![Arquitetura da aplicação](docs/arquitetura.png)

### Principais componentes

- **FastAPI** — responsável pela API REST.
- **Django Admin** — responsável pela administração dos usuários e consulta dos produtos.
- **PostgreSQL** — responsável pela persistência dos usuários, credenciais e permissões.
- **MongoDB** — responsável pela persistência dos produtos.
- **ProductRepository** — abstrai o acesso aos produtos armazenados no MongoDB.
- **Pydantic** — realiza validação dos dados recebidos pela API.
- **OAuth2 + JWT** — utilizados no processo de autenticação e autorização.
- **Docker Compose** — responsável pela execução integrada dos serviços.
- **Pytest** — utilizado nos testes automatizados.
- **pytest-html** — utilizado para geração do relatório HTML dos testes.

### Fluxo simplificado

```text
                    Usuário / Swagger
                           |
                           v
                        FastAPI
                      API REST
                     /    |    \
                    /     |     \
                   v      v      v
          Autenticação  Produtos  Django Admin
                |          |       /       \
                |          v      /         \
                |   ProductRepository       |
                |          |                |
                v          v                v
           PostgreSQL   MongoDB         Consulta
            Usuários   Produtos         administrativa
```

### Separação de responsabilidades

```text
FastAPI
   -> API REST
   -> autenticação
   -> autorização
   -> validação
   -> gerenciamento dos produtos

PostgreSQL
   -> usuários
   -> credenciais
   -> permissões

MongoDB
   -> produtos

Django Admin
   -> administração dos usuários
   -> gerenciamento de permissões
   -> consulta dos produtos
   -> produtos disponíveis somente para leitura

ProductRepository
   -> abstração da persistência dos produtos
   -> isolamento do acesso ao MongoDB

Docker Compose
   -> execução e integração dos serviços
```

O arquivo editável do diagrama pode ser mantido em:

```text
docs/arquitetura.drawio
```

E sua versão utilizada no README:

```text
docs/arquitetura.png
```

---

## 2. Tecnologias utilizadas

| Categoria | Tecnologias |
| --- | --- |
| Linguagem | Python 3.11 |
| API REST | FastAPI |
| Administração | Django / Django Admin |
| Servidor | Uvicorn |
| Banco relacional | PostgreSQL |
| Banco NoSQL | MongoDB |
| Persistência | SQLAlchemy / ProductRepository |
| Validação | Pydantic |
| Segurança | OAuth2 Password Flow / JWT |
| Infraestrutura | Docker / Docker Compose |
| Documentação | Swagger / OpenAPI |
| Testes | Pytest |
| Relatório de testes | pytest-html |

---

## 3. Estrutura do projeto

Estrutura simplificada:

```text
desafio_backend_final/
│
├── app/
│   ├── auth/
│   ├── products/
│   └── main.py
│
├── config/
│
├── tests/
│   └── test_api.py
│
├── reports/
│   └── test-report.html
│
├── docs/
│   ├── arquitetura.drawio
│   └── arquitetura.png
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Executando o projeto

### Pré-requisitos

É necessário possuir:

- Docker
- Docker Compose

### Subir o ambiente

Na raiz do projeto:

```bash
docker compose up -d
```

Na primeira execução ou após alterações nas dependências:

```bash
docker compose up -d --build
```

### Verificar os containers

```bash
docker compose ps
```

A aplicação utiliza três serviços principais:

| Serviço | Tecnologia | Responsabilidade |
| --- | --- | --- |
| API | FastAPI + Django | API REST e painel administrativo |
| Banco relacional | PostgreSQL | Persistência dos usuários |
| Banco NoSQL | MongoDB | Persistência dos produtos |

A API estará disponível em:

```text
http://localhost:8000
```

---

## 5. Documentação Swagger

A documentação interativa da API pode ser acessada em:

```text
http://localhost:8000/docs
```

Através do Swagger é possível testar os endpoints da aplicação diretamente pelo navegador.

### Endpoints de autenticação

| Método | Endpoint | Descrição |
| --- | --- | --- |
| POST | `/auth/register` | Cadastra um novo usuário |
| POST | `/auth/login` | Autentica o usuário e gera o JWT |
| GET | `/auth/me` | Retorna os dados do usuário autenticado |

### Endpoints de produtos

| Método | Endpoint | Descrição |
| --- | --- | --- |
| POST | `/products` | Cadastra um produto |
| GET | `/products` | Lista os produtos |
| GET | `/products/{id}` | Consulta um produto por ID |
| PUT | `/products/{id}` | Atualiza um produto |
| DELETE | `/products/{id}` | Exclui um produto |

### Health Check

A aplicação também disponibiliza:

```text
GET /health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

---

## 6. Autenticação

O projeto utiliza autenticação baseada em **OAuth2 Password Flow** e **JWT (JSON Web Token)**.

O fluxo de autenticação é:

```text
Usuário
   |
   v
POST /auth/login
   |
   v
Validação das credenciais
   |
   v
Geração do JWT
   |
   v
Access Token
   |
   v
Acesso aos endpoints protegidos
```

Para testar pelo Swagger:

1. cadastrar um usuário;
2. realizar o login;
3. obter o `access_token`;
4. autorizar a requisição;
5. executar os endpoints protegidos;
6. testar `GET /auth/me`.

Os dados relacionados aos usuários são persistidos exclusivamente no **PostgreSQL**.

---

## 7. Controle de acesso e permissões

A aplicação diferencia usuários comuns e administradores.

### Usuário comum

Um usuário comum pode:

- realizar login;
- acessar os recursos permitidos;
- consultar informações autorizadas.

Porém, não possui autorização para criar, alterar ou excluir produtos.

Quando tenta executar uma operação sem autorização, a API retorna:

```text
403 Forbidden
```

### Administrador

O administrador possui autorização para executar as operações de gerenciamento dos produtos.

Isso permite demonstrar a diferença entre:

```text
401 Unauthorized
```

Usuário não autenticado.

E:

```text
403 Forbidden
```

Usuário autenticado, porém sem permissão para realizar determinada operação.

---

## 8. CRUD de produtos

A API implementa o ciclo completo de gerenciamento dos produtos.

### Criar

```text
POST /products
```

### Listar

```text
GET /products
```

### Buscar por ID

```text
GET /products/{id}
```

### Atualizar

```text
PUT /products/{id}
```

### Excluir

```text
DELETE /products/{id}
```

O fluxo completo pode ser representado por:

```text
CREATE
   |
   v
 READ
   |
   v
UPDATE
   |
   v
DELETE
```

Os produtos são persistidos exclusivamente no **MongoDB**.

---

## 9. Repository Pattern

O acesso aos produtos armazenados no MongoDB é realizado através do:

```text
ProductRepository
```

O objetivo dessa camada é separar a regra da aplicação da implementação específica do banco de dados.

Fluxo:

```text
FastAPI
   |
   v
ProductRepository
   |
   v
MongoDB
```

Essa abordagem reduz o acoplamento entre a API e a camada de persistência.

---

## 10. Validações e tratamento de erros

A aplicação possui validações para impedir o envio de dados inválidos.

Entre os cenários tratados estão:

- produto com preço igual ou inferior a `0`;
- produto com nome vazio;
- status de produto inválido;
- credenciais de login inválidas;
- tentativa de cadastrar usuário duplicado;
- acesso a recurso protegido sem autenticação;
- tentativa de executar operação sem permissão.

A API utiliza códigos HTTP adequados para representar os erros.

Exemplos:

```text
401 Unauthorized
403 Forbidden
422 Unprocessable Entity
```

As validações dos dados enviados para a API são realizadas com auxílio do **Pydantic**.

---

## 11. Persistência híbrida

A aplicação utiliza dois bancos de dados com responsabilidades diferentes.

### PostgreSQL

Responsável pelos dados relacionados aos usuários:

```text
PostgreSQL
   |
   ├── usuários
   ├── credenciais
   └── permissões
```

### MongoDB

Responsável pelos produtos:

```text
MongoDB
   |
   └── produtos
       ├── nome
       ├── descrição
       ├── preço
       ├── status
       └── ID
```

Essa separação permite demonstrar a utilização de persistência relacional e NoSQL na mesma aplicação.

---

## 12. Django Admin

O painel administrativo está disponível em:

```text
http://localhost:8000/admin/
```

O Django Admin é utilizado para:

- administração dos usuários;
- visualização das informações dos usuários;
- gerenciamento das permissões;
- consulta dos produtos cadastrados.

### Produtos no Django Admin

Os produtos exibidos no painel administrativo são **somente para consulta**.

O cadastro, alteração e exclusão dos produtos são realizados exclusivamente através da **API REST FastAPI**.

Dessa forma:

```text
Django Admin
     |
     ├── Usuários -> administração
     |
     └── Produtos -> somente leitura
```

---

## 13. Docker

Todo o ambiente da aplicação é executado através do Docker Compose.

Os três principais serviços são:

```text
Docker Compose
│
├── API
│   ├── FastAPI
│   └── Django
│
├── PostgreSQL
│
└── MongoDB
```

Para visualizar os containers:

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f
```

Para acompanhar apenas os logs da API:

```bash
docker compose logs -f api
```

Para parar os serviços:

```bash
docker compose down
```

Para reconstruir a aplicação:

```bash
docker compose up -d --build
```

---

## 14. Testes automatizados

O projeto possui uma suíte de testes automatizados desenvolvida com **Pytest** e executada dentro do container da API.

Os testes verificam os principais fluxos funcionais e regras da aplicação.

### Executar os testes

Com os containers em execução:

```bash
docker compose exec api pytest -v
```

Resultado validado para esta versão:

```text
collected 10 items

tests/test_api.py .......... [100%]

10 passed, 1 warning
```

Resultado:

```text
10 testes executados
10 testes aprovados
0 falhas
0 erros
0 testes ignorados
```

O warning apresentado durante a execução está relacionado à depreciação do middleware WSGI do Starlette e não representa falha na suíte.

---

## 15. Cobertura funcional dos testes

A suíte possui os seguintes testes:

| Teste | Validação |
| --- | --- |
| `test_health` | Verifica se a API está disponível e saudável |
| `test_register_login_and_me` | Valida cadastro, login, geração do JWT e consulta do usuário autenticado |
| `test_duplicate_user_returns_standard_error` | Verifica tentativa de cadastro de usuário duplicado |
| `test_invalid_login_returns_standard_error` | Verifica o tratamento de credenciais inválidas |
| `test_product_requires_authentication` | Confirma que endpoints protegidos exigem autenticação |
| `test_regular_user_cannot_create_product` | Confirma que usuário comum não pode cadastrar produtos |
| `test_product_crud_with_admin` | Valida criação, consulta, alteração e exclusão pelo administrador |
| `test_invalid_product_price_returns_standard_error` | Valida rejeição de produto com preço inválido |
| `test_invalid_product_status_returns_standard_error` | Valida rejeição de status inválido |
| `test_empty_product_name_returns_standard_error` | Valida rejeição de produto sem nome válido |

A suíte verifica cenários de:

- disponibilidade da API;
- cadastro;
- autenticação;
- JWT;
- autorização;
- controle de acesso;
- CRUD;
- validação de dados;
- tratamento de erros.

---

## 16. Relatório HTML dos testes

Além da execução pelo terminal, o projeto utiliza **pytest-html** para gerar um relatório visual da suíte.

### Gerar o relatório

Execute:

```bash
docker compose exec api pytest -v --html=/tmp/test-report.html --self-contained-html
```

Depois copie o arquivo gerado para a pasta `reports`:

```bash
docker cp desafio-api:/tmp/test-report.html ./reports/test-report.html
```

O relatório ficará disponível em:

```text
reports/test-report.html
```

O relatório apresenta:

- ambiente de execução;
- versão do Python;
- versão do Pytest;
- plugins utilizados;
- quantidade de testes;
- testes aprovados;
- testes reprovados;
- duração individual;
- resultado geral da suíte.

Resultado atual:

```text
10 Passed
0 Failed
0 Skipped
0 Errors
```

O relatório fornece uma evidência visual e reproduzível da execução dos testes automatizados.

---

## 17. Segurança do repositório

Informações sensíveis e arquivos gerados localmente não devem ser enviados ao repositório.

O `.gitignore` deve incluir itens como:

```gitignore
.env
__pycache__/
*.pyc
.pytest_cache/
staticfiles/
```

O arquivo:

```text
.env
```

não deve ser versionado.

Para documentar as variáveis necessárias para execução, pode ser disponibilizado:

```text
.env.example
```

Esse arquivo deve possuir apenas valores de exemplo, sem credenciais reais.

---

## 18. Resumo técnico

O projeto demonstra:

- API REST desenvolvida com FastAPI;
- Python 3.11;
- autenticação JWT;
- OAuth2 Password Flow;
- controle de acesso por perfil;
- PostgreSQL para usuários;
- MongoDB para produtos;
- persistência híbrida;
- CRUD completo de produtos;
- validação com Pydantic;
- tratamento de erros HTTP;
- Django Admin integrado;
- administração de usuários;
- consulta de produtos pelo Admin;
- Repository Pattern;
- Docker;
- Docker Compose;
- documentação Swagger/OpenAPI;
- testes automatizados com Pytest;
- relatório HTML com pytest-html.

### Status dos testes

```text
10/10 testes aprovados
100% da suíte executada com sucesso
0 falhas
```

---

# Roteiro de apresentação

A sequência abaixo pode ser utilizada durante a apresentação do projeto.

## 1. Subir o ambiente

Execute:

```bash
docker compose up -d --build
```

Depois:

```bash
docker compose ps
```

Mostrar os três serviços em execução:

```text
API
PostgreSQL
MongoDB
```

---

## 2. Mostrar o Swagger

Acessar:

```text
http://localhost:8000/docs
```

Apresentar rapidamente os endpoints de autenticação e produtos.

---

## 3. Demonstrar autenticação

Realizar:

```text
Cadastro
   ↓
Login
   ↓
JWT
   ↓
Autorização
   ↓
GET /auth/me
```

Explicar que os usuários são persistidos no PostgreSQL.

---

## 4. Demonstrar permissões

Utilizar um usuário comum para tentar criar um produto.

Mostrar o retorno:

```text
403 Forbidden
```

Depois realizar a mesma operação como administrador e mostrar que a operação é permitida.

---

## 5. Demonstrar o CRUD

Executar na seguinte ordem:

```text
POST /products
GET /products
GET /products/{id}
PUT /products/{id}
DELETE /products/{id}
```

Explicar que os produtos são persistidos no MongoDB.

---

## 6. Demonstrar validações

Enviar, por exemplo:

```json
{
  "name": "Produto inválido",
  "description": "",
  "price": 0,
  "status": "Ativo"
}
```

Mostrar o retorno:

```text
422 Unprocessable Entity
```

Também pode ser demonstrado um produto com nome vazio ou status inválido.

---

## 7. Mostrar o Django Admin

Acessar:

```text
http://localhost:8000/admin/
```

Mostrar:

- usuários;
- permissões;
- produtos cadastrados;
- tela personalizada de consulta de produtos.

Explicar que os produtos são somente leitura no Django Admin.

O CRUD dos produtos é realizado exclusivamente pela API REST.

---

## 8. Explicar a arquitetura

Apresentar o diagrama:

```text
docs/arquitetura.png
```

Explicar principalmente:

```text
FastAPI
   -> API REST

PostgreSQL
   -> usuários

MongoDB
   -> produtos

Django Admin
   -> administração de usuários
   -> consulta de produtos

ProductRepository
   -> isolamento do MongoDB

Docker Compose
   -> integração dos serviços
```

---

## 9. Executar os testes

No terminal:

```bash
docker compose exec api pytest -v
```

Mostrar o resultado:

```text
10 passed
```

Explicar que os testes verificam autenticação, autorização, CRUD, validações e tratamento de erros.

---

## 10. Mostrar o relatório HTML

Abrir:

```text
reports/test-report.html
```

Mostrar:

```text
10 Passed
0 Failed
0 Skipped
0 Errors
```

Explicar que o relatório foi gerado com:

```text
Pytest + pytest-html
```

---

## 11. Encerramento

Finalizar destacando os principais pontos técnicos:

```text
FastAPI + Django
PostgreSQL + MongoDB
JWT + OAuth2
Repository Pattern
Docker Compose
Swagger / OpenAPI
Pytest + pytest-html
```

A aplicação demonstra a integração entre API REST, autenticação, autorização, persistência híbrida, administração, containerização, documentação e testes automatizados.