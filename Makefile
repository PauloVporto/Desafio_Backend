up:
	docker compose up

build:
	docker compose up --build

down:
	docker compose down

test:
	docker compose exec api pytest -v

logs:
	docker compose logs -f api
