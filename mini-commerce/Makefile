.PHONY: up down logs test backend-test mcp-test validate clean backup
up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose --profile app up -d --build

down:
	docker compose --profile app --profile observability down

logs:
	docker compose logs -f backend

test: backend-test mcp-test validate

backend-test:
	cd backend && mvn -B verify

mcp-test:
	cd mcp-server && python -m pytest -q

validate:
	python3 tools/check_learning_references.py
	docker compose config >/dev/null

backup:
	./scripts/backup.sh

clean:
	docker compose --profile app --profile observability down -v
