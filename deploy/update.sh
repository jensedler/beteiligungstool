#!/bin/bash
#
# Update-Script - Nach Code-Aenderungen ausfuehren
# Ausfuehren auf dem SERVER als root
#
set -e

APP_NAME="beteiligungstool"
APP_DIR="/var/www/$APP_NAME"

# Farben
GREEN='\033[0;32m'
NC='\033[0m'
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
    echo "Bitte als root ausfuehren (sudo ./update.sh)"
    exit 1
fi

cd "$APP_DIR"

log_info "Aktiviere venv..."
source .venv/bin/activate

log_info "Installiere ggf. neue Pakete..."
pip install -r requirements.txt --quiet

log_info "Fuehre Datenbank-Migrationen aus..."
export FLASK_APP=wsgi.py
flask db upgrade 2>/dev/null || true

log_info "Setze Berechtigungen..."
chown -R www-data:www-data "$APP_DIR"

log_info "Starte Service neu..."
systemctl restart $APP_NAME

sleep 2

if systemctl is-active --quiet $APP_NAME; then
    log_info "Update erfolgreich! Service laeuft."
else
    echo "FEHLER: Service laeuft nicht!"
    journalctl -u $APP_NAME --no-pager -n 10
    exit 1
fi
