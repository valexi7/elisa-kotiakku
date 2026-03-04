"""Coordinator for Elisa Kotiakku data fetching."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ElisaKotiakkuApiClient, ElisaKotiakkuApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


TIMESTAMP_KEYS = {"period_start", "period_end"}


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
            return await self.api.async_fetch_measurements()
        except ElisaKotiakkuApiError as err:
            raise UpdateFailed(f"Error communicating with Elisa Kotiakku API: {err}") from err
