# Deployment Beteiligungstool

## Voraussetzungen Server

- Ubuntu/Debian Linux
- Apache2 installiert
- Python 3.10+
- Root-Zugang

## Erstmaliges Deployment

### 1. Konfiguration anpassen

Bearbeite `upload.sh` und `deploy.sh`:

```bash
# In upload.sh:
SERVER_USER="root"              # Dein SSH-User
SERVER_HOST="dein-server.de"    # Server IP/Domain

# In deploy.sh:
SERVER_NAME="beteiligung.bielefeld.de"  # Deine Domain
```

### 2. Dateien hochladen (lokal ausfuehren)

```bash
cd beteiligungstool
./deploy/upload.sh
```

### 3. Deployment ausfuehren (auf Server)

```bash
ssh root@dein-server.de
cd /var/www/beteiligungstool
sudo ./deploy/deploy.sh
```

### 4. .env konfigurieren (auf Server)

```bash
nano /var/www/beteiligungstool/.env
# OPENAI_API_KEY eintragen
```

### 5. HTTPS einrichten (optional, empfohlen)

```bash
apt install certbot python3-certbot-apache
certbot --apache -d beteiligung.bielefeld.de
```

## Updates einspielen

### 1. Dateien hochladen (lokal)

```bash
./deploy/upload.sh
```

### 2. Update ausfuehren (auf Server)

```bash
sudo /var/www/beteiligungstool/deploy/update.sh
```

## Nuetzliche Befehle

```bash
# Status pruefen
systemctl status beteiligungstool

# Logs anzeigen
journalctl -u beteiligungstool -f

# Service neustarten
systemctl restart beteiligungstool

# Apache neustarten
systemctl restart apache2
```

## Troubleshooting

### Service startet nicht

```bash
journalctl -u beteiligungstool -n 50
```

### 502 Bad Gateway

Gunicorn laeuft nicht:
```bash
systemctl restart beteiligungstool
```

### Berechtigungsfehler

```bash
chown -R www-data:www-data /var/www/beteiligungstool
chmod 600 /var/www/beteiligungstool/.env
```
