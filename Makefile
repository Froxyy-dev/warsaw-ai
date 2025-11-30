SHELL := /bin/bash

# Define relative paths for clarity
BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV := $(BACKEND_DIR)/.venv

.PHONY: setup run-backend run-frontend run-all clean help install-req clean-database

help:
	@echo "AI Call Agent - Available commands:"
	@echo "  make setup          - Install all dependencies (backend + frontend)"
	@echo "  make run-backend    - Run FastAPI backend server"
	@echo "  make run-frontend   - Run React frontend"
	@echo "  make run-all        - Run both backend and frontend"
	@echo "  make clean          - Remove virtual environment and node_modules"
	@echo "  make install-req    - Install backend dependencies (uses full path)"
	@echo "  make clean-database - Remove conversation and plan data"

---

## ⚙️ Setup Targets

# The setup target still needs to use 'cd' or subshells for venv creation/activation
# and npm install, as they depend on the current directory.
setup:
	@echo "📦 Installing backend dependencies..."
	python3 -m venv $(VENV)
	# Use a sub-shell to activate the venv and install requirements
	( source $(VENV)/bin/activate && pip install -r $(BACKEND_DIR)/requirements.txt )
	@echo "📦 Installing frontend dependencies..."
	npm --prefix $(FRONTEND_DIR) install
	@echo "✅ Setup complete!"

install-req:
	@echo "📦 Installing backend dependencies..."
	# Use a sub-shell to activate the venv and install requirements
	( source $(VENV)/bin/activate && pip install -r $(BACKEND_DIR)/requirements.txt )
	@echo "✅ Requirements installed!"

---

## 🚀 Run Targets

# The run-backend target MUST activate the virtual environment for
# 'uvicorn' to be found and for dependencies to be correct.
# Using a sub-shell '()' is the cleanest way to do this without 'cd'.
run-backend:
	@echo "🚀 Starting FastAPI backend..."
	( source $(VENV)/bin/activate && uvicorn $(BACKEND_DIR)/main:app --reload --host 0.0.0.0 --port 8000 --log-level debug )

# 'npm run dev' can often be run from the parent directory using '--prefix'.
run-frontend:
	@echo "🚀 Starting React frontend..."
	npm --prefix $(FRONTEND_DIR) run dev

# Uses parallel execution for the run targets defined above.
run-all:
	@echo "🚀 Starting both backend and frontend..."
	make -j 2 run-backend run-frontend

---

## 🧹 Clean Targets

# Files can be removed directly with relative paths.
clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV)
	rm -rf $(FRONTEND_DIR)/node_modules
	@echo "✅ Cleanup complete!"

clean-database:
	@echo "🗑️ Cleaning up database files..."
	rm -f $(BACKEND_DIR)/database/conversations/*
	rm -f $(BACKEND_DIR)/database/plans/*
	@echo "✅ Database cleanup complete!"