.PHONY: install train serve test lint web demo
install:
	python -m pip install -r requirements-lock.txt
	python -m pip install --no-deps -e .
train:
	python -m signalforge train
	python -m signalforge promote
serve:
	alembic upgrade head
	uvicorn signalforge.api:app --host 127.0.0.1 --port 8000
test:
	pytest --cov=signalforge
lint:
	ruff check .
	ruff format --check .
web:
	cd apps/web && npm ci && npm run dev
demo:
	python scripts/seed_demo.py
