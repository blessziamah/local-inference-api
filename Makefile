.PHONY: help build up down restart logs logs-api ps clean shell-api health test

# Default target
help:
	@echo "BLACKSTAR-AI Docker Management"
	@echo ""
	@echo "Available commands:"
	@echo "  make build        - Build Docker images"
	@echo "  make up           - Start API service"
	@echo "  make down         - Stop API service"
	@echo "  make restart      - Restart API service"
	@echo "  make logs         - View logs from API service"
	@echo "  make logs-api     - View API logs"
	@echo "  make ps           - Show service status"
	@echo "  make clean        - Remove containers and images"
	@echo "  make shell-api    - Open shell in API container"
	@echo "  make health       - Check health of API and host services"
	@echo "  make test         - Run test HTTP requests"
	@echo ""
	@echo "Note: MongoDB and Ollama should be running on the host machine"

# Build Docker images
build:
	docker-compose build

# Start API service in detached mode
up:
	docker-compose up -d
	@echo "API service started. Available at http://localhost:8000"
	@echo "API docs available at http://localhost:8000/docs"
	@echo ""
	@echo "Ensure MongoDB and Ollama are running on the host:"
	@echo "  - MongoDB: mongodb://localhost:27017"
	@echo "  - Ollama: http://localhost:11434"

# Stop API service
down:
	docker-compose down

# Restart API service
restart:
	docker-compose restart

# View logs from API service
logs:
	docker-compose logs -f

# View API logs
logs-api:
	docker-compose logs -f api

# Show service status
ps:
	docker-compose ps

# Clean up everything (containers and images)
clean:
	@echo "Warning: This will remove API container and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down --rmi all; \
		echo "Cleanup complete!"; \
	fi

# Open shell in API container
shell-api:
	docker-compose exec api /bin/sh

# Check health of API and host services
health:
	@echo "Checking API health..."
	@curl -s http://localhost:8000/ > /dev/null && echo "✓ API is healthy" || echo "✗ API not responding"
	@echo ""
	@echo "Checking host MongoDB..."
	@mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1 && echo "✓ MongoDB is healthy" || echo "✗ MongoDB not responding (ensure it's running on host)"
	@echo ""
	@echo "Checking host Ollama..."
	@curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama is healthy" || echo "✗ Ollama not responding (ensure it's running on host)"

# Run test HTTP requests (if httpie is installed)
test:
	@command -v http >/dev/null 2>&1 || { echo "HTTPie not installed. Install with: pip install httpie"; exit 1; }
	@echo "Testing health endpoint..."
	http GET http://localhost:8000/
