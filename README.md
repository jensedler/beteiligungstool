# Beteiligungstool

Webanwendung der Stadt Bielefeld zur Erfassung und Aufbereitung von Beteiligungskonzepten. Fachaemter füllen einen strukturierten Fragebogen aus; ein KI-Dienst (OpenAI GPT-4o) generiert daraus einen Entwurf für ein Beteiligungskonzept, den das Team Dialog & Beteiligung prüft und kommentiert.

## Technologie

- **Backend:** Python 3.11, Flask 3.1
- **Datenbank:** SQLite (persistent in `/storage`)
- **KI:** OpenAI GPT-4o
- **Server:** Gunicorn, Port 80
- **Container:** Docker

## Lokale Entwicklung

### Voraussetzungen

- Python 3.11+
- pip

### Setup

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env anpassen: SECRET_KEY, OPENAI_API_KEY, ggf. DATABASE_URL

# Datenbank initialisieren und Beispieldaten anlegen
python seed_questions.py

# Entwicklungsserver starten
flask run
```

Die App ist dann unter `http://localhost:5000` erreichbar.

### Umgebungsvariablen (lokal)

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `SECRET_KEY` | ja | Flask-Session-Schlüssel |
| `OPENAI_API_KEY` | ja | OpenAI API-Key |
| `DATABASE_URL` | nein | SQLAlchemy-Verbindung (Default: `sqlite:///instance/beteiligungstool.db`) |
| `OPENAI_MODEL` | nein | Zu verwendendes Modell (Default: `gpt-4o`) |

## Deployment via Once

Siehe [deploy/README.md](deploy/README.md).
