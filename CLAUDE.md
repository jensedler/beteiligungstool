# CLAUDE.md — Beteiligungstool

Hinweise für Claude Code beim Arbeiten in diesem Repository.

## Pflichtregeln

- **Immer Migrationspfad mitdenken:** Es gibt laufende Instanzen mit gefüllten Datenbanken. Jede Schemaänderung erfordert eine Alembic-Migration (`flask db migrate`). Niemals manuelles `ALTER TABLE`. Migrations-Guards (`inspector.get_columns` / `inspector.get_table_names`) verwenden, damit bestehende Instanzen nicht beschädigt werden.
- **README.md aktualisieren:** Nach jeder relevanten Änderung (neues Feature, neue Env-Variable, geänderter Workflow) die Dokumentation mitpflegen.
- **CLAUDE.md aktualisieren:** Dieses Dokument bei architektonischen Änderungen ebenfalls anpassen.

## Technologie-Stack

- **Framework:** Flask 3.1, Python 3.11
- **ORM:** SQLAlchemy via Flask-SQLAlchemy; Migrationen mit Flask-Migrate (Alembic)
- **Datenbank:** SQLite (Pfad: `/storage/beteiligungstool.db` in Docker)
- **KI:** OpenAI-kompatible API (konfigurierbar via Env-Variablen)
- **Auth:** Flask-Login, rollenbasiert (fachamt | db_team | admin)
- **Templates:** Jinja2 + Bootstrap 5 + HTMX
- **Export:** python-docx (DOCX), markdown (HTML-Vorschau)
- **Server:** Gunicorn (Port 80), Docker

## Architektur

```
app/
  models/          # SQLAlchemy-Modelle — ein Modell pro Datei
  services/        # Geschäftslogik (ai_service, export_service, notification_service)
  blueprints/      # Flask-Blueprints (auth, main, konzept, review, admin, export)
  templates/       # Jinja2-Templates, Unterordner je Blueprint
migrations/        # Alembic-Migrationen (versions/)
seed_questions.py  # Initialisierung: Tabellen + Fragen + Admin-User
entrypoint.sh      # Docker-Start: seed_questions.py → flask db upgrade → gunicorn
```

## Datenbankmodelle

| Modell | Tabelle | Zweck |
|---|---|---|
| `User` | `users` | Nutzer mit Rollen (fachamt, db_team, admin) |
| `Section` | `sections` | Fragebogen-Sektionen |
| `Question` | `questions` | Fragen innerhalb einer Sektion |
| `Konzept` | `konzepte` | Beteiligungskonzept (Kernentität) |
| `Answer` | `answers` | Antworten des Fachamts je Konzept+Frage |
| `Comment` | `comments` | Review-Kommentare des db_teams |
| `Notification` | `notifications` | Benachrichtigungen |
| `KnowledgeDocument` | `knowledge_documents` | Referenzmaterial für KI-Generierung |

## KI-Generierung

- Einstiegspunkt: `app/services/ai_service.py`
- `_build_system_prompt()` baut den System-Prompt dynamisch: Basis-Prompt + aktive `KnowledgeDocument`-Einträge (sortiert nach `priority`)
- Generierung läuft in einem Daemon-Thread (`threading`)
- Konfiguration via Env-Variablen: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`

## Wissensdatenbank

Admins können unter **Admin → Wissensdatenbank** Referenzdokumente pflegen. Aktive Dokumente werden bei jeder KI-Generierung in den System-Prompt eingebettet.

Felder: `title`, `description`, `content` (Markdown), `category` (Freitext), `priority` (1 = höchste), `is_active`.

## Umgebungsvariablen

| Variable | Pflicht | Default |
|---|---|---|
| `SECRET_KEY` | ja | — |
| `OPENAI_API_KEY` | ja | — |
| `DATABASE_URL` | nein | `sqlite:////storage/beteiligungstool.db` |
| `OPENAI_BASE_URL` | nein | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | nein | `gpt-4o` |

## Tests / lokale Entwicklung

```bash
python3 -m venv /tmp/beteiligungstool-venv
source /tmp/beteiligungstool-venv/bin/activate
pip install -r requirements.txt
python seed_questions.py
flask db upgrade
flask run
```

Vor Python-Tests immer ein temporäres Venv unter `/tmp/beteiligungstool-venv` verwenden.
