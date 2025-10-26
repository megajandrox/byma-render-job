# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BYMA Alert Checker es un cron job minimalista que usa GitHub Actions para verificar alertas de BYMA periódicamente.

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
- GitHub Actions ejecuta el script en cada intervalo del cron
- El script ejecuta UNA verificación
- El script termina (exit 0 o 1)
- GitHub Actions captura logs y status

### Components

**Alert Check Client ([src/alert_check.py](src/alert_check.py))**:
- HTTP client que llama al endpoint BYMA
- Endpoint: `{BYMA_API_URL}/api/v1/alerts/check`
- Maneja errores de red y timeouts
- Retorna Dict con resultados o None en error
- Logs detallados de alertas disparadas

**Run Script ([src/run_check.py](src/run_check.py))**:
- Entry point para GitHub Actions
- Configura logging a stdout (GitHub Actions lo captura)
- Ejecuta una sola verificación vía AlertCheck
- Exit codes:
  - `0`: Verificación exitosa
  - `1`: Error o fallo en verificación

### Execution Flow

```
GitHub Actions Scheduler (cron expression)
  ↓
Trigger workflow cada 5 minutos (configurable)
  ↓
Setup Python 3.12 + Install dependencies
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
GitHub Actions captura logs y exit code
```

## Configuration

### GitHub Actions Configuration ([.github/workflows/byma-alerts-checker.yml](.github/workflows/byma-alerts-checker.yml))

```yaml
name: BYMA Alerts Checker

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes (customizable)
  workflow_dispatch:  # Manual execution

jobs:
  check-alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: python src/run_check.py
        env:
          BYMA_API_URL: ${{ secrets.BYMA_API_URL }}
```

**Key Fields**:
- `schedule.cron` - Expresión cron estándar (5 campos)
- `workflow_dispatch` - Permite ejecución manual desde GitHub UI
- `secrets.BYMA_API_URL` - Variable de entorno desde GitHub Secrets

### Environment Variables

**Required**:
- `BYMA_API_URL`: API endpoint (no default en producción)

**Configuration**: GitHub Repo → Settings → Secrets and variables → Actions → New repository secret

## Deployment on GitHub Actions

### Initial Setup
1. Push repository to GitHub
2. GitHub Repo → Settings → Secrets and variables → Actions
3. Add secret: `BYMA_API_URL` = your API endpoint
4. Workflow auto-executes cada 5 minutos (o ejecuta manualmente)

### Updates
```bash
git commit -am "Update alert logic"
git push origin main
# GitHub Actions auto-ejecuta con los nuevos cambios
```

### Monitoring
- GitHub Repo → Actions tab: Ver todas las ejecuciones
- Click en workflow específico → Ver logs detallados de cada step
- Email automático si workflow falla

### Manual Execution
- Actions → "BYMA Alerts Checker" → "Run workflow" → Run workflow

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
GitHub Actions captura stdout, así que logs deben ir ahí:
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
- `croniter` (no necesario, GitHub Actions maneja scheduling)
- `http.server` libraries (no health checks)

## Common Tasks

### Change Schedule
Edit [.github/workflows/byma-alerts-checker.yml](.github/workflows/byma-alerts-checker.yml):
```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
```
Commit and push. GitHub Actions will update automatically.

### Add Logging
Logs go to stdout. Add logging calls in [src/alert_check.py](src/alert_check.py) or [src/run_check.py](src/run_check.py):
```python
logger.info("Your message here")
```

### Handle New API Response Format
Update parsing logic in [src/alert_check.py](src/alert_check.py) `check_alerts()` method.

### Add Error Notifications
GitHub envía emails automáticamente cuando un workflow falla. Para customizar: GitHub Profile → Settings → Notifications → Actions.

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

### Workflow not running on schedule
- Verify cron expression at [crontab.guru](https://crontab.guru)
- Check workflow is enabled: Actions → Workflows → "BYMA Alerts Checker"
- Verify file `.github/workflows/byma-alerts-checker.yml` exists in `main` branch
- GitHub desactiva workflows si no hay actividad en 60 días → Re-enable manualmente

### Connection errors
- Verify `BYMA_API_URL` secret is set correctly in GitHub Settings → Secrets
- Check API endpoint is accessible from internet
- Test endpoint with curl from external location
- Review logs in Actions tab for detailed error messages

### Secret not working
- Verify secret name is exactly `BYMA_API_URL` (case-sensitive)
- Secrets take effect in next workflow run (not retroactive)
- Try re-running the workflow manually

## Cost Optimization

- **GitHub Actions es GRATIS** para repos públicos (2,000 min/mes)
- Repos privados: 3,000 min/mes gratis, luego $0.008/min
- Este proyecto usa ~4,320 min/mes (si cada run toma 30 seg)
- **Recomendación**: Usar repo público = $0 costo total