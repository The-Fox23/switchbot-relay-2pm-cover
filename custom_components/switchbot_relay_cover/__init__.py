"""Set up the SwitchBot Relay 2PM Cover integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwitchBotApi
from .const import CONF_SECRET, CONF_TOKEN, DOMAIN, PLATFORMS
from .coordinator import SwitchBotCoordinator

type SwitchBotConfigEntry = ConfigEntry[SwitchBotCoordinator]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SwitchBotConfigEntry) -> bool:
    """Set up a config entry and discover all supported account devices."""
    api = SwitchBotApi(
        async_get_clientsession(hass),
        entry.data[CONF_TOKEN],
        entry.data[CONF_SECRET],
    )
    coordinator = SwitchBotCoordinator(hass, api)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SwitchBotConfigEntry) -> bool:
    """Unload the integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
