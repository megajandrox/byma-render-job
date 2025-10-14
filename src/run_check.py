#!/usr/bin/env python3
"""
Run a single alert check for Render.io cron job.
This script executes once and exits - Render handles the scheduling.
"""
import sys
import logging
from alert_check import AlertCheck

# Configure logging to stdout (Render captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Execute a single alert check and exit."""
    logger.info("Starting BYMA alert check...")

    try:
        checker = AlertCheck()
        result = checker.check_alerts()

        if result:
            logger.info("Alert check completed successfully")
            sys.exit(0)  # Success
        else:
            logger.error("Alert check failed")
            sys.exit(1)  # Failure

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
