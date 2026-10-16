"""The Parmair Air Conditioning integration."""

from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import ParmairCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Set up the Parmair component."""
    await _async_register_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parmair from a config entry."""
    _LOGGER.debug("Setting up Parmair integration for %s", entry.data.get("host"))

    # Register frontend static path immediately so Lovelace cards load without waiting for Modbus
    await _async_register_frontend(hass)

    coordinator = ParmairCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        raise ConfigEntryNotReady(
            f"Unable to connect to Parmair device at {entry.data.get('host')}"
        ) from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

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
                    cache_headers=True,
                )
            ]
        )
        hass.data.setdefault(DOMAIN, {})["parmair_frontend_registered"] = True
        _LOGGER.debug("Registered Parmair frontend at /parmair")

        # Automatically register as Lovelace resource so it appears in UI Add Card picker
        await _async_register_lovelace_resource(hass)
    except Exception as err:
        _LOGGER.warning("Could not register Parmair frontend path: %s", err)


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Automatically add Parmair custom card to Lovelace resources and frontend."""
    version = "0.90.1"
    card_url = f"/parmair/parmair-mac-card.js?v={version}"

    # Always register via frontend extra_js_url (loads module directly into browser window)
    try:
        from homeassistant.components.frontend import add_extra_js_url

        add_extra_js_url(hass, card_url)
        _LOGGER.debug("Added %s via add_extra_js_url", card_url)
    except Exception as ex:
        _LOGGER.debug("Could not call add_extra_js_url: %s", ex)
        if "frontend_extra_module_url" not in hass.data:
            hass.data["frontend_extra_module_url"] = set()
        hass.data["frontend_extra_module_url"].add(card_url)

    # Also register into Lovelace ResourceStorageCollection so it persists in Dashboard Resources
    if "lovelace" in hass.data:
        ll = hass.data["lovelace"]
        resources = getattr(ll, "resources", None)
        if resources is not None:
            try:
                # If resources are not loaded yet, await loading
                if not getattr(resources, "loaded", True) and hasattr(resources, "async_load"):
                    await resources.async_load()

                # Get existing items (handle both async_items and async_get_items)
                if hasattr(resources, "async_items"):
                    existing = resources.async_items()
                elif hasattr(resources, "async_get_items"):
                    existing = resources.async_get_items()
                else:
                    existing = []

                existing_item = next(
                    (item for item in existing if item.get("url", "").startswith("/parmair/")),
                    None,
                )
                if existing_item is None:
                    await resources.async_create_item({"res_type": "module", "url": card_url})
                    _LOGGER.info("Registered Parmair MAC Card in Lovelace resources: %s", card_url)
                elif existing_item.get("url") != card_url and hasattr(
                    resources, "async_update_item"
                ):
                    await resources.async_update_item(
                        existing_item["id"], {"res_type": "module", "url": card_url}
                    )
                    _LOGGER.info("Updated Parmair MAC Card in Lovelace resources to %s", card_url)
            except Exception as ex:
                _LOGGER.debug("Could not register in Lovelace storage collection: %s", ex)


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: ParmairCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
