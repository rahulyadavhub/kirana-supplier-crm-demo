# Kirana Supplier CRM - Makefile
.PHONY: help install dev run build clean test docker-build docker-run

help: ## Show this help message
	@echo "Kirana Supplier CRM - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

dev: ## Run development server
	python3 dev-server.py

run: ## Run production server
	python3 run.py

build: ## Build Docker image
	docker build -t kirana-crm .

docker-run: ## Run with Docker Compose
	docker-compose up --build

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -f dev-server.log
	rm -f kirana.db

test: ## Run unit tests and health check
	@echo "Running pytest..."
	@pytest -q
	@echo "Testing backend health..."
	@curl -s http://localhost:5000/health | jq . || echo "Backend not running"
	@echo "Testing frontend..."
	@curl -s http://localhost:8000 | grep -q "<title>" && echo "Frontend OK" || echo "Frontend not running"

db-reset: ## Reset database to initial state
	curl -X POST http://localhost:5000/api/debug/db-reset

logs: ## Show dev server logs
	tail -f dev-server.log