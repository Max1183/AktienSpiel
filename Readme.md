# Aktien Spiel

Dieses Projekt ist ein Spiel, bei dem die Spieler Aktien kaufen und zu verkaufen können, um Gewinne zu erzielen.

## Inhaltsverzeichnis

- [Features](#features)
- [Regeln](#regeln)
- [Installation](#installation)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Verwendung](#verwendung)
- [Tests](#tests)
  - [Backend](#backend-tests)
  - [Frontend](#frontend-tests)

## Features

- Spieler können Aktien kaufen und verkaufen.
- Spieler können ihre Gewinne und Verluste verfolgen.
- Spieler können ihre Strategien anpassen, um Gewinne zu erzielen.

## Regeln

Jeder, der die Zusammenarbeit behindert, wird mit sofortiger Wirkung aus dem Projekt entfernt.

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

1. Öffne den Browser und navigiere zur URL, auf der der Entwicklungsserver läuft (z.B. http://localhost:3000).
2. Melde dich mit deinen Anmeldedaten an.

## Tests

### Backend Tests

1. Navigiere in den Backend-Ordner: `cd backend`
2. Führe die Tests aus: `poetry run python manage.py test`

### Frontend Tests

1. Navigiere in den Frontend-Ordner: `cd frontend`
2. Führe die Tests aus: `npm run test`
