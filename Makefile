.PHONY: up down logs api-test web-lint

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

api-test:
	docker compose run --rm api pytest -q

web-lint:
	docker compose run --rm web npm run lint
