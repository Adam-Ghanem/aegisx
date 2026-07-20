.PHONY: setup test lint format format-check typecheck security build start stop logs validate
setup:
	python -m pip install -e '.[dev]'
	python -m pre_commit install
test:
	python -m pytest
lint:
	python -m ruff check .
format:
	python -m ruff format .
	python -m ruff check --fix .
format-check:
	python -m ruff format --check .
	python -m ruff check .
typecheck:
	python -m mypy apps/api/src
security:
	python -m bandit -c pyproject.toml -r apps/api/src
	python -m pip_audit
build:
	python -m build
	docker compose build
start:
	docker compose up --detach --build --wait
stop:
	docker compose down
logs:
	docker compose logs --follow
validate: format-check typecheck test
	python -m bandit -c pyproject.toml -r apps/api/src
	docker compose config --quiet
