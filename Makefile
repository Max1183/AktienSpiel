# Dependencies
POETRY = cd .\backend\ && poetry
NPM = cd .\frontend\ && npm

install: backend-install frontend-install
dependencies: backend-dependencies frontend-dependencies install
backend-install:
	$(POETRY) install
frontend-install:
	$(NPM) install
backend-dependencies:
	$(POETRY) update
frontend-dependencies:
	$(NPM) update

# Frontend (React/npm)
run-frontend:
	$(NPM) run dev -- --host 0.0.0.0 --port 3000

# Backend (Django)
MANAGE = $(POETRY) run python manage.py
run-stocks:
	$(MANAGE) update_stocks
migrate:
	$(MANAGE) migrate
migrations:
	$(MANAGE) makemigrations
collectstatic:
	$(MANAGE) collectstatic --noinput
test:
	$(MANAGE) test
run-backend:
	$(MANAGE) runserver 0.0.0.0:8000
shell:
	$(MANAGE) shell
createsuperuser:
	$(MANAGE) createsuperuser
update-db: migrations migrate

# Pre-commit
install-pre-commit:
	$(POETRY) run pre-commit uninstall && $(POETRY) run pre-commit install
pre-commit:
	$(POETRY) run pre-commit run --all-files

# Kombinierte Befehle
update: test install-pre-commit pre-commit install update-db collectstatic

.PHONY: install dependencies backend-install frontend-install backend-dependencies frontend-dependencies \
		run-frontend migrate migrations collectstatic test run-backend shell createsuperuser update-db \
		install-pre-commit pre-commit update
