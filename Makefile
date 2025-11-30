SHELL := /bin/bash

.PHONY: setup run-backend run-frontend run-all clean help

help:
	@echo "AI Call Agent - Available commands:"
	@echo "  make setup        - Install all dependencies (backend + frontend)"
	@echo "  make run-backend  - Run FastAPI backend server"
	@echo "  make run-frontend - Run React frontend"
	@echo "  make run-all      - Run both backend and frontend"
	@echo "  make clean        - Remove virtual environment and node_modules"

setup:
	@echo "📦 Installing backend dependencies..."
	cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Setup complete!"

run-backend:
	@echo "🚀 Starting FastAPI backend..."
	cd backend && source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

run-frontend:
	@echo "🚀 Starting React frontend..."
	cd frontend && npm run dev

run-all:
	@echo "🚀 Starting both backend and frontend..."
	make -j 2 run-backend run-frontend

clean:
	@echo "🧹 Cleaning up..."
	rm -rf backend/.venv
	rm -rf frontend/node_modules
	@echo "✅ Cleanup complete!"

install-req:
	pip install -r backend/requirements.txt

clean-database:
	rm -rf backend/database/conversations/*
	rm -rf backend/database/plans/*