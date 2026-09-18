"""Support for petTracer collar buttons (find/search mode)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up petTracer button entities from config entry."""
    coordinator: PetTracerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data:
        for device_id, device in coordinator.data.items():
            device_name = (
                device.details.name if device.details else f"Pet Tracker {device_id}"
            )
            entities.append(PetTracerFindButton(coordinator, device_id, device_name))

    async_add_entities(entities)


class PetTracerFindButton(CoordinatorEntity, ButtonEntity):
    """Button to start the collar's temporary high-frequency search mode."""

    _attr_has_entity_name = True
    _attr_name = "Find"
    _attr_icon = "mdi:crosshairs-question"

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: int,
        device_name: str,
    ) -> None:
        """Initialize the find button."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_find"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this button."""
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

    async def async_press(self) -> None:
        """Activate search mode on the collar.

        Search is temporary and self-expiring (see
        `PetTracerDevice.start_search_mode()`). Progress is visible via the
        device tracker's `live_tracking` attribute, which tracks
        `Device.mode == TrackingMode.SEARCH` rather than `Device.search` -
        the latter clears as soon as fast fixes start arriving, well before
        search mode itself ends.
        """
        await self.coordinator.client.get_device(self._device_id).start_search_mode()
        await self.coordinator.async_request_refresh()
