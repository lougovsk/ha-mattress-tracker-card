"""Sensor platform for Mattress Tracker."""
from __future__ import annotations

import logging
from datetime import date

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    CONF_MATTRESS_NAME,
    CONF_SIDE_1_NAME,
    CONF_SIDE_2_NAME,
    ROTATION_TOP_HEAD,
    ROTATION_TOP_FOOT,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mattress Tracker sensors."""
    mattress_name = entry.data[CONF_MATTRESS_NAME]
    side_1 = entry.data[CONF_SIDE_1_NAME]
    side_2 = entry.data[CONF_SIDE_2_NAME]

    side_sensor = MattressSideSensor(entry, mattress_name, side_1, side_2)
    flipped_sensor = MattressLastFlippedSensor(entry, mattress_name)
    rotation_sensor = MattressRotationSensor(entry, mattress_name)
    rotated_sensor = MattressLastRotatedSensor(entry, mattress_name)

    # Store references for easy access by buttons/services
    hass.data[DOMAIN][entry.entry_id]["entities"]["side"] = side_sensor
    hass.data[DOMAIN][entry.entry_id]["entities"]["flipped"] = flipped_sensor
    hass.data[DOMAIN][entry.entry_id]["entities"]["rotation"] = rotation_sensor
    hass.data[DOMAIN][entry.entry_id]["entities"]["rotated"] = rotated_sensor

    async_add_entities([side_sensor, flipped_sensor, rotation_sensor, rotated_sensor])

class MattressSensorBase(RestoreEntity, SensorEntity):
    """Base class for Mattress Tracker sensors."""

    def __init__(self, entry: ConfigEntry, mattress_name: str, sensor_type: str) -> None:
        """Initialize the sensor."""
        self._entry = entry
        self._attr_name = f"{mattress_name} {sensor_type}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type.lower().replace(' ', '_')}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": mattress_name,
            "manufacturer": "Custom",
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is None:
            return

        if state.state in ("unknown", "unavailable"):
            return

        if self.device_class == SensorDeviceClass.DATE:
            try:
                self._attr_native_value = date.fromisoformat(state.state)
            except (ValueError, TypeError):
                _LOGGER.warning("Could not restore date state for %s: %s", self.entity_id, state.state)
        else:
            self._attr_native_value = state.state

class MattressSideSensor(MattressSensorBase):
    """Sensor for the current side of the mattress."""

    def __init__(self, entry: ConfigEntry, mattress_name: str, side_1: str, side_2: str) -> None:
        """Initialize the sensor."""
        super().__init__(entry, mattress_name, "Current Side")
        self._side_1 = side_1
        self._side_2 = side_2
        self._attr_native_value = side_1 # Default

    def toggle_side(self):
        """Toggle between side 1 and side 2."""
        if self._attr_native_value == self._side_1:
            self._attr_native_value = self._side_2
        else:
            self._attr_native_value = self._side_1
        self.async_write_ha_state()

    def set_side(self, side: str):
        """Set the current side."""
        self._attr_native_value = side
        self.async_write_ha_state()

class MattressLastFlippedSensor(MattressSensorBase):
    """Sensor for the last flipped date."""

    def __init__(self, entry: ConfigEntry, mattress_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(entry, mattress_name, "Last Flipped")
        self._attr_device_class = SensorDeviceClass.DATE
        self._attr_native_value = None

    def set_date(self, date_obj):
        """Set the last flipped date."""
        self._attr_native_value = date_obj
        self.async_write_ha_state()

class MattressRotationSensor(MattressSensorBase):
    """Sensor for the current rotation of the mattress."""

    def __init__(self, entry: ConfigEntry, mattress_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(entry, mattress_name, "Current Rotation")
        self._attr_native_value = ROTATION_TOP_HEAD # Default

    def toggle_rotation(self):
        """Toggle between Top at Head and Top at Foot."""
        if self._attr_native_value == ROTATION_TOP_HEAD:
            self._attr_native_value = ROTATION_TOP_FOOT
        else:
            self._attr_native_value = ROTATION_TOP_HEAD
        self.async_write_ha_state()

    def set_rotation(self, rotation: str):
        """Set the current rotation."""
        self._attr_native_value = rotation
        self.async_write_ha_state()

class MattressLastRotatedSensor(MattressSensorBase):
    """Sensor for the last rotated date."""

    def __init__(self, entry: ConfigEntry, mattress_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(entry, mattress_name, "Last Rotated")
        self._attr_device_class = SensorDeviceClass.DATE
        self._attr_native_value = None

    def set_date(self, date_obj):
        """Set the last rotated date."""
        self._attr_native_value = date_obj
        self.async_write_ha_state()
