# GSG API Deployment

## Automatisches Deployment via GitHub Actions

Das Deployment erfolgt automatisch bei jedem Push auf `main`.

### GitHub Secrets einrichten

Gehe zu: **Repository → Settings → Secrets and variables → Actions**

Erstelle folgende Secrets:

| Secret | Wert |
|--------|------|
| `SSH_PRIVATE_KEY` | Der komplette Private SSH Key (siehe unten) |
| `SERVER_HOST` | `aiserver.oneal.eu` |
| `SERVER_USER` | `gsgbot` |

### SSH Private Key

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACA+aUwjrUokzYKOFGbP1vMQDX6fl6BMJ347noIqMFRcMQAAAJiqqdt4qqnb
eAAAAAtzc2gtZWQyNTUxOQAAACA+aUwjrUokzYKOFGbP1vMQDX6fl6BMJ347noIqMFRcMQ
AAAECBOHdIJj5CPZoGm3F/ZvZ95xnroEwolGiG2RYONVsStz5pTCOtSiTNgo4UZs/W8xAN
fp+XoEwnfjuegiowVFwxAAAAFWdpdGh1Yi1hY3Rpb25zLWRlcGxveQ==
-----END OPENSSH PRIVATE KEY-----
```

## Server-Konfiguration

### Systemd Service

Der API-Service läuft als `gsg-api.service`:

```bash
# Status prüfen
sudo systemctl status gsg-api

# Logs anzeigen
sudo journalctl -u gsg-api -f

# Neustart
sudo systemctl restart gsg-api
```

### Verzeichnisse

| Pfad | Beschreibung |
|------|--------------|
| `/var/code/gsg-api` | Application Code |
| `/var/code/gsg-api/venv` | Python Virtual Environment |
| `/var/code/gsg-api/.env` | Environment Variables (nicht im Git!) |

### API Endpunkte

- **Lokal:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

## Manuelles Deployment

```bash
cd /var/code/gsg-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart gsg-api
```

## Workflow

1. **Push zu `main`** → GitHub Actions startet
2. **CI Job** → Syntax Check
3. **Deploy Job** →
   - SSH zu aiserver.oneal.eu
   - rsync Files
   - pip install
   - systemctl restart

## Troubleshooting

### Service startet nicht

```bash
# Logs prüfen
sudo journalctl -u gsg-api -n 50

# Port belegt?
ss -tlnp | grep 8000

# Manuell starten zum Debuggen
cd /var/code/gsg-api
source venv/bin/activate
uvicorn src.gsg_api.main:app --host 0.0.0.0 --port 8000
```

### Permission Denied

```bash
# Rechte prüfen
ls -la /var/code/gsg-api
chown -R gsgbot:gsgbot /var/code/gsg-api
```
