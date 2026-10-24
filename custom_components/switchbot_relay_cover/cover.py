"""Cover entities for SwitchBot Relay 2PM devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwitchBotCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add supported covers and subscribe to newly discovered devices."""
    coordinator: SwitchBotCoordinator = entry.runtime_data
    known_devices: set[str] = set()

    @callback
    def add_new_devices() -> None:
        new_devices = set(coordinator.data or {}) - known_devices
        if not new_devices:
            return
        known_devices.update(new_devices)
        async_add_entities(
            SwitchBotRelayCover(coordinator, entry, device_id)
            for device_id in new_devices
        )

    add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(add_new_devices))


class SwitchBotRelayCover(CoordinatorEntity[SwitchBotCoordinator], CoverEntity):
    """Represent one SwitchBot Relay 2PM as a native cover."""

    _attr_has_entity_name = True
    _attr_name = "Cover"
    _attr_icon = "mdi:window-shutter"
    # Keep both open and close controls available regardless of reported position.
    _attr_assumed_state = True
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )

    def __init__(
        self, coordinator: SwitchBotCoordinator, entry: ConfigEntry, device_id: str
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = device_id
        device = coordinator.data[device_id]
        self._device_name = str(device.get("_device_name", "SwitchBot Relay"))
        self._attr_unique_id = f"{device_id}_cover"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": self._device_name,
            "manufacturer": "SwitchBot",
            "model": str(device.get("_device_type", "Relay Switch 2PM")),
        }

    @property
    def available(self) -> bool:
        """Return availability only when this device has status data."""
        return super().available and self._device_id in (self.coordinator.data or {})

    @property
    def current_cover_position(self) -> int | None:
        """Return Home Assistant position (100=open, 0=closed)."""
        value = (self.coordinator.data or {}).get(self._device_id, {}).get("position")
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
        await self.coordinator.api.set_position(self._device_id, 0)
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover fully."""
        await self.coordinator.api.set_position(self._device_id, 100)
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop by commanding the currently reported position.

        The Relay Switch 2PM API documents setPosition, but not a pause command.
        """
        device_status = (self.coordinator.data or {}).get(self._device_id, {})
        switchbot_position = device_status.get("position")
        if switchbot_position is None:
            await self.coordinator.async_request_refresh()
            device_status = (self.coordinator.data or {}).get(self._device_id, {})
            switchbot_position = device_status.get("position")

        if switchbot_position is None:
            raise HomeAssistantError(
                "Cannot stop the SwitchBot cover because its current position is unknown"
            )

        try:
            position = max(0, min(100, int(switchbot_position)))
        except (TypeError, ValueError) as err:
            raise HomeAssistantError(
                "Cannot stop the SwitchBot cover because its current position is invalid"
            ) from err

        await self.coordinator.api.set_position(self._device_id, position)
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the target position requested by Home Assistant."""
        ha_position = max(0, min(100, int(kwargs["position"])))
        await self.coordinator.api.set_position(self._device_id, 100 - ha_position)
        await self.coordinator.async_request_refresh()
