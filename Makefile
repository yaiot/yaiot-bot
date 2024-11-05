run:
	@poetry run python -m src.main

lint:
	@poetry run ruff check

fmt:
	@poetry run ruff format

