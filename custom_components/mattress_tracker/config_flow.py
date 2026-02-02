"""Config flow for Mattress Tracker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MATTRESS_NAME,
    CONF_SIDE_1_NAME,
    CONF_SIDE_2_NAME,
    DEFAULT_SIDE_1_NAME,
    DEFAULT_SIDE_2_NAME,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MATTRESS_NAME): str,
        vol.Optional(CONF_SIDE_1_NAME, default=DEFAULT_SIDE_1_NAME): str,
        vol.Optional(CONF_SIDE_2_NAME, default=DEFAULT_SIDE_2_NAME): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mattress Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Check if already configured with this name
        await self.async_set_unique_id(user_input[CONF_MATTRESS_NAME])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_input[CONF_MATTRESS_NAME], data=user_input
        )
