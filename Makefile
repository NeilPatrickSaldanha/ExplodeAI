.PHONY: setup dev backend frontend test test-backend test-frontend e2e validate lint build docker-up docker-down

setup:            ## install backend (with local neural embedder) and frontend deps
	cd backend && uv sync --extra neural
	cd frontend && npm ci && npx playwright install chromium

dev:              ## run backend and frontend together (Ctrl-C stops both)
	$(MAKE) -j2 backend frontend

backend:
	cd backend && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

validate:         ## content gate: citations, sources, verification passes
	cd backend && uv run python scripts/validate_content.py

test: validate test-backend test-frontend e2e

test-backend:
	cd backend && uv run pytest

test-frontend:
	cd frontend && npm run typecheck && npm test

e2e:
	cd frontend && npm run test:e2e

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
