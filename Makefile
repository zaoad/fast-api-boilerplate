.PHONY: help build up down logs shell test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start services"
	@echo "  down      - Stop services"
	@echo "  logs      - Show logs"
	@echo "  shell     - Access application shell"
	@echo "  test      - Run tests"
	@echo "  clean     - Clean up containers and volumes"
	@echo "  migration - Create new migration"
	@echo "  migrate   - Run migrations"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Access application shell
shell:
	docker-compose exec web bash

# Run tests
test:
	docker-compose exec web pytest

# Clean up containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Create new migration
migration:
	docker-compose exec web alembic revision --autogenerate -m "$(name)"

# Run migrations
migrate:
	docker-compose exec web alembic upgrade head

# Restart services
restart: down up

# Development setup (build and start)
dev: build up logs 