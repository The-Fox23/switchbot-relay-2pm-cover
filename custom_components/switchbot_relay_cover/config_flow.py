"""Config flow for the SwitchBot Relay 2PM account."""

from __future__ import annotations

import hashlib

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwitchBotApi
from .const import CONF_SECRET, CONF_TOKEN, DOMAIN
from .coordinator import is_supported_device


class SwitchBotRelayCoverConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up all supported Relay Switch 2PM devices for one SwitchBot account."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Validate account credentials and discover supported devices."""
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            secret = user_input[CONF_SECRET].strip()
            api = SwitchBotApi(
                async_get_clientsession(self.hass), token, secret
            )
            try:
                devices = await api.get_devices()
                supported = [device for device in devices if is_supported_device(device)]
                if not supported:
                    errors["base"] = "no_supported_devices"
                else:
                    # Keep credentials out of the unique ID; the hash only prevents
                    # adding the same account more than once through this flow.
                    account_id = hashlib.sha256(token.encode()).hexdigest()[:24]
                    await self.async_set_unique_id(f"account_{account_id}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="SwitchBot Relay 2PM",
                        data={CONF_TOKEN: token, CONF_SECRET: secret},
                    )
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
