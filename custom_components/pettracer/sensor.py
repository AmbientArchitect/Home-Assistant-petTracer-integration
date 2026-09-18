"""Support for petTracer sensors."""

from __future__ import annotations

from datetime import datetime
import logging

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
from homeassistant.util import dt as dt_util

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN
from .entity import PetTracerEntity
from .helpers import battery_percentage, charging_label, device_display_name, is_searching, tracking_mode_label

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
            device_name = device_display_name(device, device_id)
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


class PetTracerSensor(PetTracerEntity, SensorEntity):
    """Representation of a petTracer sensor."""

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the petTracer sensor."""
        super().__init__(coordinator, device_id, device_name, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> int | float | str | datetime | None:
        """Return the state of the sensor."""
        device = self._device()
        if device is None:
            return None

        if self.entity_description.key == "battery_level":
            if device.bat:
                return battery_percentage(device.bat)
            return None

        if self.entity_description.key == "battery_voltage":
            return device.bat

        if self.entity_description.key == "signal_strength":
            if device.lastPos is not None and device.lastPos.rssi is not None:
                return device.lastPos.rssi
            return None

        if self.entity_description.key == "last_contact":
            if device.lastContact:
                if isinstance(device.lastContact, str):
                    try:
                        return dt_util.parse_datetime(device.lastContact)
                    except (ValueError, TypeError):
                        _LOGGER.warning(
                            "Failed to parse lastContact timestamp: %s",
                            device.lastContact,
                        )
                        return None
                if isinstance(device.lastContact, datetime):
                    return device.lastContact
            return None

        if self.entity_description.key == "satellites":
            if device.lastPos is not None and device.lastPos.sat is not None:
                return device.lastPos.sat
            return None

        if self.entity_description.key == "charging_status":
            return charging_label(device.chg)

        if self.entity_description.key == "tracking_mode":
            return tracking_mode_label(device.modeSet)

        if self.entity_description.key == "search_status":
            if device.mode is not None:
                return "On" if is_searching(device.mode) else "Off"
            return None

        return None