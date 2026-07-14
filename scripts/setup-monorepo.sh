#!/bin/bash

# ======================
# Botcraft App Setup Script
# ======================
# This script sets up the monorepo for development

set -e

echo "🚀 Setting up Botcraft App..."

# Ensure directory structure exists
mkdir -p apps/backend
mkdir -p apps/frontend
mkdir -p packages

echo "📝 Creating environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example - please update with your values"
fi

echo "📦 Installing dependencies..."
npm install

echo "🐍 Setting up Python virtual environment..."
cd apps/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..

echo "📦 Installing frontend dependencies..."
cd apps/frontend
npm install
cd ../..

echo "✅ Monorepo setup complete!"
echo ""
echo "To start development:"
echo "  npm run dev"
echo ""
echo "Or with Docker:"
echo "  npm run docker:up"
