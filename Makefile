# Variables
PYTHON = python3
PIP = pip
VENV = venv
VENV_BIN = $(VENV)/bin
PROJECT = chat2dbchatbot
SRC_DIR = ./$(PROJECT)

# Default target
all: dev

# Development environment
dev: venv install dev_services
	ENV=dev $(VENV_BIN)/python -m streamlit run $(SRC_DIR)/app.py

# Create virtual environment
venv:
	$(PYTHON) -m venv $(VENV)

# Install dependencies
install: venv
	$(VENV_BIN)/pip install -r requirements.txt

# Start necessary services for development
dev_services:
	docker compose up -d postgres vecdb

# Docker targets:

# Build the Docker image
build:
	docker compose build

# Start the application
up:
	docker compose up -d

# Stop the application
down:
	docker compose down

# Run: Build and start the application
run: build up

# Rebuild and restart
restart: down
	 docker compose build --no-cache
	 docker compose up -d

# Clean up virtual environment
clean_venv:
	rm -rf $(VENV)

# Clean up Docker containers
clean_docker:
	docker compose down -v --rmi all --remove-orphans
	docker builder prune -f