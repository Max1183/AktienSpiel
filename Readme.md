# Aktien Spiel

Dieses Projekt ist ein Spiel, bei dem die Teilnehmer Aktien kaufen und zu verkaufen können, um Gewinne zu erzielen.

## Inhaltsverzeichnis

- [Features](#features)
- [Installation](#installation)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Verwendung](#verwendung)
- [Tests](#tests)
  - [Backend](#backend-tests)
  - [Frontend](#frontend-tests)
- [Git-Workflow](#git-workflow)
- [Lizenz](#lizenz)
- [Deployment](#deployment)

## Features

- Die Aktienkurse werden jede Stunde aktualisiert.
- Der Admin kann Spieler über ihre E-Mail-Adresse einladen.
- Man spielt im Team mit bis zu 4 Spielern.
- Spieler können Aktien kaufen und verkaufen.
- Es gibt eine Depotübersicht mit den aktuellen Werten und dem Verlauf.
- Alle Transaktionen können angesehen werden und es können Notizen hinzugefügt werden.
- Es gibt eine Auswertung für die Gewinne der einzelnen Aktien.
- Es gibt eine Watchlist für die Aktien, die der Spieler beobachten möchte.
- Es gibt eine Rangliste, die die Spieler nach ihrem Gewinn sortiert.

## Installation

### Backend

1. Klone das Repository: `git clone https://github.com/Max1183/AktienSpiel.git`
2. Navigiere in den Backend-Ordner: `cd backend`
3. Erstelle eine virtuelle Umgebung mit Poetry: `poetry shell`
4. Installiere die Abhängigkeiten: `poetry install`
5. Kopiere die `.env.example` Datei: `cp .env.example .env`
6. Fülle die `.env` Datei mit deinen Datenbankzugangsdaten und anderen notwendigen Umgebungsvariablen.
7. Führe die Migrationen aus: `poetry run python manage.py migrate`
8. Erstelle einen Superuser: `poetry run python manage.py createsuperuser`
9. Starte den Entwicklungsserver: `poetry run python manage.py runserver`

### Frontend

1. Navigiere in den Frontend-Ordner: `cd frontend`
2. Installiere die Abhängigkeiten: `npm install`
3. Starte den Entwicklungsserver: `npm run dev`

## Verwendung

1. Öffne den Browser und navigiere zur URL, auf der der Entwicklungsserver läuft: http://localhost:3000.
2. Das Backend ist unter http://localhost:8000 erreichbar.
3. Im Frontend kann der Admin über /admin/ weitere Spieler einladen.

## Tests

### Backend Tests

1. Navigiere in den Backend-Ordner: `cd backend`
2. Führe die Tests aus: `poetry run python manage.py test`

### Frontend Tests

1. Navigiere in den Frontend-Ordner: `cd frontend`
2. Führe die Tests aus: `npm run test`

## Git Workflow

1. Wechsle zum Develop-Branch: `git checkout develop`
2. Stelle sicher, dass dein Develop-Branch auf dem aktuellen Stand ist: `git pull origin develop`
3. Erstelle einen neuen Feature Branch für deine Änderungen: `git checkout -b feature/new-feature`
4. Nimm Änderungen vor und füge sie zu git hinzu: `git add .`
5. Commite deine Änderungen: `git commit -m "Beschreibung der Änderungen"`
6. Wechsle zum Development Branch: `git checkout develop`
7. Stelle sicher, dass dein Develop-Branch auf dem aktuellen Stand ist: `git pull origin develop`
8. Führe einen Merge aus: `git merge feature/new-feature`
9. Lösche den Branch, wenn er nicht mehr benötigt wird: `git branch -d feature/new-feature`
10. Pushe deine Änderungen: `git push origin develop`
11. Erstelle einen Pull Request von `develop` nach `main` auf GitHub.
12. Nach erfolgreichem Review und Tests wird der Pull Request auf Github in den main-Branch gemerged.
13. Aktualisiere deinen lokalen main-Branch: `git checkout master` & `git pull origin master`

## Contributing

Wenn du einen Fehler findest oder Verbesserungsvorschläge hast, erstelle bitte ein Issue oder einen Pull Request.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## Deployment

1. Dependencies in `requirement.txt` exportieren `poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev`
2. Docker-Image erstellen `docker build -t backend .`
3. Docker Container starten `docker run -p 8000:8000 -e PORT=8000 backend`
4. Frontend build testen: `npm run build`
