# Deployment Beteiligungstool

## Deployment via Once (empfohlen)

Die App ist für das Deployment über [Once](https://github.com/basecamp/once) vorbereitet und erfüllt alle Voraussetzungen:

- Docker-Container, der HTTP auf Port 80 bereitstellt
- Healthcheck-Endpunkt unter `/up`
- Persistente Daten unter `/storage`

### Voraussetzungen

- Once ist auf dem Zielserver installiert
- Ein DNS-Eintrag für die gewünschte Domain zeigt auf den Server
- Das Docker-Image ist auf GitHub Container Registry veröffentlicht (siehe unten)

### Docker-Image veröffentlichen

Das Repository enthält einen GitHub Actions Workflow (`.github/workflows/docker-publish.yml`), der das Image automatisch baut und auf der GitHub Container Registry (GHCR) veröffentlicht, sobald ein neues Tag gepusht wird.

**Wichtig:** Erst den Pull Request in `master` mergen, dann taggen — das Image wird immer auf dem Stand von `master` gebaut.

Das Tag muss zwingend mit `v` beginnen (z.B. `v1.0.0`), da der Workflow nur auf Tags der Form `v*` reagiert.

#### Option A: Terminal

```bash
git checkout master
git pull
git tag v0.1.0
git push origin v0.1.0
```

#### Option B: github.com

1. Repo-Seite öffnen → **Releases** → **Create a new release**
2. Unter **Choose a tag** ein neues Tag eingeben — Format: `v0.1.0` (mit `v`, ohne Punkt danach)
3. Als Ziel-Branch `master` auswählen
4. **Publish release** klicken → der Workflow startet automatisch

Das Image ist danach unter `ghcr.io/jensedler/beteiligungstool:<version>` verfügbar.

### Erstmaliges Deployment

1. Ein neues Tag pushen, um das Image zu bauen (siehe oben).

2. In der Once-Oberfläche die App hinzufügen und den Image-Pfad sowie die Domain eintragen:

```
ghcr.io/jensedler/beteiligungstool:latest
```

3. Umgebungsvariablen in den Once-Einstellungen (`s` für Settings) konfigurieren:

| Variable | Pflicht | Beschreibung |
|---|---|---|
| `OPENAI_API_KEY` | ja | OpenAI API-Key |
| `OPENAI_BASE_URL` | nein | API-Endpunkt (Default: `https://api.openai.com/v1`) |
| `OPENAI_MODEL` | nein | Zu verwendendes Modell (Default: `gpt-4o`) |

`SECRET_KEY_BASE` wird von Once automatisch gesetzt und als Flask `SECRET_KEY` verwendet.

4. Die Datenbank wird beim ersten Start automatisch initialisiert. Dabei wird ein Admin-Account angelegt:

| E-Mail | Passwort |
|---|---|
| `admin@bielefeld.de` | `changeme123` |

**Das Passwort nach dem ersten Login umgehend ändern.**

Der Seed-Prozess legt einen Admin-Account an:

| E-Mail | Passwort |
|---|---|
| `admin@bielefeld.de` | `changeme123` |

**Das Passwort nach dem ersten Login umgehend ändern.**

### Updates einspielen

Neues Image bauen, pushen und in der Once-Oberfläche neu deployen.

---

## Staging-Umgebung

### Konzept

Zwei Tags steuern, welche Once-Instanz ein Update erhält:

| Docker-Tag | Wann gesetzt | Once-Instanz |
|---|---|---|
| `latest` | Nur bei stabilen Releases (`v1.2.0`) | Produktion |
| `staging` | Nur bei Pre-Release-Tags (`v1.2.0-rc.1`) | Staging |

Da die Produktiv-Instanz in Once auf `:latest` pinnt und die Staging-Instanz auf `:staging`, zieht Once nie automatisch ein Update für die falsche Umgebung.

### Branch-Strategie

```
master   ──●──────────────────────────────●──── (Produktion, v1.2.0)
            ↑                              ↑ Merge + stabiles Tag
staging  ───●──●──●──●──●──●──●──●──●──● ─────  (v1.2.0-rc.1, -rc.2, …)
```

Entwicklung findet auf dem `staging`-Branch statt. Ist ein Stand bereit zum Testen, wird ein Pre-Release-Tag gesetzt.

### Staging-Release erstellen

```bash
git checkout staging
git pull
git tag v1.2.0-rc.1
git push origin v1.2.0-rc.1
```

Der Workflow baut das Image und veröffentlicht es als `ghcr.io/jensedler/beteiligungstool:staging` sowie `ghcr.io/jensedler/beteiligungstool:1.2.0-rc.1`. Das GitHub-Release wird automatisch als „Pre-release" markiert.

Danach in der Once-Oberfläche die Staging-App manuell neu deployen — die Produktiv-App bleibt unberührt.

### Staging-Instanz in Once einrichten

1. In Once eine neue App anlegen
2. Image-Pfad:
   ```
   ghcr.io/jensedler/beteiligungstool:staging
   ```
3. Domain: `staging.beteiligungstool.<domain>`
4. Dieselben Umgebungsvariablen wie Produktion konfigurieren (ggf. andere Werte)

### Staging → Produktion

```bash
git checkout master
git merge staging
git push
git tag v1.2.0
git push origin v1.2.0
```

Das stabile Tag setzt `latest` — die Produktiv-Instanz kann nun in Once aktualisiert werden.

### Datenpersistenz

Die SQLite-Datenbank liegt unter `/storage/beteiligungstool.db` im Container. Once bindet dieses Verzeichnis als persistentes Volume ein und sichert es automatisch.

---

## Manuelles Deployment (ohne Once)

### Voraussetzungen Server

- Ubuntu/Debian Linux
- Docker installiert
- Root-Zugang

### Container starten

```bash
docker run -d \
  --name beteiligungstool \
  -p 80:80 \
  -v /var/www/beteiligungstool/storage:/storage \
  -e SECRET_KEY=<zufaelliger-schluessel> \
  -e OPENAI_API_KEY=<dein-key> \
  <registry>/<image-name>:latest
```

### Updates einspielen

```bash
docker pull <registry>/<image-name>:latest
docker stop beteiligungstool && docker rm beteiligungstool
# docker run ... (wie oben)
```

## Troubleshooting

### Container startet nicht

```bash
docker logs beteiligungstool
```

### Healthcheck schlägt fehl

```bash
curl http://localhost/up
# Erwartete Antwort: OK
```

### Datenbankfehler

Sicherstellen, dass das `/storage`-Verzeichnis im Container beschreibbar ist:

```bash
docker exec -it beteiligungstool ls -la /storage
```
