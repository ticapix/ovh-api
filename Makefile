ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON3=python3
VENV_DIR=$(ROOT_DIR)/venv3
NAME=$(shell basename $(ROOT_DIR))
ECHO=@echo
RM=rm -rf

.PHONY: help

help:
	$(ECHO) "$(NAME)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m=> %s\n", $$1, $$2}'

$(VENV_DIR):
	$(PYTHON3) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -Ur requirements.txt

install: $(VENV_DIR) ## install dependencies

run: install ## local service excusion
	$(VENV_DIR)/bin/python ./run.py

lint: install ## run flake8 and mypy
	$(VENV_DIR)/bin/flake8

test: install ## run test and list outdated packages
	ASYNC_TEST_TIMEOUT=20 $(VENV_DIR)/bin/python -m tornado.testing tests
	$(VENV_DIR)/bin/pip list --outdated

clean: ## remove generated files
	$(RM) $(VENV_DIR)
