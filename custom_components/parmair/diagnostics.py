"""Diagnostics support for Parmair integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ParmairCoordinator

TO_REDACT = {
    CONF_HOST,
    "host",
    "ip_address",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: ParmairCoordinator = hass.data[DOMAIN][entry.entry_id]

    diagnostics_data: dict[str, Any] = {
        "config_entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "config_entry_options": async_redact_data(dict(entry.options), TO_REDACT),
        "device_info": coordinator.device_info,
        "software_version": coordinator.software_version,
        "heater_type": coordinator.heater_type,
        "is_connected": coordinator.is_connected,
        "coordinator_data": coordinator.data,
    }

    return diagnostics_data

