"""HTTP client for Elisa Kotiakku public API."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession
from yarl import URL

from homeassistant.exceptions import HomeAssistantError

from .const import API_BASE_URL, MEASUREMENTS_PATH


class ElisaKotiakkuApiError(HomeAssistantError):
    """Base API error."""


class ElisaKotiakkuApiAuthError(ElisaKotiakkuApiError):
    """Authentication or authorization error."""


class ElisaKotiakkuApiClient:
    """Client for the Elisa Kotiakku public API."""

    def __init__(self, session: ClientSession, api_key: str) -> None:
        """Initialize API client."""
        self._session = session
        self._api_key = api_key

    async def async_fetch_measurements(
        self,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch measurements from the API."""
        url = URL(API_BASE_URL).with_path(MEASUREMENTS_PATH)
        params: dict[str, str] = {}

        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        headers = {"x-api-key": self._api_key}

        try:
            response = await self._session.get(url, params=params, headers=headers, timeout=20)
        except ClientError as err:
            raise ElisaKotiakkuApiError(f"Unable to connect to Elisa Kotiakku API: {err}") from err

        async with response:
            if response.status in (401, 403):
                raise ElisaKotiakkuApiAuthError("Invalid or unauthorized API key")
            if response.status == 429:
                raise ElisaKotiakkuApiError("Rate limit exceeded")
            if response.status >= 400:
                body = await response.text()
                raise ElisaKotiakkuApiError(
                    f"Elisa Kotiakku API request failed ({response.status}): {body}"
                )

            payload = await response.json()

        if not isinstance(payload, list):
            raise ElisaKotiakkuApiError("Unexpected API response format, expected array")

        return [item for item in payload if isinstance(item, dict)]
