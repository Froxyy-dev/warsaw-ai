SHELL := /bin/bash

.PHONY: setup run-backend run-frontend run-all clean help install-req clean-database

## 📚 Help Menu
help:
	@echo "🤖 AI Call Agent - Available commands:"
	@echo "  make setup        - Install all dependencies (backend + frontend)"
	@echo "  make run-backend  - Run FastAPI backend server"
	@echo "  make run-frontend - Run React frontend"
	@echo "  make run-all      - Run both backend and frontend concurrently"
	@echo "  make clean        - Remove virtual environment and node_modules"
	@echo "  make install-req  - Install backend requirements (utility)"
	@echo "  make clean-database - Remove conversation and plan history (utility)"

## ⚙️ Setup & Dependencies
setup: install-req
	@echo "📦 Installing frontend dependencies..."
	npm install --prefix frontend
	@echo "✅ Setup complete!"

install-req:
	@echo "📦 Installing backend dependencies..."
	python3 -m venv backend/.venv
	./backend/.venv/bin/pip install -r backend/requirements.txt

## ▶️ Running Services

run-backend:
	@echo "🚀 Starting FastAPI backend..."
	# Source the venv, then execute uvicorn
	. backend/.venv/bin/activate; uvicorn main:app --app-dir backend --reload --host 0.0.0.0 --port 8000 --log-level debug

run-frontend:
	@echo "🚀 Starting React frontend..."
	npm run --prefix frontend dev

run-all:
	@echo "🚀 Starting both backend and frontend..."
	# Use `make -j 2` to run both rules in parallel
	make -j 2 run-backend run-frontend

## 🗑️ Cleanup
clean:
	@echo "🧹 Cleaning up..."
	rm -rf backend/.venv
	rm -rf frontend/node_modules
	@echo "✅ Cleanup complete!"

clean-database:
	@echo "🗑️ Cleaning up database files..."
	rm -rf backend/database/conversations/*
	rm -rf backend/database/plans/*
	@echo "✅ Database cleanup complete!"