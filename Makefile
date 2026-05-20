.PHONY: check test lint

check: lint test

test:
	uv run pytest -q

lint:
	uv run ruff check && uv run mypy afspec/
