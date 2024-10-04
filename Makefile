# Poetry commands
.PHONY: poetry-update
poetry-update:
	poetry update

.PHONY: install
install:
	poetry install

# Pre-commit commands
.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall && poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run --all-files

# Git commands
.PHONY: git-status
git-status:
	poetry run git status

.PHONY: git-add
git-add:
	poetry run git add .

.PHONY: git-commit
git-commit:
ifeq ($(msg),)
	$(error msg is undefined)
else
	poetry run git commit -am "$(msg)"
endif

.PHONY: git-prepare
git-prepare: git-add $(if $(msg), git-commit $(msg)) git-status

.PHONY: git-pull
git-pull:
	poetry run git pull origin master

.PHONY: git-push
git-push:
	poetry run git push origin master

.PHONY: git-force-pull
git-force-pull: git-fetch git-merge $(force="true")

.PHONY: git-fetch
git-fetch:
	poetry run git fetch origin master

.PHONY: git-merge
git-merge:
	poetry run git merge origin/master $(if $(force), --allow-unrelated-histories)

# Django commands
.PHONY: migrate
migrate:
	cd ./backend && poetry run python manage.py migrate

.PHONY: migrations
migrations:
	cd ./backend && poetry run python manage.py makemigrations

.PHONY: run-server
run-server:
	cd ./backend && poetry run python manage.py runserver 0.0.0.0:8000

.PHONY: shell
shell:
	cd ./backend && poetry run python manage.py shell

.PHONY: superuser
superuser:
	cd ./backend && poetry run python manage.py createsuperuser

.PHONY: update-db
update-db: migrations migrate

# Run before commit
.PHONY: update
update: install update-db git-add install-pre-commit pre-commit git-status ;
