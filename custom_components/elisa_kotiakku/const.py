"""Constants for the Elisa Kotiakku integration."""

from datetime import timedelta

DOMAIN = "elisa_kotiakku"
NAME = "Elisa Kotiakku"

API_BASE_URL = "https://residential.gridle.com"
MEASUREMENTS_PATH = "/api/public/measurements"

CONF_API_KEY = "api_key"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=4)
RATE_LIMIT_INTERVAL_STEP = timedelta(minutes=2)
MAX_SCAN_INTERVAL = timedelta(minutes=20)

STARTUP_RETRY_INITIAL_DELAY = 300  # 5 minutes as the data is updated every 5 minutes
STARTUP_RETRY_DELAY_STEP = 300
STARTUP_RETRY_ATTEMPTS = 10
