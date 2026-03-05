"""HTTP client for Elisa Kotiakku public API."""

from __future__ import annotations

from asyncio import TimeoutError
import json
from typing import Any

from aiohttp import ClientError, ClientSession
from yarl import URL

from homeassistant.exceptions import HomeAssistantError

from .const import API_BASE_URL, MEASUREMENTS_PATH


class ElisaKotiakkuApiError(HomeAssistantError):
    """Base API error."""


class ElisaKotiakkuApiAuthError(ElisaKotiakkuApiError):
    """Authentication or authorization error."""


class ElisaKotiakkuApiConnectionError(ElisaKotiakkuApiError):
    """Network/connection error when reaching the API."""


class ElisaKotiakkuApiRateLimitError(ElisaKotiakkuApiError):
    """Rate limit exceeded error."""


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
        except (ClientError, TimeoutError) as err:
            raise ElisaKotiakkuApiConnectionError(
                f"Unable to connect to Elisa Kotiakku API: {err}"
            ) from err

        async with response:
            if response.status in (401, 403):
                raise ElisaKotiakkuApiAuthError("Invalid or unauthorized API key")
            body = await response.text()
            if response.status == 429:
                api_message = _extract_api_message(body)
                if api_message:
                    raise ElisaKotiakkuApiRateLimitError(
                        f"Rate limit exceeded: {api_message}"
                    )
                raise ElisaKotiakkuApiRateLimitError("Rate limit exceeded: no response message")
            if response.status >= 400:
                api_message = _extract_api_message(body)
                if not api_message:
                    api_message = body.strip() or "no response message"
                raise ElisaKotiakkuApiError(
                    f"Elisa Kotiakku API request failed ({response.status}): {api_message}"
                )

            payload = json.loads(body)

        if not isinstance(payload, list):
            raise ElisaKotiakkuApiError("Unexpected API response format, expected array")

        return [item for item in payload if isinstance(item, dict)]


def _extract_api_message(body: str) -> str | None:
    """Extract a human-readable message from API response body."""
    stripped = body.strip()
    if not stripped:
        return None

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    if isinstance(parsed, dict):
        for key in ("message", "error", "detail"):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return stripped

    return stripped
