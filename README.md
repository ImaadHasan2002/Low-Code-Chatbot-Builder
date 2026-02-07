# Botcraft

A full-stack AI chatbot platform with FastAPI backend and Next.js frontend.

> 📚 **See [MONOREPO_README.md](MONOREPO_README.md) for full documentation**

## Quick Start

```bash
# Install dependencies
npm run install:all

# Start development (both frontend & backend)
npm run dev

# Or with Docker
docker-compose up -d
```

## Project Structure

```
botcraft/
├── apps/
│   ├── backend/    # FastAPI Python backend
│   └── frontend/   # Next.js React frontend
├── packages/       # Shared packages
├── docker-compose.yml
├── package.json
└── Makefile
```
