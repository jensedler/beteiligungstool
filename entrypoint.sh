#!/bin/sh
set -e

python seed_questions.py
flask db upgrade

exec gunicorn --workers 3 --bind 0.0.0.0:80 wsgi:app
