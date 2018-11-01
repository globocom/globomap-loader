# Makefile for globomap-loader

# Pip executable path
PIP := $(shell which pip)

PROJECT_HOME = "`pwd`"

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo

	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Install project dependencies
	@pip install -r $(PROJECT_HOME)/requirements_test.txt

clean: ## Clear *.pyc files, etc
	@echo "Cleaning project ..."
	@rm -rf build dist *.egg-info
	@find . \( -name '*.pyc' -o  -name '__pycache__' -o -name '**/*.pyc' -o -name '*~' \) -delete

compile: clean ## Compile source code
	@echo "Compiling source code..."
	@python3.6 -tt -m compileall globomap_loader
	@pycodestyle --format=pylint --statistics globomap_loader

tests: clean ## Run tests
	@echo "Running tests..."
	@export ENV=test
	@nosetests --verbose --rednose  --nocapture --cover-package=globomap_loader --with-coverage

tests_ci: clean ## Make tests to CI
	@echo "Running tests..."
	@export ENV=test
	@nosetests --verbose --rednose  --nocapture --cover-package=globomap_loader

run:  ## Run the loader
	@echo "Running loader..."
	@PYTHONPATH=`pwd`:$PYTHONPATH python globomap_loader/run_loader.py

run_scheduler_tasks: ## Run the reset loader app
	@echo "Running reset loader..."
	@PYTHONPATH=`pwd`:$PYTHONPATH python globomap_loader/scheduler_tasks.py

containers_start:## Start containers
	docker-compose up -d

containers_build: ## Build containers
	docker-compose build --no-cache

containers_stop: ## Stop containers
	docker-compose stop

containers_clean: ## Destroy containers
	docker-compose rm -s -v -f
