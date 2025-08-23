.PHONY: run test lint build

run:
        uvicorn main:app --host 0.0.0.0 --port 8080

test:
	pytest

lint:
	flake8 .

build:
	docker build -t app .
