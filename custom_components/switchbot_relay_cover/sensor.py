"""Electrical measurement sensors for SwitchBot Relay 2PM devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfPower, UnitOfElectricPotential
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwitchBotCoordinator


@dataclass(frozen=True, slots=True)
class Measurement:
    """Description of one measurement provided by the Relay Switch 2PM API."""

    key_suffix: str
    name: str
    device_class: SensorDeviceClass
    native_unit: str
    divisor: float = 1.0


MEASUREMENTS: tuple[Measurement, ...] = (
    Measurement("Voltage", "Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT),
    Measurement("Power", "Power", SensorDeviceClass.POWER, UnitOfPower.WATT),
    # The SwitchBot API reports electric current in milliamps; Home Assistant uses amps.
    Measurement("ElectricCurrent", "Current", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 1000.0),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add measurement sensors for all supported devices, including new discoveries."""
    coordinator: SwitchBotCoordinator = entry.runtime_data
    known_devices: set[str] = set()

    @callback
    def add_new_devices() -> None:
        new_devices = set(coordinator.data or {}) - known_devices
        if not new_devices:
            return
        known_devices.update(new_devices)
        async_add_entities(
            SwitchBotRelayMeasurementSensor(coordinator, device_id, channel, measurement)
            for device_id in new_devices
            for channel in (1, 2)
            for measurement in MEASUREMENTS
        )

    add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(add_new_devices))


class SwitchBotRelayMeasurementSensor(
    CoordinatorEntity[SwitchBotCoordinator], SensorEntity
):
    """Represent one electrical measurement for one relay channel."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SwitchBotCoordinator,
        device_id: str,
        channel: int,
        measurement: Measurement,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._measurement = measurement
        device = coordinator.data[device_id]
        device_name = str(device.get("_device_name", "SwitchBot Relay"))
        self._status_key = f"switch{channel}{measurement.key_suffix}"
        self._attr_name = f"Switch {channel} {measurement.name}"
        self._attr_unique_id = f"{device_id}_switch{channel}_{measurement.key_suffix.lower()}"
        self._attr_device_class = measurement.device_class
        self._attr_native_unit_of_measurement = measurement.native_unit
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "SwitchBot",
            "model": str(device.get("_device_type", "Relay Switch 2PM")),
        }

    @property
    def available(self) -> bool:
        """Only report availability when this device has status data."""
        return super().available and self._device_id in (self.coordinator.data or {})

    @property
    def native_value(self) -> float | None:
        """Return the latest measurement, converting milliamps to amps if needed."""
        status: dict[str, Any] = (self.coordinator.data or {}).get(self._device_id, {})
        value = status.get(self._status_key)
        if value is None:
            return None
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return None
        numeric_value /= self._measurement.divisor
        return round(numeric_value, 3) if self._measurement.divisor != 1.0 else numeric_value
