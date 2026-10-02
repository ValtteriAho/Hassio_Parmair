"""Fan platform for Parmair ventilation integration."""
# State control has been moved to the select platform (ParmairStateSelect).

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Parmair fan platform — no entities registered (State moved to select platform)."""
