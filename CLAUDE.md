# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BYMA Alert Checker es un cron job minimalista para Render.io que verifica alertas de BYMA periódicamente.

## Essential Commands

### Development Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Local Testing
```bash
# Set environment variable
export BYMA_API_URL=http://localhost:8000

# Run a single check
python src/run_check.py

# Should output logs and exit with code 0 (success) or 1 (failure)
```

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=src
```

## Architecture

### Core Philosophy: Single Execution Model

Este proyecto usa el patrón **"run once and exit"**:
- Render.io ejecuta el script en cada intervalo del cron
- El script ejecuta UNA verificación
- El script termina (exit 0 o 1)
- Render.io captura logs y status

### Components

**Alert Check Client ([src/alert_check.py](src/alert_check.py))**:
- HTTP client que llama al endpoint BYMA
- Endpoint: `{BYMA_API_URL}/api/v1/alerts/check`
- Maneja errores de red y timeouts
- Retorna Dict con resultados o None en error
- Logs detallados de alertas disparadas

**Run Script ([src/run_check.py](src/run_check.py))**:
- Entry point para Render.io
- Configura logging a stdout (Render lo captura)
- Ejecuta una sola verificación vía AlertCheck
- Exit codes:
  - `0`: Verificación exitosa
  - `1`: Error o fallo en verificación

### Execution Flow

```
Render.io Scheduler (cron expression)
  ↓
Ejecuta: python src/run_check.py
  ↓
run_check.main()
  ↓
AlertCheck().check_alerts()
  ↓
HTTP GET → {BYMA_API_URL}/api/v1/alerts/check
  ↓
Parse response, log results
  ↓
Exit 0 (success) or 1 (failure)
  ↓
Render captura logs y exit code
```

## Configuration

### Render.io Configuration ([render.yaml](render.yaml))

```yaml
services:
  - type: cron
    name: byma-alerts-checker
    runtime: python
    schedule: '*/5 * * * *'  # Customizable
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python src/run_check.py
```

**Key Fields**:
- `type: cron` - Especifica que es un cron job
- `schedule` - Expresión cron estándar (5 campos)
- `startCommand` - Lo que Render ejecuta en cada intervalo

### Environment Variables

**Required**:
- `BYMA_API_URL`: API endpoint (no default en producción)

**Optional**:
- `PYTHON_VERSION`: Versión de Python (default: 3.12)

**Configuration**: Set in Render Dashboard → Environment

## Deployment on Render.io

### Initial Setup
1. Push repository to GitHub/GitLab
2. Render Dashboard → New → Cron Job
3. Connect repository
4. Render auto-detects `render.yaml`
5. Set `BYMA_API_URL` in Environment tab
6. Deploy

### Updates
```bash
git commit -am "Update alert logic"
git push origin main
# Render auto-rebuilds and redeploys
```

### Monitoring
- Dashboard → Logs: Ver logs de cada ejecución
- Dashboard → Settings → Notifications: Configurar alertas de fallos

## Important Patterns

### Single Execution Pattern
SIEMPRE diseñar scripts para ejecutar una vez y terminar:
```python
def main():
    result = do_work()
    if result:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
```

### Logging to Stdout
Render captura stdout, así que logs deben ir ahí:
```python
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

### Environment-based Configuration
Usar environment variables para configuración:
```python
base_url = os.getenv('BYMA_API_URL', 'http://localhost:8000')
```

## Dependencies

Minimalistas from [requirements.txt](requirements.txt):
- `requests>=2.28.0` - HTTP client (única dependencia de producción)
- `pytest>=7.0.0` - Testing (opcional, dev-only)

**NO incluye**:
- `croniter` (no necesario, Render maneja scheduling)
- `http.server` libraries (no health checks)

## Common Tasks

### Change Schedule
Edit [render.yaml](render.yaml):
```yaml
schedule: '*/15 * * * *'  # Every 15 minutes
```
Commit and push. Render will update.

### Add Logging
Logs go to stdout. Add logging calls in [src/alert_check.py](src/alert_check.py) or [src/run_check.py](src/run_check.py):
```python
logger.info("Your message here")
```

### Handle New API Response Format
Update parsing logic in [src/alert_check.py](src/alert_check.py) `check_alerts()` method.

### Add Error Notifications
Configure in Render Dashboard → Settings → Notifications. No code changes needed.

## Testing Strategy

### Local Testing
```bash
# Test single execution
export BYMA_API_URL=http://localhost:8000
python src/run_check.py
```

### Unit Tests
Create `tests/test_alert_check.py`:
```python
from src.alert_check import AlertCheck

def test_initialization():
    checker = AlertCheck("https://example.com")
    assert checker.base_url == "https://example.com"
```

## Troubleshooting

### Job not running on schedule
- Verify cron expression at [crontab.guru](https://crontab.guru)
- Check job is "Active" in Render dashboard
- Review build logs for errors

### Connection errors
- Verify `BYMA_API_URL` is correct and accessible from internet
- Check API endpoint firewall/security settings
- Test endpoint with curl from external location

### Build failures
- Check `requirements.txt` syntax
- Review build logs in Render dashboard
- Try "Clear build cache & deploy"

## Cost Optimization

- Render charges per-second of execution time
- Longer intervals = lower cost (e.g., every 15 min vs every 5 min)
- Optimize script for fast execution
- Typical run time should be 1-5 seconds