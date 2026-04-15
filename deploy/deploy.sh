#!/bin/bash
#
# Deployment-Script fuer Beteiligungstool
# Konfiguriert Apache als Reverse Proxy fuer den Docker-Container.
# Ausfuehren auf dem Server als root oder mit sudo.
#
set -e

# ============================================
# KONFIGURATION - HIER ANPASSEN
# ============================================
APP_NAME="beteiligungstool"
SERVER_NAME="beteiligung.bielefeld.de"  # Domain anpassen!
GUNICORN_PORT="8000"

# ============================================
# Farben fuer Ausgabe
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================
# Pruefungen
# ============================================
if [ "$EUID" -ne 0 ]; then
    log_error "Bitte als root ausfuehren (sudo ./deploy.sh)"
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${APP_NAME}$"; then
    log_error "Docker-Container '$APP_NAME' laeuft nicht."
    log_info "Bitte zuerst den Container starten:"
    log_info "  docker run -d --name $APP_NAME -p $GUNICORN_PORT:$GUNICORN_PORT \\"
    log_info "    --env-file /var/www/$APP_NAME/.env \\"
    log_info "    -v /var/www/$APP_NAME/instance:/app/instance \\"
    log_info "    $APP_NAME"
    exit 1
fi

# ============================================
# 1. Apache installieren (falls noetig)
# ============================================
if ! command -v apache2 &>/dev/null; then
    log_info "Installiere Apache..."
    apt-get update
    apt-get install -y apache2 libapache2-mod-proxy-html
fi

# ============================================
# 2. Apache-Module aktivieren
# ============================================
log_info "Aktiviere Apache-Module..."
a2enmod proxy proxy_http headers rewrite 2>/dev/null

# ============================================
# 3. Apache VirtualHost konfigurieren
# ============================================
log_info "Erstelle Apache-Konfiguration..."

cat > /etc/apache2/sites-available/${APP_NAME}.conf << EOF
<VirtualHost *:80>
    ServerName $SERVER_NAME

    # Proxy zu Gunicorn (Docker-Container)
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:$GUNICORN_PORT/
    ProxyPassReverse / http://127.0.0.1:$GUNICORN_PORT/

    # Security Headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"

    # Logs
    ErrorLog \${APACHE_LOG_DIR}/${APP_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${APP_NAME}_access.log combined
</VirtualHost>
EOF

a2ensite $APP_NAME 2>/dev/null
systemctl reload apache2

# ============================================
# 4. Abschluss
# ============================================
echo ""
echo "============================================"
log_info "Apache-Konfiguration abgeschlossen!"
echo "============================================"
echo ""
echo "Die App ist erreichbar unter: http://$SERVER_NAME"
echo ""
echo "Naechste Schritte:"
echo "  1. DNS-Eintrag fuer $SERVER_NAME auf diesen Server setzen"
echo "  2. HTTPS einrichten (empfohlen):"
echo "     apt install certbot python3-certbot-apache"
echo "     certbot --apache -d $SERVER_NAME"
echo ""
echo "Nuetzliche Befehle:"
echo "  Docker-Status:  docker ps -f name=$APP_NAME"
echo "  Docker-Logs:    docker logs -f $APP_NAME"
echo "  Neustart:       docker restart $APP_NAME"
echo "  Apache-Status:  systemctl status apache2"
echo ""
