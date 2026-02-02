"""Button platform for Mattress Tracker."""
from __future__ import annotations

from datetime import date

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MATTRESS_NAME

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mattress Tracker buttons."""
    mattress_name = entry.data[CONF_MATTRESS_NAME]

    async_add_entities(
        [
            MattressFlipButton(entry, mattress_name),
            MattressRotateButton(entry, mattress_name),
        ]
    )

class MattressButtonBase(ButtonEntity):
    """Base class for Mattress Tracker buttons."""

    def __init__(self, entry: ConfigEntry, mattress_name: str, button_type: str) -> None:
        """Initialize the button."""
        self._entry = entry
        self._attr_name = f"{mattress_name} {button_type}"
        self._attr_unique_id = f"{entry.entry_id}_{button_type.lower().replace(' ', '_')}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": mattress_name,
            "manufacturer": "Custom",
        }

class MattressFlipButton(MattressButtonBase):
    """Button to flip the mattress."""

    def __init__(self, entry: ConfigEntry, mattress_name: str) -> None:
        """Initialize the button."""
        super().__init__(entry, mattress_name, "Flip")

    async def async_press(self) -> None:
        """Handle the button press."""
        entities = self.hass.data[DOMAIN][self._entry.entry_id]["entities"]
        if "side" in entities and "flipped" in entities:
            entities["side"].toggle_side()
            entities["flipped"].set_date(date.today())
        if "rotated" in entities:
            entities["rotated"].set_date(date.today())

class MattressRotateButton(MattressButtonBase):
    """Button to rotate the mattress."""

    def __init__(self, entry: ConfigEntry, mattress_name: str) -> None:
        """Initialize the button."""
        super().__init__(entry, mattress_name, "Rotate")

    async def async_press(self) -> None:
        """Handle the button press."""
        entities = self.hass.data[DOMAIN][self._entry.entry_id]["entities"]
        if "rotation" in entities and "rotated" in entities:
            entities["rotation"].toggle_rotation()
            entities["rotated"].set_date(date.today())
