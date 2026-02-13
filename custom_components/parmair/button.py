"""Button platform for Parmair MAC integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_ACKNOWLEDGE_ALARMS,
    REG_FILTER_REPLACED,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair button platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = [
        ParmairButton(
            coordinator, entry, REG_ACKNOWLEDGE_ALARMS, "Acknowledge Alarms", "mdi:bell-off", 1
        ),
        ParmairButton(
            coordinator, entry, REG_FILTER_REPLACED, "Filter Replaced", "mdi:air-filter", 1
        ),
    ]

    async_add_entities(entities)


class ParmairButton(CoordinatorEntity[ParmairCoordinator], ButtonEntity):
    """Representation of a Parmair button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        press_value: int,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._press_value = press_value
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            _LOGGER.debug(
                "Button pressed: %s, writing %s to register %s",
                self._attr_name,
                self._press_value,
                self._data_key,
            )
            await self.coordinator.async_write_register(self._data_key, self._press_value)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to press button %s: %s", self._attr_name, ex)
            raise
