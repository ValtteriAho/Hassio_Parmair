"""Select platform for Parmair MAC integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_AWAY_SPEED,
    REG_BOOST_SETTING,
    REG_BOOST_TIME_SETTING,
    REG_FILTER_INTERVAL,
    REG_HOME_SPEED,
    REG_OVERPRESSURE_TIME_SETTING,
    REG_SPEED_CONTROL,
    REG_SUMMER_MODE,
    SOFTWARE_VERSION_2,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)

# Device value -> UI label (single source of truth)
FILTER_INTERVAL_MAP: dict[int, str] = {0: "3 months", 1: "4 months", 2: "6 months"}
FILTER_INTERVAL_OPTIONS = list(FILTER_INTERVAL_MAP.values())
FILTER_INTERVAL_TO_VALUE = {v: k for k, v in FILTER_INTERVAL_MAP.items()}

MANUAL_SPEED_MAP: dict[int, str] = {
    0: "Auto",
    1: "Stop",
    2: "Speed 1",
    3: "Speed 2",
    4: "Speed 3",
    5: "Speed 4",
    6: "Speed 5",
}
MANUAL_SPEED_OPTIONS = list(MANUAL_SPEED_MAP.values())
MANUAL_SPEED_TO_VALUE = {v: k for k, v in MANUAL_SPEED_MAP.items()}

SPEED_PRESET_MAP: dict[int, str] = {
    0: "Speed 1",
    1: "Speed 2",
    2: "Speed 3",
    3: "Speed 4",
    4: "Speed 5",
}
SPEED_PRESET_OPTIONS = list(SPEED_PRESET_MAP.values())
SPEED_PRESET_TO_VALUE = {v: k for k, v in SPEED_PRESET_MAP.items()}

BOOST_SPEED_MAP: dict[int, str] = {2: "Speed 3", 3: "Speed 4", 4: "Speed 5"}
BOOST_SPEED_OPTIONS = list(BOOST_SPEED_MAP.values())
BOOST_SPEED_TO_VALUE = {v: k for k, v in BOOST_SPEED_MAP.items()}

SUMMER_MODE_MAP: dict[int, str] = {0: "Off", 1: "On", 2: "Auto"}
SUMMER_MODE_OPTIONS = list(SUMMER_MODE_MAP.values())
SUMMER_MODE_TO_VALUE = {v: k for k, v in SUMMER_MODE_MAP.items()}

BOOST_DURATION_MAP: dict[int, str] = {
    0: "30 min",
    1: "60 min",
    2: "90 min",
    3: "120 min",
    4: "180 min",
}
BOOST_DURATION_OPTIONS = list(BOOST_DURATION_MAP.values())
BOOST_DURATION_TO_VALUE = {v: k for k, v in BOOST_DURATION_MAP.items()}

OVERPRESSURE_DURATION_MAP: dict[int, str] = {
    0: "15 min",
    1: "30 min",
    2: "45 min",
    3: "60 min",
    4: "120 min",
}
OVERPRESSURE_DURATION_OPTIONS = list(OVERPRESSURE_DURATION_MAP.values())
OVERPRESSURE_DURATION_TO_VALUE = {v: k for k, v in OVERPRESSURE_DURATION_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair select platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]
    is_v2 = coordinator.software_version == SOFTWARE_VERSION_2 or str(
        coordinator.software_version
    ).startswith("2.")

    entities: list[SelectEntity] = [
        ParmairFilterIntervalSelect(coordinator, entry),
        ParmairManualSpeedSelect(coordinator, entry),
        ParmairSpeedPresetSelect(coordinator, entry, REG_HOME_SPEED, "Home Speed Preset"),
        ParmairSpeedPresetSelect(coordinator, entry, REG_AWAY_SPEED, "Away Speed Preset"),
        ParmairBoostSpeedSelect(coordinator, entry),
        ParmairBoostDurationSelect(coordinator, entry),
        ParmairOverpressureDurationSelect(coordinator, entry),
    ]
    if is_v2:
        entities.append(ParmairSummerModeSelect(coordinator, entry))

    async_add_entities(entities)


class ParmairFilterIntervalSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for filter change interval (3, 4 or 6 months)."""

    _attr_has_entity_name = True
    _attr_name = "Filter Change Interval"
    _attr_icon = "mdi:air-filter"
    _attr_options = FILTER_INTERVAL_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize filter interval select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_FILTER_INTERVAL}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_FILTER_INTERVAL)
        if value is None:
            return None
        return FILTER_INTERVAL_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the filter change interval."""
        raw = FILTER_INTERVAL_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_FILTER_INTERVAL, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set filter interval to %s: %s", option, ex)
            raise


class ParmairManualSpeedSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for manual speed control (Auto, Stop, Speed 1-5)."""

    _attr_has_entity_name = True
    _attr_name = "Manual Speed Control"
    _attr_icon = "mdi:fan-speed-1"
    _attr_options = MANUAL_SPEED_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize manual speed select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_SPEED_CONTROL}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_SPEED_CONTROL)
        if value is None:
            return None
        return MANUAL_SPEED_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the manual speed."""
        raw = MANUAL_SPEED_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_SPEED_CONTROL, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set manual speed to %s: %s", option, ex)
            raise


class ParmairSpeedPresetSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for Home or Away speed preset (Speed 1-5)."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:fan"
    _attr_options = SPEED_PRESET_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
    ) -> None:
        """Initialize speed preset select."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{data_key}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(self._data_key)
        if value is None:
            return None
        return SPEED_PRESET_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the speed preset."""
        raw = SPEED_PRESET_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(self._data_key, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set %s to %s: %s", self._data_key, option, ex)
            raise


class ParmairBoostSpeedSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for boost speed preset (Speed 3, 4 or 5)."""

    _attr_has_entity_name = True
    _attr_name = "Boost Speed Preset"
    _attr_icon = "mdi:fan"
    _attr_options = BOOST_SPEED_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize boost speed select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_BOOST_SETTING}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_BOOST_SETTING)
        if value is None:
            return None
        return BOOST_SPEED_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the boost speed preset."""
        raw = BOOST_SPEED_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_BOOST_SETTING, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set boost speed to %s: %s", option, ex)
            raise


class ParmairSummerModeSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for summer mode on V2 (Off, On, Auto)."""

    _attr_has_entity_name = True
    _attr_name = "Summer Mode"
    _attr_icon = "mdi:weather-sunny"
    _attr_options = SUMMER_MODE_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize summer mode select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_SUMMER_MODE}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_SUMMER_MODE)
        if value is None:
            return None
        return SUMMER_MODE_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the summer mode."""
        raw = SUMMER_MODE_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_SUMMER_MODE, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set summer mode to %s: %s", option, ex)
            raise


class ParmairBoostDurationSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for boost duration preset when activating boost."""

    _attr_has_entity_name = True
    _attr_name = "Boost Duration Preset"
    _attr_icon = "mdi:timer"
    _attr_options = BOOST_DURATION_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize boost duration select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_BOOST_TIME_SETTING}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_BOOST_TIME_SETTING)
        if value is None:
            return None
        return BOOST_DURATION_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the boost duration preset."""
        raw = BOOST_DURATION_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_BOOST_TIME_SETTING, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set boost duration to %s: %s", option, ex)
            raise


class ParmairOverpressureDurationSelect(CoordinatorEntity[ParmairCoordinator], SelectEntity):
    """Select entity for overpressure duration preset when activating overpressure."""

    _attr_has_entity_name = True
    _attr_name = "Overpressure Duration Preset"
    _attr_icon = "mdi:timer"
    _attr_options = OVERPRESSURE_DURATION_OPTIONS

    def __init__(
        self,
        coordinator: ParmairCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize overpressure duration select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{REG_OVERPRESSURE_TIME_SETTING}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data.get(REG_OVERPRESSURE_TIME_SETTING)
        if value is None:
            return None
        return OVERPRESSURE_DURATION_MAP.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Set the overpressure duration preset."""
        raw = OVERPRESSURE_DURATION_TO_VALUE.get(option)
        if raw is None:
            return
        try:
            await self.coordinator.async_write_register(REG_OVERPRESSURE_TIME_SETTING, raw)
            await self.coordinator.async_request_refresh()
        except Exception as ex:
            _LOGGER.error("Failed to set overpressure duration to %s: %s", option, ex)
            raise
