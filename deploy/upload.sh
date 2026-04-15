#!/bin/bash
#
# Upload-Script - Dateien auf Server kopieren
# Ausfuehren auf dem LOKALEN Rechner
#
set -e

# ============================================
# KONFIGURATION - HIER ANPASSEN
# ============================================
SERVER_USER="root"                    # SSH-Benutzer
SERVER_HOST="85.214.130.243"          # Server-Adresse/IP
SERVER_PATH="/var/www/beteiligungstool"
LOCAL_PATH="$(dirname "$(dirname "$(realpath "$0")")")"  # Projektverzeichnis

# ============================================
# Farben
# ============================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ============================================
# Pruefungen
# ============================================
if [ ! -f "$LOCAL_PATH/wsgi.py" ]; then
    echo "Fehler: wsgi.py nicht gefunden in $LOCAL_PATH"
    exit 1
fi

echo "============================================"
echo "Beteiligungstool Upload"
echo "============================================"
echo ""
echo "Quelle:  $LOCAL_PATH"
echo "Ziel:    $SERVER_USER@$SERVER_HOST:$SERVER_PATH"
echo ""
read -p "Fortfahren? (j/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

# ============================================
# Upload mit rsync
# ============================================
log_info "Lade Dateien hoch..."

rsync -avz --progress \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude '.env' \
    --exclude 'instance/' \
    --exclude 'migrations/' \
    --exclude '.DS_Store' \
    "$LOCAL_PATH/" \
    "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"

# ============================================
# Abschluss
# ============================================
echo ""
log_info "Upload abgeschlossen!"
echo ""
echo "Naechste Schritte auf dem Server:"
echo "  ssh $SERVER_USER@$SERVER_HOST"
echo "  cd $SERVER_PATH"
echo "  sudo ./deploy/deploy.sh    # Beim ersten Mal"
echo "  sudo systemctl restart beteiligungstool  # Bei Updates"
echo ""
