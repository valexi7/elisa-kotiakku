"""Coordinator for Elisa Kotiakku data fetching."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ElisaKotiakkuApiClient,
    ElisaKotiakkuApiConnectionError,
    ElisaKotiakkuApiError,
    ElisaKotiakkuApiRateLimitError,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MAX_SCAN_INTERVAL, RATE_LIMIT_INTERVAL_STEP

_LOGGER = logging.getLogger(__name__)


TIMESTAMP_KEYS = {"period_start", "period_end"}
EXPECTED_MEASUREMENT_KEYS = {
    "battery_power_kw",
    "state_of_charge_percent",
    "solar_power_kw",
    "grid_power_kw",
    "house_power_kw",
    "solar_to_house_kw",
    "solar_to_battery_kw",
    "solar_to_grid_kw",
    "grid_to_house_kw",
    "grid_to_battery_kw",
    "battery_to_house_kw",
    "battery_to_grid_kw",
    "battery_temperature_celsius",
}


class ElisaKotiakkuDataCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Handle fetching Elisa Kotiakku data."""

    def __init__(self, hass: HomeAssistant, api: ElisaKotiakkuApiClient) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api
        self._api_connection_lost_logged = False
        self._null_values_logged = False
        self._base_update_interval = DEFAULT_SCAN_INTERVAL
        self._current_rate_limited_interval = DEFAULT_SCAN_INTERVAL
        self._rate_limit_retry_attempt = 0
        self._last_rate_limit_delay_seconds = 0

    @property
    def latest_row(self) -> dict[str, Any]:
        """Return the latest row with at least one measurement value."""
        if not self.data:
            return {}

        for row in reversed(self.data):
            non_timestamp_values = [
                value for key, value in row.items() if key not in TIMESTAMP_KEYS and value is not None
            ]
            if non_timestamp_values:
                return row

        return self.data[-1]

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch latest measurements data from API."""
        try:
            data = await self.api.async_fetch_measurements()
            self._api_connection_lost_logged = False
            self._reset_rate_limit_backoff_if_needed()

            if self._latest_measurements_are_null(data):
                if not self._null_values_logged:
                    _LOGGER.warning(
                        "Elisa Kotiakku API is reachable, but all latest measurement values are null. "
                        "Connection to the inverter may be lost."
                    )
                    self._null_values_logged = True
            else:
                self._null_values_logged = False

            return data
        except ElisaKotiakkuApiRateLimitError as err:
            self._rate_limit_retry_attempt += 1
            next_interval = self._increase_rate_limit_backoff()
            self._last_rate_limit_delay_seconds = int(next_interval.total_seconds())
            _LOGGER.warning(
                "Elisa Kotiakku API rate-limited the request (%s). "
                "Using cached data and delaying next poll to %s seconds (retry attempt %s).",
                err,
                int(next_interval.total_seconds()),
                self._rate_limit_retry_attempt,
            )

            if self.data:
                return self.data

            raise UpdateFailed(f"Rate limited by Elisa Kotiakku API during initial load: {err}") from err
        except ElisaKotiakkuApiConnectionError as err:
            if not self._api_connection_lost_logged:
                _LOGGER.warning(
                    "Connection to Elisa Kotiakku API lost (no response body available): %s",
                    err,
                )
                self._api_connection_lost_logged = True
            raise UpdateFailed(f"Error communicating with Elisa Kotiakku API: {err}") from err
        except ElisaKotiakkuApiError as err:
            _LOGGER.warning("Elisa Kotiakku API returned an error response: %s", err)
            raise UpdateFailed(f"Error communicating with Elisa Kotiakku API: {err}") from err

    def _increase_rate_limit_backoff(self):
        """Increase polling interval incrementally after rate-limit responses."""
        next_interval = min(
            self._current_rate_limited_interval + RATE_LIMIT_INTERVAL_STEP,
            MAX_SCAN_INTERVAL,
        )
        self._current_rate_limited_interval = next_interval
        self.update_interval = next_interval
        return next_interval

    def _reset_rate_limit_backoff_if_needed(self) -> None:
        """Restore base interval once API requests succeed again."""
        if self._rate_limit_retry_attempt > 0:
            _LOGGER.info(
                "Elisa Kotiakku API request succeeded after %s retry attempts "
                "(last retry delay: %s seconds).",
                self._rate_limit_retry_attempt,
                self._last_rate_limit_delay_seconds,
            )
        if self.update_interval != self._base_update_interval:
            _LOGGER.info(
                "Elisa Kotiakku API request succeeded, restoring polling interval to %s seconds.",
                int(self._base_update_interval.total_seconds()),
            )
        self._rate_limit_retry_attempt = 0
        self._last_rate_limit_delay_seconds = 0
        self._current_rate_limited_interval = self._base_update_interval
        self.update_interval = self._base_update_interval

    @staticmethod
    def _latest_measurements_are_null(data: list[dict[str, Any]]) -> bool:
        """Check if the latest row has only null values for expected measurements."""
        if not data:
            return False

        latest = data[-1]
        present_keys = [key for key in EXPECTED_MEASUREMENT_KEYS if key in latest]
        if not present_keys:
            return False

        return all(latest.get(key) is None for key in present_keys)
