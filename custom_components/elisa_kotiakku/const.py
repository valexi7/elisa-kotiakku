"""Constants for the Elisa Kotiakku integration."""

from datetime import timedelta

DOMAIN = "elisa_kotiakku"
NAME = "Elisa Kotiakku"

API_BASE_URL = "https://residential.gridle.com"
MEASUREMENTS_PATH = "/api/public/measurements"

CONF_API_KEY = "api_key"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
