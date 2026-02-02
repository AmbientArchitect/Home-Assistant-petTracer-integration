"""Support for petTracer device tracking."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
    AddEntitiesCallback,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from pettracer import PetTracerClient

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the petTracer device tracker platform from YAML."""
    # Get the YAML config stored during async_setup
    if DOMAIN not in hass.data or "yaml_config" not in hass.data[DOMAIN]:
        _LOGGER.error("petTracer not configured in configuration.yaml")
        return

    conf = hass.data[DOMAIN]["yaml_config"]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]

    # Create our own aiohttp session for petTracer
    # HA's managed session has incompatible settings
    session = aiohttp.ClientSession()
    client = PetTracerClient(session=session)
    await client.login(username, password, timeout=30)

    # Create a simple coordinator for YAML setup
    coordinator = PetTracerYAMLCoordinator(hass, client, session)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            # device is a Device dataclass object
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(PetTracerDeviceTracker(coordinator, device_id, device_name))

    async_add_entities(entities, True)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up petTracer device tracker entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            # device is a Device dataclass object
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(PetTracerDeviceTracker(coordinator, device_id, device_name))

    async_add_entities(entities)


class PetTracerYAMLCoordinator(DataUpdateCoordinator):
    """Coordinator for YAML-based setup."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: PetTracerClient,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.session = session

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_yaml",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Fetch data from petTracer API."""
        try:
            # Get all devices using the async get_all_devices() method
            # Returns List[Device] with Device dataclass objects
            devices = await self.client.get_all_devices()
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with petTracer API: {err}"
            ) from err
        else:
            # Build a dictionary with device data, keyed by device ID
            data = {}
            for device in devices:
                if device.id:
                    # Store the complete Device object
                    # lastPos contains the latest location data
                    data[device.id] = device

            return data


class PetTracerDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a petTracer device tracker."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the petTracer device tracker."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_source_type = SourceType.GPS

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this tracker."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "petTracer",
            "model": "Pet Collar",
        }

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        return device.lastPos.posLat if device.lastPos else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        return device.lastPos.posLong if device.lastPos else None

    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return 0

        device = self.coordinator.data[self._device_id]
        return device.lastPos.acc if device.lastPos and device.lastPos.acc else 0

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return None

        device = self.coordinator.data[self._device_id]
        # Convert battery voltage (mV) to approximate percentage
        # Typical range: 3300mV (empty) to 4200mV (full)
        if device.bat:
            return min(100, max(0, int((device.bat - 3300) / 9)))
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}

        if not self.coordinator.data or self._device_id not in self.coordinator.data:
            return attrs

        device = self.coordinator.data[self._device_id]

        # Add battery voltage (mV)
        if device.bat:
            attrs["battery_voltage"] = device.bat

        # Add last position timestamp
        if device.lastPos and device.lastPos.timeMeasure:
            attrs["last_update"] = device.lastPos.timeMeasure

        # Add last contact with device
        if device.lastContact:
            attrs["last_contact"] = device.lastContact

        # Add GPS quality info
        if device.lastPos:
            if device.lastPos.sat is not None:
                attrs["satellites"] = device.lastPos.sat
            if device.lastPos.rssi is not None:
                attrs["signal_strength"] = device.lastPos.rssi

        # Add device status
        if device.status is not None:
            attrs["status"] = device.status
        if device.mode is not None:
            attrs["mode"] = device.mode

        return attrs
