"""Config flow for petTracer."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pettracer import PetTracerClient, PetTracerError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        # Create a fresh aiohttp session for pettracer auth
        # HA's managed session may have incompatible settings
        _LOGGER.debug("Creating fresh aiohttp session for authentication")
        async with aiohttp.ClientSession() as fresh_session:
            client = PetTracerClient(session=fresh_session)
            _LOGGER.debug(
                "PetTracerClient created with fresh session: %s", type(client)
            )

            # Authenticate with increased timeout (30 seconds)
            _LOGGER.debug("Attempting login with username: %s", data[CONF_USERNAME])
            await client.login(data[CONF_USERNAME], data[CONF_PASSWORD], timeout=30)
            _LOGGER.debug("Login successful")

            # Get all devices - returns list of Device objects
            devices = await client.get_all_devices()
            _LOGGER.debug("Retrieved %d devices", len(devices) if devices else 0)

            if not devices:
                raise CannotConnect("No devices found for this account")

            # Extract collar IDs from Device objects (use device.id)
            collar_ids = [device.id for device in devices if device.id]
            _LOGGER.debug("Found collar IDs: %s", collar_ids)

            if not collar_ids:
                raise CannotConnect("No valid collar IDs found")

    except PetTracerError as err:
        _LOGGER.error("PetTracer error: %s", err)
        raise InvalidAuth from err
    except aiohttp.ClientError as err:
        _LOGGER.error("HTTP error (type: %s): %s", type(err).__name__, err)
        raise CannotConnect from err
    except CannotConnect:
        raise
    except Exception as err:
        _LOGGER.exception(
            "Unexpected error (type: %s) connecting to petTracer: %s",
            type(err).__name__,
            err,
        )
        raise CannotConnect from err

    # Return info including collar IDs for device setup
    return {
        "title": data[CONF_USERNAME],
        "collar_ids": collar_ids,
        "device_count": len(collar_ids),
    }


class PetTracerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for petTracer."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                _LOGGER.debug("Starting validation of user input")
                info = await validate_input(self.hass, user_input)
                _LOGGER.debug("Validation successful: %s", info)
            except CannotConnect:
                _LOGGER.error("Cannot connect error during validation")
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                _LOGGER.error("Invalid auth error during validation")
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.exception("Unexpected exception during validation: %s", err)
                errors["base"] = "unknown"
            else:
                # Set unique ID based on username to prevent duplicate accounts
                _LOGGER.debug(
                    "Setting unique ID for username: %s", user_input[CONF_USERNAME]
                )
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                _LOGGER.debug("Checking for duplicate entries")
                self._abort_if_unique_id_configured()
                _LOGGER.debug("Creating config entry with title: %s", info["title"])

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
