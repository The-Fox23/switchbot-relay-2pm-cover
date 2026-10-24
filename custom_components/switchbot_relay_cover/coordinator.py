"""Coordinator for polling SwitchBot device status."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SwitchBotApi
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SwitchBotCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the selected SwitchBot device."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SwitchBotApi,
        device_id: str,
        device_name: str,
    ) -> None:
        self.api = api
        self.device_id = device_id
        self.device_name = device_name
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{device_name}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_status(self.device_id)
        except Exception as err:
            raise UpdateFailed(f"Error fetching SwitchBot device status: {err}") from err
