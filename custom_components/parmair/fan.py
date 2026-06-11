"""Fan platform for Parmair ventilation integration."""

from __future__ import annotations

import logging

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MODE_AWAY,
    MODE_BOOST,
    MODE_FIREPLACE,
    MODE_HOME,
    MODE_SAUNA,
    MODE_STOP,
    REG_CONTROL_STATE,
    SOFTWARE_VERSION_2,
)
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)

# Preset modes that users can select
PRESET_MODE_AWAY = "away"
PRESET_MODE_HOME = "home"
PRESET_MODE_BOOST = "boost"
PRESET_MODE_SAUNA = "sauna"  # V2 only — Humidity override mode
PRESET_MODE_FIREPLACE = "fireplace"  # V2 only


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
    _attr_name = "State"
    _attr_supported_features = FanEntityFeature.PRESET_MODE

    def __init__(self, coordinator: ParmairCoordinator, entry: ConfigEntry) -> None:
        """Initialize the fan entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_fan"
        self._attr_device_info = coordinator.device_info
        # Determine if V2 firmware for extended mode support
        # Prefers device-reported software_version over config entry
        # This ensures compatibility with devices configured before v0.16.0
        dev_sw = coordinator.data.get("software_version") if coordinator.data else None
        if dev_sw is not None:
            self._is_v2 = dev_sw >= 2.0 if isinstance(dev_sw, int | float) else str(dev_sw).startswith("2.")
        else:
            # Fallback to config entry when device data not yet available
            self._is_v2 = coordinator.software_version == SOFTWARE_VERSION_2 or str(
                coordinator.software_version
            ).startswith("2.")
        
        # Set preset modes based on firmware version
        if self._is_v2:
            self._attr_preset_modes = [
                PRESET_MODE_AWAY,
                PRESET_MODE_HOME,
                PRESET_MODE_BOOST,
                PRESET_MODE_SAUNA,
                PRESET_MODE_FIREPLACE,
            ]
        else:
            self._attr_preset_modes = [PRESET_MODE_AWAY, PRESET_MODE_HOME, PRESET_MODE_BOOST]

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        control_state = self.coordinator.data.get("control_state", MODE_STOP)
        if control_state == MODE_STOP:
            return None

        if control_state == MODE_AWAY:
            return PRESET_MODE_AWAY
        elif control_state == MODE_HOME:
            return PRESET_MODE_HOME
        elif control_state == MODE_BOOST:
            return PRESET_MODE_BOOST
        elif self._is_v2 and control_state == MODE_SAUNA:
            return PRESET_MODE_SAUNA
        elif self._is_v2 and control_state == MODE_FIREPLACE:
            return PRESET_MODE_FIREPLACE

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        mode_map = {
            PRESET_MODE_AWAY: MODE_AWAY,
            PRESET_MODE_HOME: MODE_HOME,
            PRESET_MODE_BOOST: MODE_BOOST,
        }
        if self._is_v2:
            mode_map[PRESET_MODE_SAUNA] = MODE_SAUNA
            mode_map[PRESET_MODE_FIREPLACE] = MODE_FIREPLACE

        if preset_mode in mode_map:
            mode_value = mode_map[preset_mode]
            if await self.coordinator.async_write_register(REG_CONTROL_STATE, mode_value):
                await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose high-level metadata for diagnostics."""

        return {
            "parmair_control_register": self.coordinator.get_register_definition(
                REG_CONTROL_STATE
            ).label,
        }
