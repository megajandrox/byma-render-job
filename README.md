# BYMA Alert Checker - GitHub Actions Cron Job

Servicio minimalista para verificar alertas de BYMA (Bolsas y Mercados Argentinos) usando GitHub Actions scheduled workflows.

## Descripción

Este proyecto ejecuta verificaciones periódicas de alertas llamando a un endpoint de la API de BYMA. A diferencia de un daemon continuo, este servicio se ejecuta como un **cron job** donde GitHub Actions maneja el scheduling y ejecuta el script en cada intervalo configurado.

## Características

- **Cron Job nativo**: GitHub Actions maneja el scheduling automáticamente
- **Ejecución única**: Cada run ejecuta una verificación y termina
- **Sin daemon**: No requiere proceso continuo ni health checks
- **Logs centralizados**: GitHub Actions captura todos los logs automáticamente
- **Configuración simple**: Un solo archivo `.github/workflows/byma-alerts-checker.yml`
- **100% Gratis**: Sin costos de infraestructura (2,000-3,000 minutos/mes incluidos)

## Arquitectura

### Componentes

1. **[src/alert_check.py](src/alert_check.py)**: Cliente HTTP que llama al endpoint `/api/v1/alerts/check`
2. **[src/run_check.py](src/run_check.py)**: Script de ejecución que ejecuta una sola verificación

### Flujo de Ejecución

```
GitHub Actions (scheduler)
  → Trigger cada 5 minutos (configurable)
  → Setup Python + Install dependencies
  → Ejecuta: python src/run_check.py
  → AlertCheck().check_alerts()
  → Llama a: {BYMA_API_URL}/api/v1/alerts/check
  → Logs a stdout
  → Exit (0=success, 1=failure)
  → GitHub captura logs y status
```

## Setup Local

### Prerrequisitos
- Python 3.12 o superior
- pip

### Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/byma-render-job.git
cd byma-render-job
```

2. Crear entorno virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tu BYMA_API_URL
```

### Testing Local

```bash
# Activar entorno virtual
source .venv/bin/activate

# Configurar API URL
export BYMA_API_URL=http://localhost:8000

# Ejecutar una verificación
python src/run_check.py
```

## Deployment en GitHub Actions

### Setup Inicial

1. **Clonar/Fork este repositorio en GitHub**

2. **Configurar Secrets**:
   - Ve a tu repositorio en GitHub
   - Settings → Secrets and variables → Actions
   - Click en "New repository secret"
   - Agrega:
     - **Name**: `BYMA_API_URL`
     - **Value**: Tu URL de API (ej: `https://api.byma.com.ar`)

3. **Activar el workflow**:
   - El workflow se activa automáticamente al hacer push
   - O manualmente: Actions → "BYMA Alerts Checker" → "Run workflow"

4. **Verificar ejecución**:
   - Ve a la pestaña "Actions" en tu repositorio
   - Verás las ejecuciones cada 5 minutos

### Ejecución Manual

Para ejecutar el check manualmente sin esperar el schedule:

1. Ve a: Actions → "BYMA Alerts Checker"
2. Click en "Run workflow"
3. Selecciona la branch (normalmente `main`)
4. Click en "Run workflow"

### Configuración del Schedule

El schedule predeterminado es cada 5 minutos (`*/5 * * * *`). Para modificarlo:

**Editar [.github/workflows/byma-alerts-checker.yml](.github/workflows/byma-alerts-checker.yml)**:
```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Cambiar a cada 15 minutos
```

Luego hacer commit y push de los cambios.

#### Ejemplos de Schedules

| Expresión | Descripción |
|-----------|-------------|
| `*/5 * * * *` | Cada 5 minutos (recomendado para producción) |
| `*/15 * * * *` | Cada 15 minutos |
| `0 * * * *` | Cada hora en punto |
| `0 9 * * *` | Todos los días a las 9 AM |
| `0 9 * * 1-5` | Días hábiles a las 9 AM |
| `*/30 9-17 * * 1-5` | Cada 30 min, 9-17hs, días hábiles |

## Variables de Entorno

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `BYMA_API_URL` | URL base de la API de BYMA | ✅ | `http://localhost:8000` |
| `PYTHON_VERSION` | Versión de Python | No | `3.12` |

## Monitoreo y Logs

### Ver Logs en GitHub Actions

