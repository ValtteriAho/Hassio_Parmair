"""Switch platform for Parmair MAC integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_AUTO_CO2_BOOST,
    REG_AUTO_CO2_HOME_AWAY,
    REG_AUTO_COLD_LOWSPEED,
    REG_AUTO_HUMIDITY_BOOST,
    REG_HEATER_ENABLE,
    REG_SUMMER_MODE,
    REG_SUMMER_MODE_TEMP_LIMIT,
    REG_TIME_PROGRAM_ENABLE,
    SOFTWARE_VERSION_1,
    SOFTWARE_VERSION_2,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair switch platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]
    is_v1 = coordinator.software_version == SOFTWARE_VERSION_1 or str(
        coordinator.software_version
    ).startswith("1.")

    entities: list[SwitchEntity] = []
    # Summer Mode: V1 uses switch (0/1), V2 uses Select (Off/On/Auto)
    if is_v1:
        entities.append(
            ParmairSwitch(
                coordinator,
                entry,
                REG_SUMMER_MODE,
                "Summer Mode",
                "mdi:weather-sunny",
                "Enables heat recovery summer operation mode",
            )
        )
    entities.extend(
        [
            ParmairSwitch(
                coordinator,
                entry,
                REG_TIME_PROGRAM_ENABLE,
                "Time Program",
                "mdi:clock-outline",
                "Enables weekly time program control",
            ),
            ParmairSwitch(
                coordinator,
                entry,
                REG_HEATER_ENABLE,
                "Post Heater",
                "mdi:radiator",
                "Enables post-heating element",
            ),
        ]
    )

    if not is_v1:
        entities.extend(
            [
                ParmairSwitch(
                    coordinator,
                    entry,
                    REG_AUTO_CO2_BOOST,
                    "Auto CO2 Boost",
                    "mdi:molecule-co2",
                    "Automatically activates boost mode when CO2 exceeds the boost threshold",
                ),
                ParmairSwitch(
                    coordinator,
                    entry,
                    REG_AUTO_HUMIDITY_BOOST,
                    "Auto Humidity Boost",
                    "mdi:water-percent",
                    "Automatically activates boost mode when humidity is high",
                ),
                ParmairSwitch(
                    coordinator,
                    entry,
                    REG_AUTO_CO2_HOME_AWAY,
                    "Auto CO2 Home/Away",
                    "mdi:home-import-outline",
                    "Automatically switches between Home and Away based on CO2 level",
                ),
                ParmairSwitch(
                    coordinator,
                    entry,
                    REG_AUTO_COLD_LOWSPEED,
                    "Auto Cold Speed Reduction",
                    "mdi:snowflake",
                    "Automatically reduces fan speed in very cold outdoor conditions",
                ),
            ]
        )

    async_add_entities(entities)


class ParmairSwitch(CoordinatorEntity[ParmairCoordinator], SwitchEntity):
    """Representation of a Parmair switch."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        icon: str,
        description: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_entity_registry_enabled_default = True

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None
        # V2 summer mode (AUTO_SUMMER_COOL_S): 0=off, 1=on, 2=auto
        if self._data_key == REG_SUMMER_MODE:
            is_v2 = self.coordinator.software_version == SOFTWARE_VERSION_2 or str(
                self.coordinator.software_version
            ).startswith("2.")
            if is_v2:
                return value in (1, 2)
        return value == 1

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for summer mode switch."""
        # Only add attributes for summer mode switch
        if self._data_key == REG_SUMMER_MODE:
            temp_limit = self.coordinator.data.get(REG_SUMMER_MODE_TEMP_LIMIT)
            if temp_limit is not None:
                return {"temperature_limit": f"{temp_limit}°C"}
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.async_write_register(self._data_key, 1)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to turn on %s: %s", self._data_key, ex)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.async_write_register(self._data_key, 0)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to turn off %s: %s", self._data_key, ex)
            raise
