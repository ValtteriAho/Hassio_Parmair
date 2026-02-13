"""Number platform for Parmair MAC integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_BOOST_TIMER,
    REG_EXHAUST_TEMP_SETPOINT,
    REG_OVERPRESSURE_TIMER,
    REG_SUMMER_MODE_TEMP_LIMIT,
    REG_SUPPLY_TEMP_SETPOINT,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair number platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = [
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_EXHAUST_TEMP_SETPOINT, "Exhaust Temperature Setpoint"
        ),
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_SUPPLY_TEMP_SETPOINT, "Supply Temperature Setpoint"
        ),
        ParmairTemperatureSetpointNumber(
            coordinator, entry, REG_SUMMER_MODE_TEMP_LIMIT, "Summer Mode Temperature Limit"
        ),
        ParmairTimerNumber(
            coordinator,
            entry,
            REG_BOOST_TIMER,
            "Boost Timer",
            "mdi:timer",
            "Set boost mode timer in minutes",
        ),
        ParmairTimerNumber(
            coordinator,
            entry,
            REG_OVERPRESSURE_TIMER,
            "Overpressure Timer",
            "mdi:timer",
            "Set overpressure mode timer in minutes",
        ),
    ]

    async_add_entities(entities)


class ParmairNumberEntity(CoordinatorEntity[ParmairCoordinator], NumberEntity):
    """Base class for Parmair number entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.coordinator.async_write_register(self._data_key, int(value))
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set %s to %s: %s", self._data_key, value, ex)
            raise


class ParmairTemperatureSetpointNumber(ParmairNumberEntity):
    """Number entity for temperature setpoints."""

    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize temperature setpoint number."""
        super().__init__(coordinator, entry, data_key, name)

        # Set appropriate ranges based on register
        if data_key == REG_EXHAUST_TEMP_SETPOINT:
            self._attr_native_min_value = 18.0
            self._attr_native_max_value = 26.0
            self._attr_native_step = 0.5
        elif data_key == REG_SUPPLY_TEMP_SETPOINT:
            self._attr_native_min_value = 15.0
            self._attr_native_max_value = 25.0
            self._attr_native_step = 0.5
        elif data_key == REG_SUMMER_MODE_TEMP_LIMIT:
            self._attr_native_min_value = 15.0
            self._attr_native_max_value = 30.0
            self._attr_native_step = 0.5


class ParmairTimerNumber(ParmairNumberEntity):
    """Number entity for boost/overpressure timers (minutes)."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = -1
    _attr_native_max_value = 300
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize timer number."""
        super().__init__(coordinator, entry, data_key, name)
        self._attr_icon = icon
