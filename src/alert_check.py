import logging
import requests
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AlertCheck:
    def __init__(self, base_url: str = None):
        """
        Inicializar el cliente de verificación de alertas.

        Args:
            base_url: URL base de la API. Si no se proporciona, se obtiene de la variable
                     de entorno BYMA_API_URL o usa http://localhost:8000 por defecto
        """
        if base_url is None:
            base_url = os.getenv('BYMA_API_URL', 'http://localhost:8000')

        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/api/v1/system/alerts/check"

        logger.info(f"AlertCheck initialized with base URL: {self.base_url}")

    def check_alerts(self) -> Optional[Dict]:
        """
        Llamar al endpoint de verificación de alertas.

        Returns:
            Dict con la respuesta del endpoint o None si hay error
        """
        try:
            logger.info(f"Calling alerts endpoint: {self.endpoint}")

            response = requests.get(
                self.endpoint,
                timeout=30,
                verify=True  # Verificar SSL
            )

            if response.status_code == 200:
                result = response.json()
                total_checked = result.get('total_alerts_checked', 0)
                triggered_count = len(result.get('triggered_alerts', []))

                logger.info(f"Alerts check successful: {total_checked} alerts checked, {triggered_count} triggered")

                # Log triggered alerts if any
                if triggered_count > 0:
                    logger.warning(f"Found {triggered_count} triggered alerts:")
                    for alert in result.get('triggered_alerts', []):
                        logger.warning(f"  - Alert: {alert}")

                return result
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while checking alerts: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while checking alerts: {e}")
            return None
