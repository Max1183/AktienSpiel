# Poetry
install: backend-install frontend-install
dependencies:
	poetry update && cd ./frontend && npm update
	make install
backend-install:
	poetry install

# Frontend (React/npm)
frontend-install:
	cd ./frontend && npm install
run-frontend:
	cd ./frontend && npm run dev -- --host 0.0.0.0 --port 3000

# Pre-commit
install-pre-commit:
	poetry run pre-commit uninstall && poetry run pre-commit install
pre-commit:
	poetry run pre-commit run --all-files

# Backend (Django)
MANAGE = cd ./backend && poetry run python manage.py
migrate:
	$(MANAGE) migrate
migrations:
	$(MANAGE) makemigrations
collectstatic:
	$(MANAGE) collectstatic --noinput
run-backend:
	$(MANAGE) runserver 0.0.0.0:8000
shell:
	$(MANAGE) shell
createsuperuser:
	$(MANAGE) createsuperuser
update-db: migrations migrate

# Kombinierte Befehle
update: update-db collectstatic install-pre-commit pre-commit

.PHONY: install dependencies backend-install frontend-install run-frontend install-pre-commit pre-commit \
        git-status git-add git-commit git-prepare git-pull git-push git-force-pull git-fetch git-merge \
        migrate migrations collectstatic run-backend shell createsuperuser update-db update
