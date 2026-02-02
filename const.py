"""Constants for the petTracer integration."""

from homeassistant.const import Platform

DOMAIN = "pettracer"

# The integration exposes multiple entity types. The list is kept
# separate so ``async_forward_entry_setups`` can be used in ``__init__``.

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER,
]
