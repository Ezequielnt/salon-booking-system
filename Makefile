.PHONY: help up down logs build makemigrations migrate seed shell dbshell test lint front-install

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up:  ## Levanta todo el stack
	docker compose up

build:  ## Reconstruye las imágenes
	docker compose build

down:  ## Baja el stack (conserva la base de datos)
	docker compose down

down-v:  ## Baja el stack y BORRA la base de datos
	docker compose down -v

logs:  ## Sigue los logs de todos los servicios
	docker compose logs -f

makemigrations:  ## Genera migraciones a partir de los modelos
	docker compose run --rm backend python manage.py makemigrations

migrate:  ## Aplica migraciones
	docker compose run --rm backend python manage.py migrate

seed:  ## Recarga los datos de demo
	docker compose run --rm backend python manage.py seed_demo

shell:  ## Shell de Django (shell_plus)
	docker compose run --rm backend python manage.py shell_plus

dbshell:  ## Consola psql
	docker compose exec db psql -U salon -d salon

test:  ## Corre los tests
	docker compose run --rm backend pytest

lint:  ## Linter (ruff)
	docker compose run --rm backend ruff check .

front-install:  ## Reinstala dependencias del frontend en el contenedor
	docker compose run --rm frontend npm install
