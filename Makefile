# Makefile for globomap-core-loader

# Pip executable path
PIP := $(shell which pip)

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean      to clean garbage left by builds and installation"
	@echo "  compile    to compile .py files (just to check for syntax errors)"
	@echo "  test       to execute all tests"
	@echo "  run        to run the loader app"
	@echo "  run_api    to run the loader api app"
	@echo

clean:
	@echo "Cleaning project ..."
	@rm -rf build dist *.egg-info
	@find . \( -name '*.pyc' -o -name '**/*.pyc' -o -name '*~' \) -delete

compile: clean
	@echo "Compiling source code..."
	@python -tt -m compileall .
	@pep8 --format=pylint --statistics loader driver api

tests: clean compile
	@python -m unittest discover -s tests/

setup: requirements.txt
	$(PIP) install -r $^

run:
	@python run.py

run_load:
	@python run_load.py

run_api:
	@python run_api.py