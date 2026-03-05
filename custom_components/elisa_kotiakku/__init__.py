"""The Elisa Kotiakku integration."""

from __future__ import annotations

import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ElisaKotiakkuApiClient
from .const import (
    CONF_API_KEY,
    DOMAIN,
    STARTUP_RETRY_ATTEMPTS,
    STARTUP_RETRY_DELAY_STEP,
    STARTUP_RETRY_INITIAL_DELAY,
)
from .coordinator import ElisaKotiakkuDataCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Elisa Kotiakku from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    domain_data = hass.data[DOMAIN]

    blocked_until = domain_data.get("_startup_backoff_until", 0.0)
    now = time.monotonic()
    if blocked_until > now:
        remaining = max(1, int(blocked_until - now))
        if domain_data.get("_startup_backoff_logged_until") != blocked_until:
            _LOGGER.warning(
                "Elisa Kotiakku startup backoff active, next API attempt in ~%s seconds.",
                remaining,
            )
            domain_data["_startup_backoff_logged_until"] = blocked_until
        raise ConfigEntryNotReady(
            f"Elisa Kotiakku startup backoff active, retry in ~{remaining} seconds"
        )

    session = async_get_clientsession(hass)
    api = ElisaKotiakkuApiClient(session, entry.data[CONF_API_KEY])
    coordinator = ElisaKotiakkuDataCoordinator(hass, api)

    try:
        await coordinator.async_config_entry_first_refresh()
        startup_retry_attempt = int(domain_data.get("_startup_retry_attempt", 0))
        startup_last_retry_delay = int(domain_data.get("_startup_last_retry_delay", 0))
        if startup_retry_attempt > 0:
            _LOGGER.info(
                "Initial Elisa Kotiakku API fetch succeeded after %s retry attempts "
                "(last retry delay: %s seconds).",
                startup_retry_attempt,
                startup_last_retry_delay,
            )
        domain_data.pop("_startup_backoff_until", None)
        domain_data.pop("_startup_backoff_delay", None)
        domain_data.pop("_startup_last_retry_delay", None)
    except ConfigEntryNotReady as err:
        attempt = int(domain_data.get("_startup_retry_attempt", 0)) + 1
        domain_data["_startup_retry_attempt"] = attempt
        if attempt >= STARTUP_RETRY_ATTEMPTS:
            _LOGGER.error(
                "Initial Elisa Kotiakku fetch failed after %s attempts. Marking integration setup as failed: %s",
                STARTUP_RETRY_ATTEMPTS,
                err,
            )
            domain_data.pop("_startup_backoff_until", None)
            domain_data.pop("_startup_backoff_delay", None)
            domain_data.pop("_startup_backoff_logged_until", None)
            raise ConfigEntryError(
                f"Failed to fetch initial Elisa Kotiakku data after {STARTUP_RETRY_ATTEMPTS} attempts"
            ) from err

        retry_delay = int(domain_data.get("_startup_backoff_delay", STARTUP_RETRY_INITIAL_DELAY))
        domain_data["_startup_backoff_until"] = time.monotonic() + retry_delay
        domain_data["_startup_backoff_delay"] = retry_delay + STARTUP_RETRY_DELAY_STEP
        domain_data["_startup_last_retry_delay"] = retry_delay
        domain_data.pop("_startup_backoff_logged_until", None)
        _LOGGER.warning(
            "Initial Elisa Kotiakku fetch failed (%s). Deferring next startup retry by %s seconds "
            "(attempt %s/%s).",
            err,
            retry_delay,
            attempt,
            STARTUP_RETRY_ATTEMPTS,
        )
        raise ConfigEntryNotReady(
            f"Failed to fetch initial Elisa Kotiakku data, retry in ~{retry_delay} seconds"
        ) from err

    domain_data.pop("_startup_retry_attempt", None)
    domain_data[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
