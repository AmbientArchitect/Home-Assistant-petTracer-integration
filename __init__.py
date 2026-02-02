"""The petTracer integration."""

from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pettracer import PetTracerClient, PetTracerError

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

# Schema for YAML configuration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the petTracer component from YAML configuration."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    # Store the config for later use in platform setup
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["yaml_config"] = conf

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up petTracer from a config entry."""
    _LOGGER.debug("async_setup_entry called for entry: %s", entry.entry_id)
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    # Create our own aiohttp session for petTracer
    # HA's managed session has incompatible settings for the petTracer API
    _LOGGER.debug("Creating dedicated session for petTracer API")
    session = aiohttp.ClientSession()
    client = PetTracerClient(session=session)

    # Authenticate and validate
    try:
        _LOGGER.debug("Logging in with username: %s", username)
        await client.login(username, password, timeout=30)
        # Test authentication by fetching devices
        await client.get_all_devices()
        _LOGGER.debug("Authentication successful")
    except PetTracerError as err:
        _LOGGER.error("Failed to authenticate with petTracer: %s", err)
        await session.close()
        raise ConfigEntryAuthFailed from err
    except Exception as err:
        _LOGGER.error("Unexpected error connecting to petTracer: %s", err)
        await session.close()
        raise ConfigEntryNotReady from err

    coordinator = PetTracerDataUpdateCoordinator(hass, client, entry, session)
    _LOGGER.debug("Coordinator created, performing first refresh")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("First refresh complete")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    _LOGGER.debug("Coordinator stored in hass.data")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("Entry setup complete")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        # Close the session we created
        if hasattr(coordinator, "session"):
            await coordinator.session.close()

    return unload_ok


class PetTracerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching petTracer data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: PetTracerClient,
        entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.entry = entry
        self.session = session

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Fetch data from petTracer API."""
        try:
            # Get all devices using the async get_all_devices() method
            # Returns List[Device] with Device dataclass objects
            devices = await self.client.get_all_devices()
        except PetTracerError as err:
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
