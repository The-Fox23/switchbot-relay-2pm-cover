"""Aggregated electrical measurement sensors for SwitchBot Relay 2PM."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwitchBotCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add one set of aggregate measurement sensors per discovered cover."""
    coordinator: SwitchBotCoordinator = entry.runtime_data
    known_devices: set[str] = set()

    @callback
    def add_new_devices() -> None:
        new_devices = set(coordinator.data or {}) - known_devices
        if not new_devices:
            return
        known_devices.update(new_devices)
        async_add_entities(
            SwitchBotRelayMeasurementSensor(coordinator, device_id, measurement)
            for device_id in new_devices
            for measurement in ("voltage", "current", "power", "energy")
        )

    add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(add_new_devices))


class SwitchBotRelayMeasurementSensor(
    CoordinatorEntity[SwitchBotCoordinator], SensorEntity
):
    """Represent combined measurements from both relay channels."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SwitchBotCoordinator, device_id: str, measurement: str
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._measurement = measurement
        device = coordinator.data[device_id]
        device_name = str(device.get("_device_name", "SwitchBot Relay"))

        definitions = {
            "voltage": ("Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, "mdi:flash"),
            "current": ("Current", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, "mdi:current-ac"),
            "power": ("Power", SensorDeviceClass.POWER, UnitOfPower.WATT, "mdi:lightning-bolt"),
            "energy": ("Daily energy", SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "mdi:lightning-bolt-circle"),
        }
        name, device_class, unit, icon = definitions[measurement]
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{measurement}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        if measurement == "energy":
            # SwitchBot reports daily consumption in watt-minutes, reset each day.
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            self._attr_state_class = SensorStateClass.MEASUREMENT
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
        """Return the combined live value or daily energy from both channels."""
        status: dict[str, Any] = (self.coordinator.data or {}).get(self._device_id, {})
        try:
            if self._measurement == "voltage":
                # Both channels are on the same mains supply; prefer channel 1.
                value = status.get("switch1Voltage")
                if value is None:
                    value = status.get("switch2Voltage")
                return float(value) if value is not None else None

            if self._measurement == "current":
                values = [status.get(f"switch{channel}ElectricCurrent") for channel in (1, 2)]
                if all(value is None for value in values):
                    return None
                return sum(float(value or 0) for value in values) / 1000.0

            if self._measurement == "power":
                values = [status.get(f"switch{channel}Power") for channel in (1, 2)]
                if all(value is None for value in values):
                    return None
                return sum(float(value or 0) for value in values)

            values = [status.get(f"switch{channel}UsedElectricity") for channel in (1, 2)]
            if all(value is None for value in values):
                return None
            # API values are watt-minutes: 60,000 watt-minutes = 1 kWh.
            return round(sum(float(value or 0) for value in values) / 60000.0, 6)
        except (TypeError, ValueError):
            return None
