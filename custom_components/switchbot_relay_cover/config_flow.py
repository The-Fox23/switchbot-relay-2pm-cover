"""Config flow for SwitchBot Relay 2PM Cover."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .api import SwitchBotApi
from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_SECRET,
    CONF_TOKEN,
    DOMAIN,
    SUPPORTED_DEVICE_TYPES,
)


def _supported(device: dict[str, Any]) -> bool:
    """Return whether the device is a Relay Switch 2PM."""
    device_type = str(device.get("deviceType", "")).lower()
    return any(item in device_type for item in SUPPORTED_DEVICE_TYPES)


class SwitchBotRelayCoverConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SwitchBot Relay 2PM Cover."""

    VERSION = 1

    def __init__(self) -> None:
        self._token = ""
        self._secret = ""
        self._devices: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Validate credentials and discover supported devices."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._token = user_input[CONF_TOKEN].strip()
            self._secret = user_input[CONF_SECRET].strip()
            api = SwitchBotApi(
                async_get_clientsession(self.hass), self._token, self._secret
            )
            try:
                devices = await api.get_devices()
                self._devices = [device for device in devices if _supported(device)]
                if not self._devices:
                    errors["base"] = "no_supported_devices"
                elif len(self._devices) == 1:
                    return await self._create_entry(self._devices[0])
                else:
                    return await self.async_step_device()
            except HomeAssistantError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_TOKEN): str,
                vol.Required(CONF_SECRET): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_device(self, user_input: dict[str, Any] | None = None):
        """Select the device to integrate."""
        if user_input is not None:
            selected_id = user_input[CONF_DEVICE_ID]
            device = next(
                (
                    item
                    for item in self._devices
                    if str(item.get("deviceId")) == selected_id
                ),
                None,
            )
            if device is None:
                return self.async_abort(reason="device_not_found")
            return await self._create_entry(device)

        options = [
            {
                "value": str(device.get("deviceId", "")),
                "label": (
                    f"{device.get('deviceName', 'SwitchBot device')} "
                    f"({device.get('deviceType', 'Unknown type')})"
                ),
            }
            for device in self._devices
        ]
        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): SelectSelector(
                    SelectSelectorConfig(options=options, mode="dropdown")
                )
            }
        )
        return self.async_show_form(step_id="device", data_schema=schema)

    async def _create_entry(self, device: dict[str, Any]):
        """Create the config entry for a selected device."""
        device_id = str(device.get("deviceId", ""))
        device_name = str(device.get("deviceName", "SwitchBot Relay"))
        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=device_name,
            data={
                CONF_TOKEN: self._token,
                CONF_SECRET: self._secret,
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_NAME: device_name,
            },
        )
