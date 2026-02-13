"""Fan platform for Parmair ventilation integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .const import (
    DOMAIN,
    MODE_AWAY,
    MODE_BOOST,
    MODE_HOME,
    MODE_STOP,
    POWER_OFF,
    POWER_RUNNING,
    REG_CONTROL_STATE,
    REG_POWER,
    SOFTWARE_VERSION_2,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)

# Preset modes that users can select
PRESET_MODE_AWAY = "away"
PRESET_MODE_HOME = "home"
PRESET_MODE_BOOST = "boost"

ORDERED_NAMED_FAN_SPEEDS = ["away", "home", "boost"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair fan platform."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([ParmairFan(coordinator, entry)])


class ParmairFan(CoordinatorEntity[ParmairCoordinator], FanEntity):
    """Representation of a Parmair ventilation system as a fan."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_preset_modes = [PRESET_MODE_AWAY, PRESET_MODE_HOME, PRESET_MODE_BOOST]
    _attr_speed_count = 3

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        power_state = self.coordinator.data.get("power", POWER_OFF)
        control_state = self.coordinator.data.get("control_state", MODE_STOP)
        # V1: power 3 = Running. V2: power 1 = On.
        is_v2 = self.coordinator.software_version == SOFTWARE_VERSION_2 or str(
            self.coordinator.software_version
        ).startswith("2.")
        power_ok = (power_state == 1) if is_v2 else (power_state == POWER_RUNNING)
        return power_ok and control_state != MODE_STOP

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if not self.is_on:
            return 0

        control_state = self.coordinator.data.get("control_state", MODE_STOP)

        # Map control state to percentage
        if control_state == MODE_AWAY:
            return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, PRESET_MODE_AWAY)
        elif control_state == MODE_HOME:
            return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, PRESET_MODE_HOME)
        elif control_state == MODE_BOOST:
            return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, PRESET_MODE_BOOST)

        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        if not self.is_on:
            return None

        control_state = self.coordinator.data.get("control_state", MODE_STOP)

        if control_state == MODE_AWAY:
            return PRESET_MODE_AWAY
        elif control_state == MODE_HOME:
            return PRESET_MODE_HOME
        elif control_state == MODE_BOOST:
            return PRESET_MODE_BOOST

        return None

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        # First ensure power is on
        if self.coordinator.data.get("power") != POWER_RUNNING:
            await self.coordinator.async_write_register(REG_POWER, POWER_RUNNING)
            await self.coordinator.async_request_refresh()

        # Then set mode
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            # Default to HOME mode
            await self.coordinator.async_write_register(REG_CONTROL_STATE, MODE_HOME)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        if await self.coordinator.async_write_register(REG_CONTROL_STATE, MODE_STOP):
            await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return

        # Map percentage to preset mode
        named_speed = percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage)
        await self.async_set_preset_mode(named_speed)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        mode_map = {
            PRESET_MODE_AWAY: MODE_AWAY,
            PRESET_MODE_HOME: MODE_HOME,
            PRESET_MODE_BOOST: MODE_BOOST,
        }

        if preset_mode in mode_map:
            mode_value = mode_map[preset_mode]
            if await self.coordinator.async_write_register(REG_CONTROL_STATE, mode_value):
                await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose high-level metadata for diagnostics."""

        return {
            "parmair_power_register": self.coordinator.get_register_definition(REG_POWER).label,
            "parmair_control_register": self.coordinator.get_register_definition(
                REG_CONTROL_STATE
            ).label,
        }
