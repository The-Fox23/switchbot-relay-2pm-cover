"""Coordinator for discovering and polling SwitchBot Relay 2PM devices."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SwitchBotApi
from .const import DOMAIN, SCAN_INTERVAL, SUPPORTED_DEVICE_TYPES

_LOGGER = logging.getLogger(__name__)


def is_supported_device(device: dict[str, Any]) -> bool:
    """Return whether the device is a supported Relay Switch 2PM."""
    device_type = str(device.get("deviceType", "")).lower()
    return any(item in device_type for item in SUPPORTED_DEVICE_TYPES)


class SwitchBotCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Discover supported devices and poll their status."""

    def __init__(self, hass: HomeAssistant, api: SwitchBotApi) -> None:
        self.api = api
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Refresh the account device list and each supported device's status."""
        try:
            devices = await self.api.get_devices()
            supported = {
                str(device["deviceId"]): device
                for device in devices
                if is_supported_device(device) and device.get("deviceId")
            }
            statuses: dict[str, dict[str, Any]] = {}
            for device_id, device in supported.items():
                try:
                    status = await self.api.get_status(device_id)
                except Exception as err:
                    _LOGGER.warning(
                        "Could not fetch status for SwitchBot device %s: %s",
                        device_id,
                        err,
                    )
                    # Preserve the device so its entity remains registered/available
                    # according to the last successful status when possible.
                    previous = (self.data or {}).get(device_id)
                    if previous is not None:
                        statuses[device_id] = {
                            **previous,
                            "_device_name": str(
                                device.get("deviceName", "SwitchBot Relay")
                            ),
                        }
                    continue
                statuses[device_id] = {
                    **status,
                    "_device_name": str(device.get("deviceName", "SwitchBot Relay")),
                    "_device_type": str(device.get("deviceType", "Relay Switch 2PM")),
                }
            if not supported:
                raise UpdateFailed("No supported Relay Switch 2PM devices were found")
            return statuses
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error discovering SwitchBot devices: {err}") from err
