# Makefile for Botcraft Monorepo
# ======================

.PHONY: help install dev build start stop test lint clean docker-up docker-down

# Default target
help:
	@echo "Botcraft App Commands:"
	@echo ""
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make build        - Build for production"
	@echo "  make start        - Start production servers"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo ""

# Install all dependencies
install:
	@echo "📦 Installing Node.js dependencies..."
	npm install
	@echo "📦 Installing frontend dependencies..."
	cd apps/frontend && npm install
	@echo "🐍 Installing Python dependencies..."
	cd apps/backend && pip install -r requirements.txt
	@echo "✅ All dependencies installed!"

# Development mode
dev:
	@echo "🚀 Starting development servers..."
	npm run dev

dev-backend:
	@echo "🐍 Starting backend server..."
	npm run dev:backend

dev-frontend:
	@echo "⚛️  Starting frontend server..."
	npm run dev:frontend

# Build for production
build:
	@echo "🏗️  Building frontend..."
	npm run build:frontend

# Start production
start:
	npm run start

# Run tests
test:
	@echo "🧪 Running backend tests..."
	cd apps/backend && pytest -v

test-coverage:
	cd apps/backend && pytest --cov=app --cov-report=html

# Linting
lint:
	@echo "🔍 Linting frontend..."
	npm run lint:frontend

lint-backend:
	cd apps/backend && python -m flake8 app/

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf node_modules
	rm -rf apps/frontend/node_modules
	rm -rf apps/frontend/.next
	rm -rf apps/backend/__pycache__
	rm -rf apps/backend/app/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete!"

# Docker commands
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

# Database commands
db-shell:
	docker-compose exec mongodb mongosh

# Redis commands
redis-cli:
	docker-compose exec redis redis-cli

# Setup monorepo structure
setup:
	chmod +x scripts/setup-monorepo.sh
	./scripts/setup-monorepo.sh
