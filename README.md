# Beteiligungstool

Webanwendung der Stadt Bielefeld zur Erfassung und Aufbereitung von Beteiligungskonzepten. Fachaemter füllen einen strukturierten Fragebogen aus; ein KI-Dienst generiert daraus einen Entwurf für ein Beteiligungskonzept, den das Team Dialog & Beteiligung prüft und kommentiert.

Admins können in der **Wissensdatenbank** Referenzmaterial hinterlegen (Leitlinien, Methodenkatalog, rechtliche Rahmenbedingungen), das bei jeder KI-Generierung automatisch in den System-Prompt eingebettet wird.

## Technologie

- **Backend:** Python 3.11, Flask 3.1
- **Datenbank:** SQLite (persistent in `/storage`)
- **KI:** OpenAI-kompatible API (konfigurierbar, z. B. OpenRouter)
- **Server:** Gunicorn, Port 80
- **Container:** Docker

## Lokale Entwicklung

### Voraussetzungen

- Python 3.11+

### Setup

```bash
# Virtualenv erstellen und Abhängigkeiten installieren
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env anpassen: SECRET_KEY, OPENAI_API_KEY, ggf. DATABASE_URL

# Datenbank initialisieren und Migrationsstatus aktualisieren
python seed_questions.py
flask db upgrade

# Entwicklungsserver starten
flask run
```

Die App ist dann unter `http://localhost:5000` erreichbar.

### Umgebungsvariablen (lokal)

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `SECRET_KEY` | ja | Flask-Session-Schlüssel |
| `OPENAI_API_KEY` | ja | API-Key (OpenAI oder kompatibler Anbieter) |
| `DATABASE_URL` | nein | SQLAlchemy-Verbindung (Default: `sqlite:///instance/beteiligungstool.db`) |
| `OPENAI_BASE_URL` | nein | API-Endpunkt (Default: `https://api.openai.com/v1`) |
| `OPENAI_MODEL` | nein | Zu verwendendes Modell (Default: `gpt-4o`) |

### Datenbankmigrationen

Das Projekt nutzt Flask-Migrate (Alembic) für Schemaänderungen.

```bash
# Neue Migration erstellen (nach Modelländerung)
flask db migrate -m "beschreibung der aenderung"

# Migration anwenden
flask db upgrade

# Migration rückgängig machen
flask db downgrade
```

Migrationen liegen in `migrations/versions/`. Jede Datei enthält `upgrade()` und `downgrade()`. Beim Deployment wird `flask db upgrade` automatisch in `entrypoint.sh` ausgeführt.

## Wissensdatenbank

Admins können unter **Admin → Wissensdatenbank** Referenzdokumente anlegen, bearbeiten und deaktivieren. Jedes Dokument hat:

| Feld | Beschreibung |
|---|---|
| **Titel** | Anzeigename des Dokuments |
| **Kategorie** | Frei wählbares Label (z. B. `Leitlinien`, `Methodik`, `Rechtliches`) |
| **Priorität** | Reihenfolge im Prompt — niedrigere Zahl = weiter vorne. Empfehlung: 1–5 für verbindliche Vorgaben, 10–20 für allgemeines Hintergrundwissen |
| **Inhalt** | Der eigentliche Referenztext (Markdown wird unterstützt) |
| **Aktiv** | Nur aktive Dokumente werden in die KI-Generierung eingebettet |

Dokumente werden bei jeder neuen KI-Generierung automatisch berücksichtigt. Bestehende Konzepte (bereits generierte Texte) sind davon nicht betroffen.

## Deployment via Once

Siehe [deploy/README.md](deploy/README.md).
