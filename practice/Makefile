SHELL := /bin/bash
DB_URL ?= postgresql://commerce:commerce-local@localhost:15432/commerce

.PHONY: up down reset ps logs schema seed million explain backup restore

up:
	docker compose up -d postgres redis rabbitmq

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d postgres redis rabbitmq

ps:
	docker compose ps

logs:
	docker compose logs -f

schema:
	psql "$(DB_URL)" -f sql/01_schema.sql

seed:
	psql "$(DB_URL)" -f sql/02_seed.sql

million:
	psql "$(DB_URL)" -v order_count=1000000 -f sql/03_generate_orders.sql

explain:
	psql "$(DB_URL)" -f sql/04_index_lab.sql

backup:
	mkdir -p backups
	pg_dump -Fc "$(DB_URL)" -f backups/commerce.dump

restore:
	@echo "Create a new database and run: pg_restore -d <url> backups/commerce.dump"
