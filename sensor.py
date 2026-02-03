"""Support for petTracer sensors."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery_level",
        name="Battery level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="battery_voltage",
        name="Battery voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="signal_strength",
        name="Signal strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="last_contact",
        name="Last contact",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="satellites",
        name="GPS satellites",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:satellite-variant",
    ),
    SensorEntityDescription(
        key="charging_status",
        name="Charging status",
        icon="mdi:battery-charging",
    ),
    SensorEntityDescription(
        key="tracking_mode",
        name="Tracking mode",
        icon="mdi:crosshairs",
    ),
    SensorEntityDescription(
        key="search_status",
        name="Live tracking",
        icon="mdi:radar",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up petTracer sensor entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            for description in SENSOR_TYPES:
                entities.append(
                    PetTracerSensor(
                        coordinator,
                        device_id,
                        device_name,
                        description,
                    )
                )

    async_add_entities(entities)


class PetTracerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a petTracer sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the petTracer sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{description.key}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this sensor."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "petTracer",
            "model": "Pet Collar",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._device_id in self.coordinator.data
        )

    @property
    def native_value(self) -> int | float | datetime | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]

        if self.entity_description.key == "battery_level":
            # Convert battery voltage (mV) to approximate percentage
            # Typical range: 3300mV (empty) to 4200mV (full)
            if device.bat:
                return min(100, max(0, int((device.bat - 3300) / 9)))
            return None

        if self.entity_description.key == "battery_voltage":
            return device.bat

        if self.entity_description.key == "signal_strength":
            if device.lastPos and device.lastPos.rssi is not None:
                return device.lastPos.rssi
            return None

        if self.entity_description.key == "last_contact":
            if device.lastContact:
                # If lastContact is a string, try to parse it
                if isinstance(device.lastContact, str):
                    try:
                        return dt_util.parse_datetime(device.lastContact)
                    except (ValueError, TypeError):
                        _LOGGER.warning(
                            "Failed to parse lastContact timestamp: %s",
                            device.lastContact,
                        )
                        return None
                # If it's already a datetime object
                if isinstance(device.lastContact, datetime):
                    return device.lastContact
            return None

        if self.entity_description.key == "satellites":
            if device.lastPos and device.lastPos.sat is not None:
                return device.lastPos.sat
            return None

        if self.entity_description.key == "charging_status":
            if device.chg is not None:
                return "Charging" if device.chg == 1 else "Not charging"
            return None

        if self.entity_description.key == "tracking_mode":
            if device.modeSet is not None:
                modes = {1: "Fast", 2: "Normal", 3: "Slow"}
                return modes.get(device.modeSet, "Unknown")
            return None

        if self.entity_description.key == "search_status":
            if device.search is not None:
                return "On" if device.search else "Off"
            return None

        return None
