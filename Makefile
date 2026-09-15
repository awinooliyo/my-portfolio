.PHONY: install dev migrate superuser seed collectstatic shell

install:
	uv sync

dev:
	uv run python manage.py runserver 8002

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

superuser:
	uv run python manage.py createsuperuser

seed:
	uv run python manage.py loaddata portfolio/fixtures/initial_data.json

collectstatic:
	DJANGO_SETTINGS_MODULE=config.settings.prod \
	uv run python manage.py collectstatic --noinput

shell:
	uv run python manage.py shell

setup: install migrate seed superuser
	@echo "✓ Portfolio ready — run 'make dev' to start"
