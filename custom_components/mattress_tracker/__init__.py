"""The Mattress Tracker integration."""
from __future__ import annotations

import logging
from datetime import date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_MATTRESS_NAME,
    CONF_SIDE_1_NAME,
    CONF_SIDE_2_NAME,
    ROTATION_TOP_HEAD,
    ROTATION_TOP_FOOT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "button"]

SERVICE_FLIP = "flip"
SERVICE_ROTATE = "rotate"
SERVICE_SET_SIDE = "set_side"
SERVICE_SET_ROTATION = "set_rotation"

ATTR_DATE = "date"
ATTR_SIDE = "side"
ATTR_ROTATION = "rotation"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
)

SET_SIDE_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required(ATTR_SIDE): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
)

SET_ROTATION_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required(ATTR_ROTATION): cv.string,
        vol.Optional(ATTR_DATE): cv.date,
    }
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Mattress Tracker component."""
    hass.data.setdefault(DOMAIN, {})

    async def get_entry_id_from_device(device_id: str) -> str | None:
        registry = dr.async_get(hass)
        device = registry.async_get(device_id)
        if device:
            # Return the first config entry associated with this device
            return list(device.config_entries)[0] if device.config_entries else None
        return None

    async def handle_flip(call: ServiceCall):
        """Handle the flip service call."""
        device_id = call.data["device_id"]
        flip_date = call.data.get(ATTR_DATE, date.today())

        entry_id = await get_entry_id_from_device(device_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "side" in entities and "flipped" in entities:
                entities["side"].toggle_side()
                entities["flipped"].set_date(flip_date)
            if "rotated" in entities:
                entities["rotated"].set_date(flip_date)

    async def handle_rotate(call: ServiceCall):
        """Handle the rotate service call."""
        device_id = call.data["device_id"]
        rotate_date = call.data.get(ATTR_DATE, date.today())

        entry_id = await get_entry_id_from_device(device_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "rotation" in entities and "rotated" in entities:
                entities["rotation"].toggle_rotation()
                entities["rotated"].set_date(rotate_date)

    async def handle_set_side(call: ServiceCall):
        """Handle the set_side service call."""
        device_id = call.data["device_id"]
        side = call.data[ATTR_SIDE]
        set_date = call.data.get(ATTR_DATE, date.today())

        entry_id = await get_entry_id_from_device(device_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entry = hass.config_entries.async_get_entry(entry_id)
            side_1 = entry.data[CONF_SIDE_1_NAME]
            side_2 = entry.data[CONF_SIDE_2_NAME]

            if side not in [side_1, side_2]:
                _LOGGER.error("Invalid side %s. Valid options: %s, %s", side, side_1, side_2)
                return

            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "side" in entities and "flipped" in entities:
                entities["side"].set_side(side)
                entities["flipped"].set_date(set_date)
            if "rotated" in entities:
                entities["rotated"].set_date(set_date)

    async def handle_set_rotation(call: ServiceCall):
        """Handle the set_rotation service call."""
        device_id = call.data["device_id"]
        rotation = call.data[ATTR_ROTATION]
        set_date = call.data.get(ATTR_DATE, date.today())

        if rotation not in [ROTATION_TOP_HEAD, ROTATION_TOP_FOOT]:
            _LOGGER.error("Invalid rotation %s. Valid options: %s, %s", rotation, ROTATION_TOP_HEAD, ROTATION_TOP_FOOT)
            return

        entry_id = await get_entry_id_from_device(device_id)
        if entry_id and entry_id in hass.data[DOMAIN]:
            entities = hass.data[DOMAIN][entry_id].get("entities", {})
            if "rotation" in entities and "rotated" in entities:
                entities["rotation"].set_rotation(rotation)
                entities["rotated"].set_date(set_date)

    hass.services.async_register(DOMAIN, SERVICE_FLIP, handle_flip, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_ROTATE, handle_rotate, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_SIDE, handle_set_side, schema=SET_SIDE_SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SET_ROTATION, handle_set_rotation, schema=SET_ROTATION_SERVICE_SCHEMA)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mattress Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "entities": {},
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
