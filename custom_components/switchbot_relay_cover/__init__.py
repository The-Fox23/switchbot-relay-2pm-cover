"""Set up the SwitchBot Relay 2PM Cover integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwitchBotApi
from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, CONF_SECRET, CONF_TOKEN, DOMAIN, PLATFORM
from .coordinator import SwitchBotCoordinator

PLATFORMS = ["cover"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    api = SwitchBotApi(
        async_get_clientsession(hass),
        entry.data[CONF_TOKEN],
        entry.data[CONF_SECRET],
    )
    coordinator = SwitchBotCoordinator(
        hass,
        api,
        entry.data[CONF_DEVICE_ID],
        entry.data[CONF_DEVICE_NAME],
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
