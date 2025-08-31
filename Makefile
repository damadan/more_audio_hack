.PHONY: run-server logs run-gpu test-offline lint types tests

run-server: ## docker cpu
	docker compose up -d --build

logs:
	docker compose logs -f

run-gpu: ## docker gpu
	docker compose --compatibility up -d --build

test-offline:
	python client_offline_test.py --ws ws://localhost:8000 --wav ru_test.wav

lint:
	ruff check .

types:
	mypy .

tests:
	pytest -q
