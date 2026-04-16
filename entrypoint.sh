#!/bin/sh
set -e

python seed_questions.py

exec gunicorn --workers 3 --bind 0.0.0.0:80 wsgi:app
