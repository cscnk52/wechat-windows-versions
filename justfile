check:
    uv run python -m src.checker

process:
    uv run python -m src.processor

run:
    uv run python -m src.processor

install:
    uv sync

fmt:
    uv run ruff format src/

lint:
    uv run ruff check src/
