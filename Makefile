# Define variables
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
ANSIBLE_LINT := $(VENV_DIR)/bin/ansible-lint
PYTEST := $(VENV_DIR)/bin/pytest
BLACK := $(VENV_DIR)/bin/black
FLAKE8 := $(VENV_DIR)/bin/flake8
MODULE_NAME := my_ansible_module

# Default target
all: install

# Create virtual environment
$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

# Install dependencies
install: $(VENV_DIR)
	$(PIP) install -r requirements.txt
	$(PIP) install -r test-requirements.txt

# Run tests
test: $(VENV_DIR)
	$(PYTEST) tests/

# Lint code
lint: $(VENV_DIR)
	$(FLAKE8) $(MODULE_NAME) tests/
	$(BLACK) --check $(MODULE_NAME) tests/

# Format code
format: $(VENV_DIR)
	$(BLACK) $(MODULE_NAME) tests/

# Run Ansible lint
ansible-lint: $(VENV_DIR)
	$(ANSIBLE_LINT) .

# Clean up
clean:
	rm -rf $(VENV_DIR) .pytest_cache .mypy_cache

.PHONY: all install test lint format ansible-lint clean
