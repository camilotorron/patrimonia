.PHONY: help install dev run test lint format check migrate seed setup import backup docker-build docker-up docker-down deploy

help: ## Mostrar ayuda
	@echo "Patrimonia — Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias con Poetry
	poetry install

dev: ## Instalar dependencias de desarrollo
	poetry install --with dev

run: ## Levantar servidor de desarrollo
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Ejecutar tests con cobertura
	cd backend && poetry run pytest tests/ -v --cov=app --cov-report=term-missing

lint: ## Lint con ruff
	poetry run ruff check backend/app backend/tests

format: ## Formatear código con ruff
	poetry run ruff format backend/app backend/tests
	poetry run ruff check --fix backend/app backend/tests

check: ## Verificar formato y lint sin modificar
	poetry run ruff format --check backend/app backend/tests
	poetry run ruff check backend/app backend/tests

migrate: ## Crear tablas en la base de datos
	PYTHONPATH=backend poetry run python -m scripts.init_db

seed: ## Wizard interactivo: registrar tu patrimonio real (cuentas, saldos, activos, ganancias)
	PYTHONPATH=backend poetry run python -m scripts.seed_data

import: ## Importar datos iniciales desde init_data/*.json (borra y recrea la BD)
	PYTHONPATH=backend poetry run python -m scripts.import_initial_data

setup: ## Configuración inicial completa: crear BD + importar datos desde JSON
	PYTHONPATH=backend poetry run python -m scripts.import_initial_data

backup: ## Backup de la base de datos
	PYTHONPATH=backend poetry run python -m scripts.backup

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Levantar contenedores
	docker-compose up -d

docker-down: ## Detener contenedores
	docker-compose down

docker-logs: ## Ver logs
	docker-compose logs -f

deploy: ## Desplegar en producción (placeholder)
	@echo "Deploy no implementado. Ver docs/DEPLOYMENT.md"
