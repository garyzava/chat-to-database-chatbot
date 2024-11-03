# Variables
PYTHON = python3
PIP = pip
VENV = venv
VENV_BIN = $(VENV)/bin
PROJECT = chat2dbchatbot
SRC_DIR = ./$(PROJECT)

# Default target
all: venv install

# Create virtual environment
venv:
	$(PYTHON) -m venv $(VENV)

# Install dependencies
install: venv
	$(VENV_BIN)/pip install -r requirements.txt

# Docker targets
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
restart: down build up

# Clean up virtual environment
clean_venv:
	rm -rf $(VENV)

# Clean up Docker containers
clean_docker:
	docker compose down -v --rmi all --remove-orphans