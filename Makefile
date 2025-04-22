.PHONY: up down logs makemigrations migrate shell lint format runserver runserver-local freeze test

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

makemigrations:
	docker compose exec web python manage.py makemigrations

migrate:
	docker compose exec web python manage.py migrate

shell:
	docker compose exec web python manage.py shell

lint:
	flake8 ecom

format:
	black . && isort .

runserver:
	docker compose exec web python manage.py runserver 0.0.0.0:8000

runserver-local:
	python manage.py runserver

freeze:
	pip freeze > requirements.txt

test: up
	docker compose exec web python manage.py makemigrations
	docker compose exec web python manage.py migrate --noinput
	docker compose exec web python manage.py test
