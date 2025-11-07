PYTHON ?= python3
PIP ?= pip3
BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help install-backend install-frontend test-backend test-frontend lint format compose-up compose-down

help:
	@echo "Targets: install-backend install-frontend test-backend test-frontend lint format compose-up compose-down"

install-backend:
	cd $(BACKEND_DIR) && $(PIP) install -U pip && $(PIP) install -e .[dev]

install-frontend:
	cd $(FRONTEND_DIR) && pnpm install

test-backend:
	cd $(BACKEND_DIR) && pytest

test-frontend:
	cd $(FRONTEND_DIR) && pnpm test

lint:
	cd $(BACKEND_DIR) && ruff check && black --check app tests
	cd $(FRONTEND_DIR) && pnpm lint

format:
	cd $(BACKEND_DIR) && ruff check --fix && black app tests
	cd $(FRONTEND_DIR) && pnpm format

compose-up:
	docker compose up --build

compose-down:
	docker compose down -v
