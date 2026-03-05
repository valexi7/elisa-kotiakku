"""Config flow for Elisa Kotiakku integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ElisaKotiakkuApiAuthError, ElisaKotiakkuApiClient, ElisaKotiakkuApiError
from .const import CONF_API_KEY, DOMAIN


class ElisaKotiakkuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Elisa Kotiakku."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            is_valid = await self._async_validate_api_key(api_key)
            if is_valid:
                return self.async_create_entry(title="Elisa Kotiakku", data={CONF_API_KEY: api_key})
            errors["base"] = "invalid_auth"

        schema = vol.Schema({vol.Required(CONF_API_KEY): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _async_validate_api_key(self, api_key: str) -> bool:
        """Validate API key by doing a lightweight API call."""
        session = async_get_clientsession(self.hass)
        client = ElisaKotiakkuApiClient(session, api_key)

        try:
            await client.async_fetch_measurements()
        except ElisaKotiakkuApiAuthError:
            return False
        except ElisaKotiakkuApiError:
            return False

        return True
