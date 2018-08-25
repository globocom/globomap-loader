# Makefile for globomap-core-loader

# Pip executable path
PIP := $(shell which pip)

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo

	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clear *.pyc files, etc
	@echo "Cleaning project ..."
	@rm -rf build dist *.egg-info
	@find . \( -name '*.pyc' -o  -name '__pycache__' -o -name '**/*.pyc' -o -name '*~' \) -delete

compile: clean ## Compile source code
	@echo "Compiling source code..."
	@python3.6 -tt -m compileall globomap_loader_api
	@pycodestyle --format=pylint --statistics globomap_loader_api

tests: clean ## Run tests
	@echo "Running tests..."
	@export ENV=test
	@nosetests --verbose --rednose  --nocapture --cover-package=globomap_loader_api --with-coverage

tests_ci: clean ## Make tests to CI
	@echo "Running tests..."
	@export ENV=test
	@nosetests --verbose --rednose  --nocapture --cover-package=globomap_loader_api

run_version_control: ## Run version control
	@echo "Running version control..."
	@python3.6 migrations/manage.py version_control || true

run_migrations: run_version_control ## Run migrations
	@echo "Running migrations..."
	@python3.6 migrations/manage.py upgrade

run_loader: run_migrations ## Run the loader
	@echo "Running loader..."
	@python3.6 scripts/run_loader.py $(module)

run_reset_loader: ## Run the reset loader app
	@echo "Running reset loader..."
	@python3.6 scripts/run_reset_loader.py

containers_start:## Start containers
	docker-compose up -d

containers_build: ## Build containers
	docker-compose build --no-cache

containers_stop: ## Stop containers
	docker-compose stop

containers_clean: ## Destroy containers
	docker-compose rm -s -v -f
