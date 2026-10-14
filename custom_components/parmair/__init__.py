"""The Parmair Air Conditioning integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parmair from a config entry."""
    _LOGGER.debug("Setting up Parmair integration for %s", entry.data.get("host"))

    coordinator = ParmairCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        raise ConfigEntryNotReady(
            f"Unable to connect to Parmair device at {entry.data.get('host')}"
        ) from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register frontend static path for the Parmair Lovelace card and SVG schematic
    await _async_register_frontend(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Register static path for built-in Parmair Lovelace custom card."""
    from pathlib import Path

    from homeassistant.components.http import StaticPathConfig

    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        return

    # Check if already registered
    if "parmair_frontend_registered" in hass.data.get(DOMAIN, {}):
        return

    try:
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    url_path="/parmair",
                    path=str(frontend_dir),
                    cache_headers=False,
                )
            ]
        )
        hass.data[DOMAIN]["parmair_frontend_registered"] = True
        _LOGGER.debug("Registered Parmair frontend at /parmair")
    except Exception as err:
        _LOGGER.warning("Could not register Parmair frontend path: %s", err)


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: ParmairCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