1. Ve a la pestaña **Actions** en tu repositorio
2. Click en el workflow "BYMA Alerts Checker"
3. Selecciona una ejecución específica
4. Click en el job "check-alerts" para ver logs detallados
5. Cada step muestra su output completo

### Ejemplo de Log Exitoso

```
2025-01-15 10:05:00 - INFO - Starting BYMA alert check...
2025-01-15 10:05:00 - INFO - AlertCheck initialized with base URL: https://api.byma.com.ar
2025-01-15 10:05:00 - INFO - Calling alerts endpoint: https://api.byma.com.ar/api/v1/alerts/check
2025-01-15 10:05:01 - INFO - Alerts check successful: 15 alerts checked, 2 triggered
2025-01-15 10:05:01 - WARNING - Found 2 triggered alerts:
2025-01-15 10:05:01 - WARNING -   - Alert: {'symbol': 'GGAL', 'price': 1250}
2025-01-15 10:05:01 - WARNING -   - Alert: {'symbol': 'YPFD', 'price': 8900}
2025-01-15 10:05:01 - INFO - Alert check completed successfully
```

### Notificaciones de Fallos

GitHub Actions puede enviarte notificaciones automáticamente:
- **Email**: Configurado por defecto si un workflow falla
- **GitHub UI**: Badge de status en la pestaña Actions
- **Customizar**: Settings → Notifications → Actions (en tu perfil de GitHub)

## Troubleshooting

### El workflow no se ejecuta

**Verificar**:
1. El archivo `.github/workflows/byma-alerts-checker.yml` existe en la branch `main`
2. Schedule está en formato correcto (usa [crontab.guru](https://crontab.guru) para validar)
3. El repositorio ha tenido actividad en los últimos 60 días (GitHub desactiva workflows inactivos)
4. Ve a Actions → Workflows y verifica que "BYMA Alerts Checker" esté habilitado

### Error "Connection refused" o timeout

**Solución**:
- Verificar que `BYMA_API_URL` esté configurado como secret en GitHub
- Verificar que el endpoint sea accesible desde internet
- Revisar firewall/seguridad del API endpoint
- Probar ejecutar manualmente el workflow para ver logs detallados

### Error "No module named 'requests'"

**Solución**:
- Verificar que `requirements.txt` existe y está correcto en el repositorio
- El error no debería ocurrir ya que el workflow instala dependencias automáticamente
- Si ocurre, revisar los logs del step "Install dependencies"

### El workflow se desactiva automáticamente

**Causa**: GitHub desactiva workflows scheduled si no hay actividad en 60 días

**Solución**:
- Hacer un commit cualquiera (ej: actualizar README)
- O habilitar manualmente en: Actions → Workflows → "BYMA Alerts Checker" → Enable

## Costos

GitHub Actions es **100% GRATIS** para este uso:

- **Repositorios públicos**: 2,000 minutos/mes GRATIS
- **Repositorios privados**: 3,000 minutos/mes GRATIS (con plan Free)
- **Uso estimado de este proyecto**:
  - Cada ejecución: ~30 segundos (con setup de Python e instalación)
  - Frecuencia: cada 5 minutos = 288 ejecuciones/día = 8,640/mes
  - Total mensual: ~4,320 minutos (260 horas)
  - **Costo**: $0 USD (dentro del límite gratuito para repos públicos)

**Nota**: Si usas repositorio privado, considerarías ~1,320 minutos extra sobre el límite, pero GitHub cobra solo $0.008 por minuto extra = ~$10.56/mes. **Recomendación**: Usar repositorio público para mantenerlo 100% gratis.

## Diferencias vs Daemon Continuo

| Característica | Cron Job (este proyecto) | Daemon Continuo |
|----------------|-------------------------|-----------------|
| Ejecución | Intervalos definidos | Continuo 24/7 |
| Health Check | No necesario | Requerido |
| Billing | GRATIS (GitHub Actions) | Por tiempo total |
| Código | Simple (~100 líneas) | Complejo (~350 líneas) |
| Plataforma | GitHub Actions | Railway/Heroku/Render web |
| Setup | 2 minutos (agregar secret) | 10-15 minutos (deploy + config) |

## Soporte

Para problemas o preguntas:
1. Revisa los logs en GitHub Actions (pestaña "Actions")
2. Verifica configuración de secrets en Settings → Secrets and variables → Actions
3. Consulta [GitHub Actions Docs](https://docs.github.com/en/actions)
4. Abre un issue en este repositorio

## Licencia

MIT
