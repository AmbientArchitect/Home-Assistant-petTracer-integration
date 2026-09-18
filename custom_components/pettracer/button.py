"""Support for petTracer collar buttons (find/search mode)."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PetTracerDataUpdateCoordinator
from .const import DOMAIN
from .entity import PetTracerEntity
from .helpers import device_display_name

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
            entities.append(
                PetTracerFindButton(
                    coordinator, device_id, device_display_name(device, device_id)
                )
            )

    async_add_entities(entities)


class PetTracerFindButton(PetTracerEntity, ButtonEntity):
    """Button to start the collar's temporary high-frequency search mode."""

    _attr_name = "Find"
    _attr_icon = "mdi:crosshairs-question"

    def __init__(
        self,
        coordinator: PetTracerDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the find button."""
        super().__init__(coordinator, device_id, device_name, "find")

    async def async_press(self) -> None:
        """Activate search mode on the collar.

        Search is temporary and self-expiring (see
        `PetTracerDevice.start_search_mode()`). Progress is visible via the
        device tracker's `live_tracking` attribute, which tracks
        `Device.mode == TrackingMode.SEARCH` rather than `Device.search` -
        the latter clears as soon as fast fixes start arriving, well before
        search mode itself ends.
        """
        device = self._device()
        if device is None:
            return
        await self.coordinator.client.get_device(self._device_id).start_search_mode()
        await self.coordinator.async_request_refresh()