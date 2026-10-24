"""Cover entity for SwitchBot Relay 2PM."""

from __future__ import annotations

from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME, DOMAIN
from .coordinator import SwitchBotCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    coordinator: SwitchBotCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SwitchBotRelayCover(coordinator, entry)])


class SwitchBotRelayCover(CoordinatorEntity[SwitchBotCoordinator], CoverEntity):
    """Represent a SwitchBot Relay 2PM as a cover."""

    _attr_has_entity_name = True
    _attr_name = "Cover"
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )

    def __init__(self, coordinator: SwitchBotCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_cover"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_id)},
            "name": entry.data[CONF_DEVICE_NAME],
            "manufacturer": "SwitchBot",
            "model": "Relay Switch 2PM",
        }

    @property
    def current_cover_position(self) -> int | None:
        """Return Home Assistant position (100=open, 0=closed)."""
        value = self.coordinator.data.get("position")
        if value is None:
            return None
        try:
            switchbot_position = max(0, min(100, int(value)))
        except (TypeError, ValueError):
            return None
        return 100 - switchbot_position

    @property
    def is_closed(self) -> bool | None:
        """Return whether the cover is fully closed."""
        position = self.current_cover_position
        if position is None:
            return None
        return position == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover fully."""
        await self.coordinator.api.set_position(self.coordinator.device_id, 0)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover fully."""
        await self.coordinator.api.set_position(self.coordinator.device_id, 100)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Try to stop movement by commanding the currently reported position."""
        status = self.coordinator.data or {}
        current_position = status.get("position")

        # SwitchBot uses 0=open and 100=closed. Re-send that raw position
        # as the target instead of relying on turnOff, which did not stop motion.
        try:
            target_position = max(0, min(100, int(current_position)))
        except (TypeError, ValueError):
            await self.coordinator.async_request_refresh()
            return

        await self.coordinator.api.set_position(
            self.coordinator.device_id, target_position
        )
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the target position requested by Home Assistant."""
        ha_position = max(0, min(100, int(kwargs["position"])))
        switchbot_position = 100 - ha_position
        await self.coordinator.api.set_position(
            self.coordinator.device_id, switchbot_position
        )
        await self.coordinator.async_request_refresh()
