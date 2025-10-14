# BYMA Alert Checker - Render.io Cron Job

Servicio minimalista para verificar alertas de BYMA (Bolsas y Mercados Argentinos) usando Render.io Cron Jobs.

## Descripción

Este proyecto ejecuta verificaciones periódicas de alertas llamando a un endpoint de la API de BYMA. A diferencia de un daemon continuo, este servicio se ejecuta como un **cron job** donde Render.io maneja el scheduling y ejecuta el script en cada intervalo configurado.

## Características

- **Cron Job nativo**: Render.io maneja el scheduling
- **Ejecución única**: Cada run ejecuta una verificación y termina
- **Sin daemon**: No requiere proceso continuo ni health checks
- **Logs centralizados**: Render.io captura todos los logs automáticamente
- **Configuración simple**: Un solo archivo `render.yaml`

## Arquitectura

### Componentes

1. **[src/alert_check.py](src/alert_check.py)**: Cliente HTTP que llama al endpoint `/api/v1/alerts/check`
2. **[src/run_check.py](src/run_check.py)**: Script de ejecución que ejecuta una sola verificación

### Flujo de Ejecución

```
Render.io (scheduler)
  → Ejecuta: python src/run_check.py
  → AlertCheck().check_alerts()
  → Llama a: {BYMA_API_URL}/api/v1/alerts/check
  → Logs a stdout
  → Exit (0=success, 1=failure)
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

## Deployment en Render.io

### Opción 1: Usando el Dashboard (Recomendado)

1. **Crear cuenta en Render.io**: [render.com](https://render.com)

2. **Conectar repositorio**:
   - Click en "New +" → "Cron Job"
   - Conecta tu cuenta de GitHub/GitLab
   - Selecciona este repositorio

3. **Configuración automática**:
   - Render detectará el archivo `render.yaml`
   - Click en "Apply" para crear el cron job

4. **Configurar variables de entorno**:
   - En el dashboard de tu cron job, ve a "Environment"
   - Agrega: `BYMA_API_URL` con tu endpoint real
   - Ejemplo: `https://api.byma.com.ar` o tu URL personalizada

5. **Activar**: El cron job comenzará a ejecutarse según el schedule configurado

### Opción 2: Usando Blueprint (IaC)

Si prefieres Infrastructure as Code:

```bash
# Render detectará automáticamente render.yaml en el repositorio
git push origin main
```

### Configuración del Schedule

El schedule predeterminado es cada 5 minutos (`*/5 * * * *`). Para modificarlo:

**En render.yaml**:
```yaml
schedule: '*/15 * * * *'  # Cada 15 minutos
```

**O en el Dashboard**:
- Settings → Schedule → Editar expresión cron

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

### Ver Logs en Render

1. Dashboard → Tu cron job → "Logs"
2. Cada ejecución aparecerá con timestamp
3. Puedes filtrar por fecha/hora

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

Render puede enviarte notificaciones por email si un cron job falla:
- Dashboard → Settings → Notifications
- Configura tu email y alertas

## Troubleshooting

### El cron job no se ejecuta

**Verificar**:
1. Schedule está en formato correcto (usa [crontab.guru](https://crontab.guru) para validar)
2. El cron job está "activo" en el dashboard
3. No hay errores en los logs de build

### Error "Connection refused" o timeout

**Solución**:
- Verificar que `BYMA_API_URL` esté configurado correctamente
- Verificar que el endpoint sea accesible desde internet
- Revisar firewall/seguridad del API endpoint

### Error "No module named 'requests'"

**Solución**:
- Verificar que `requirements.txt` existe y está correcto
- Forzar rebuild: Dashboard → Manual Deploy → "Clear build cache & deploy"

## Costos

Render cobra por tiempo de ejecución activo:

- **Mínimo mensual**: $1 USD por cron job
- **Cobro**: Prorrateado por segundo de ejecución
- **Ejemplo**: Si cada run toma 2 segundos y ejecutas cada 5 minutos:
  - ~8,640 ejecuciones/mes
  - ~17,280 segundos = 4.8 horas
  - Costo estimado: ~$1-2 USD/mes

## Diferencias vs Daemon Continuo

| Característica | Cron Job (este proyecto) | Daemon Continuo |
|----------------|-------------------------|-----------------|
| Ejecución | Intervalos definidos | Continuo 24/7 |
| Health Check | No necesario | Requerido |
| Billing | Por tiempo de ejecución | Por tiempo total |
| Código | Simple (~100 líneas) | Complejo (~350 líneas) |
| Plataforma | Render.io cron | Railway/Heroku web |

## Soporte

Para problemas o preguntas:
1. Revisa los logs en Render dashboard
2. Verifica configuración de variables de entorno
3. Consulta [Render Docs - Cron Jobs](https://render.com/docs/cronjobs)

## Licencia

MIT
