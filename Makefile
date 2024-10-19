# Poetry
install: backend-install frontend-install
dependencies:
	poetry update && cd ./frontend && npm update
	make install
backend-install:
	poetry install

# Frontend
frontend-install:
	cd ./frontend && npm install
run-frontend:
	cd ./frontend && npm run dev -- --host 0.0.0.0 --port 3000

# Pre-commit
install-pre-commit:
	poetry run pre-commit uninstall && poetry run pre-commit install
pre-commit:
	poetry run pre-commit run --all-files

# Git (vereinfacht und mit Variablen)
GIT = poetry run git
git-status:
	$(GIT) status
git-add:
	$(GIT) add .
git-commit:
ifndef msg
	$(error msg is undefined)
endif
	$(GIT) commit -am "$(msg)"
git-prepare: git-add $(if $(msg),git-commit) git-status  # Vereinfacht
git-pull:
	$(GIT) pull origin master
git-push:
	$(GIT) push origin master
git-fetch:
	$(GIT) fetch origin master
git-merge:
	$(GIT) merge origin/master $(if $(force),--allow-unrelated-histories)
git-force-pull: git-fetch git-merge $(force="true") # force als Parameter


# Django
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
update: update-db git-add install-pre-commit pre-commit git-status

.PHONY: install dependencies backend-install frontend-install run-frontend install-pre-commit pre-commit \
        git-status git-add git-commit git-prepare git-pull git-push git-force-pull git-fetch git-merge \
        migrate migrations collectstatic run-backend shell createsuperuser update-db update
