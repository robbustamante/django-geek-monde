.PHONY: help install migrations run test lint format clean

help:
	@echo "Django Geek Monde - Available Commands"
	@echo "======================================"
	@grep -E '^\w+:' Makefile | awk '{print "  make " $$1}'

install:
	pip install -r requirements.txt

migrations:
	python manage.py makemigrations

migrate: migrations
	python manage.py migrate

run:
	python manage.py runserver

test:
	pytest

test-cov:
	pytest --cov=apps --cov=config --cov-report=html

lint:
	flake8 apps config email_auth
	isort --check-only apps config email_auth

format:
	isort apps config email_auth
	black apps config email_auth

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache htmlcov .coverage

superuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

static:
	python manage.py collectstatic --noinput
