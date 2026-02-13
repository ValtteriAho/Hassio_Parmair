"""Pymodbus API compatibility across HA/pymodbus versions.

Home Assistant bundles different pymodbus versions across releases; the parameter
for unit/slave ID has changed over time (device_id= in 3.10+, slave= and unit=
in older 3.x). We detect the working parameter on first use and cache it, so we
support any version and survive HA upgrades (module reload resets the cache).

See docs/PYMODBUS_HA_VERSIONS.md for HA release → pymodbus version mapping.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Cached parameter name for unit/slave ID (set on first successful call).
# None = not yet detected. After HA upgrade, module reload clears this.
_read_kwarg: str | None = None
_write_kwarg: str | None = None
_lock = threading.Lock()

# Try order: 3.10+ use device_id=, older 3.x use slave=, some use unit=
_READ_CANDIDATES = ("device_id", "slave", "unit")
_WRITE_CANDIDATES = ("device_id", "slave", "unit")


def read_holding_registers(client: Any, address: int, count: int, unit_id: int) -> Any:
    """Read holding registers with unit ID. Works with any pymodbus 3.x bundled by HA."""
    global _read_kwarg
    if _read_kwarg is not None:
        return client.read_holding_registers(address=address, count=count, **{_read_kwarg: unit_id})
    with _lock:
        if _read_kwarg is not None:
            return client.read_holding_registers(
                address=address, count=count, **{_read_kwarg: unit_id}
            )
        for kw in _READ_CANDIDATES:
            try:
                result = client.read_holding_registers(
                    address=address, count=count, **{kw: unit_id}
                )
                _read_kwarg = kw
                _LOGGER.debug("pymodbus read_holding_registers uses %s=", kw)
                return result
            except TypeError:
                continue
        _read_kwarg = "device_id"
        return client.read_holding_registers(address=address, count=count, device_id=unit_id)


def write_register(client: Any, address: int, value: int, unit_id: int) -> Any:
    """Write single register with unit ID. Works with any pymodbus 3.x bundled by HA."""
    global _write_kwarg
    if _write_kwarg is not None:
        return client.write_register(address, value, **{_write_kwarg: unit_id})
    with _lock:
        if _write_kwarg is not None:
            return client.write_register(address, value, **{_write_kwarg: unit_id})
        for kw in _WRITE_CANDIDATES:
            try:
                result = client.write_register(address, value, **{kw: unit_id})
                _write_kwarg = kw
                _LOGGER.debug("pymodbus write_register uses %s=", kw)
                return result
            except TypeError:
                continue
        _write_kwarg = "device_id"
        return client.write_register(address, value, device_id=unit_id)
