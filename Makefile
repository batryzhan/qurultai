.PHONY: setup backend frontend test
setup:
	python -m venv .venv
	.venv/bin/python -m pip install -e './backend[dev]'
	cd frontend && npm ci
backend:
	.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
frontend:
	cd frontend && npm run dev
test:
	cd backend && ../.venv/bin/python -m pytest && ../.venv/bin/ruff check .
	cd frontend && npm test && npm run typecheck && npm run lint && npm run build
