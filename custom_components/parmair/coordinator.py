"""DataUpdateCoordinator for Parmair integration."""

from __future__ import annotations

import contextlib
import logging
import random
import threading
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from . import pymodbus_compat
from .const import (
    CONF_HEATER_TYPE,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_SOFTWARE_VERSION,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    HARDWARE_TYPE_MAP_V2,
    HEATER_TYPE_UNKNOWN,
    POLLING_REGISTER_KEYS,
    SOFTWARE_VERSION_1,
    SOFTWARE_VERSION_2,
    STATIC_REGISTER_KEYS,
    RegisterDefinition,
    get_register_definition,
    get_registers_for_version,
)

_LOGGER = logging.getLogger(__name__)


def _set_unit_id(client: ModbusTcpClient, unit_id: int) -> None:
    """Set unit ID on the Modbus client for pymodbus 3.x."""
    # Pymodbus 3.x uses 'slave' attribute
    if hasattr(client, "slave"):
        client.slave = unit_id
    # Fallback to other common attributes
    elif hasattr(client, "unit_id"):
        client.unit_id = unit_id
    elif hasattr(client, "slave_id"):
        client.slave_id = unit_id


def _build_read_ranges(
    address_to_definitions: dict[int, list[RegisterDefinition]],
    max_registers: int = 125,
) -> list[tuple[int, int]]:
    """Group addresses into consecutive spans for batch reads.

    Args:
        address_to_definitions: Maps address -> list of definitions using that address
        max_registers: Max registers per Modbus request (Modbus limit is 125)

    Returns:
        List of (start_address, count) for each consecutive span
    """
    if not address_to_definitions:
        return []
    addresses = sorted(address_to_definitions.keys())
    ranges: list[tuple[int, int]] = []
    start = addresses[0]
    count = 1
    for prev, curr in zip(addresses[:-1], addresses[1:], strict=True):
        if curr == prev + 1 and count < max_registers:
            count += 1
        else:
            ranges.append((start, count))
            start = curr
            count = 1
    ranges.append((start, count))
    return ranges


class ParmairCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Parmair data from Modbus."""

    def _opt(self, key: str, default: Any) -> Any:
        """Get config value from options with fallback to entry data."""
        opts = self.entry.options or {}
        return opts.get(key, self.entry.data.get(key, default))

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = self._opt(CONF_HOST, entry.data.get(CONF_HOST, ""))
        self.port = self._opt(CONF_PORT, DEFAULT_PORT)
        # Parmair devices use unit 0; default to 0 and treat legacy slave_id=1 as 0
        raw_slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
        if raw_slave_id == 1:
            _LOGGER.warning(
                "Config has slave_id=1 but Parmair uses unit 0; using 0. "
                "Delete and re-add the integration to clear this warning."
            )
            self.slave_id = 0
        else:
            self.slave_id = raw_slave_id
        # Prefer options (user-configured) over initial config
        self.software_version = self._opt(CONF_SOFTWARE_VERSION, SOFTWARE_VERSION_1)
        self.heater_type = self._opt(CONF_HEATER_TYPE, HEATER_TYPE_UNKNOWN)

        scan_interval = self._opt(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        # Get version-specific register map
        self._registers = get_registers_for_version(self.software_version)

        # Separate static and dynamic register lists
        self._static_registers: list[RegisterDefinition] = [
            self._registers[key] for key in STATIC_REGISTER_KEYS if key in self._registers
        ]

        self._poll_registers: list[RegisterDefinition] = [
            self._registers[key] for key in POLLING_REGISTER_KEYS if key in self._registers
        ]

        # Storage for static data (read once)
        self._static_data: dict[str, Any] = {}
        self._static_data_read = False

        self._client = ModbusTcpClient(host=self.host, port=self.port)
        self._lock = threading.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Parmair via Modbus."""
        try:
            return await self.hass.async_add_executor_job(self._read_modbus_data)
        except ModbusException as err:
            raise UpdateFailed(f"Error communicating with Parmair device: {err}") from err

    def _read_modbus_data(self) -> dict[str, Any]:
        """Read data from Modbus (runs in executor)."""
        with self._lock:
            # Use a fresh client per poll to avoid transaction_id mismatch from stale
            # responses or from another Modbus client (pymodbus: "transaction_id=X but got id=Y").
            read_client = ModbusTcpClient(host=self.host, port=self.port)
            try:
                if not read_client.connect():
                    raise ModbusException("Failed to connect to Modbus device")
                _set_unit_id(read_client, self.slave_id)
                # Delay after connect to let device and buffers settle
                time.sleep(0.5)
                # Jitter to desynchronize from other Modbus clients polling the same device
                time.sleep(random.uniform(0.2, 0.7))
            except Exception:
                with contextlib.suppress(Exception):
                    read_client.close()
                raise

            # Wake-up read: power register (1001) to keep device responsive
            with contextlib.suppress(Exception):
                _ = read_client.read_holding_registers(address=1001, count=1)
            time.sleep(0.3)

            # Read static registers once on first poll (batched)
            if not self._static_data_read:
                _LOGGER.info("Reading static device information (one-time read)")
                static_addr_to_defs: dict[int, list[RegisterDefinition]] = {}
                for definition in self._static_registers:
                    static_addr_to_defs.setdefault(definition.address, []).append(definition)
                for start_addr, span_count in _build_read_ranges(static_addr_to_defs):
                    block = self._read_register_block(start_addr, span_count, read_client)
                    for _ in range(3):
                        if block is None:
                            time.sleep(0.5)
                            block = self._read_register_block(start_addr, span_count, read_client)
                    if block is not None:
                        for i, raw in enumerate(block):
                            addr = start_addr + i
                            if addr in static_addr_to_defs:
                                for definition in static_addr_to_defs[addr]:
                                    if definition.optional and raw < 0:
                                        continue
                                    self._static_data[definition.key] = self._from_raw(
                                        definition, raw
                                    )
                                    _LOGGER.debug(
                                        "Static register %s: %s",
                                        definition.label,
                                        self._static_data[definition.key],
                                    )
                    time.sleep(0.3)
                self._static_data_read = True

            data: dict[str, Any] = {}
            failed_registers: list[str] = []

            try:
                # Group definitions by address to avoid duplicate reads (e.g. v2 USERSTATECONTROL)
                address_to_definitions: dict[int, list[RegisterDefinition]] = {}
                for definition in self._poll_registers:
                    address_to_definitions.setdefault(definition.address, []).append(definition)

                # Read in batched ranges, one Modbus request per consecutive span
                for start_addr, span_count in _build_read_ranges(address_to_definitions):
                    block = self._read_register_block(start_addr, span_count, read_client)
                    for _ in range(3):
                        if block is None:
                            time.sleep(0.5)
                            block = self._read_register_block(start_addr, span_count, read_client)
                    if block is None:
                        for addr in range(start_addr, start_addr + span_count):
                            if addr in address_to_definitions:
                                failed_registers.append(
                                    f"{address_to_definitions[addr][0].label}({address_to_definitions[addr][0].register_id})"
                                )
                        continue
                    for i, raw in enumerate(block):
                        addr = start_addr + i
                        if addr not in address_to_definitions:
                            continue
                        definitions = address_to_definitions[addr]
                        first_def = definitions[0]
                        if first_def.optional and raw < 0:
                            continue
                        value = self._from_raw(first_def, raw)
                        for definition in definitions:
                            data[definition.key] = value
                    time.sleep(0.3)

                if failed_registers:
                    _LOGGER.debug(
                        "Failed to read %d registers: %s",
                        len(failed_registers),
                        ", ".join(failed_registers),
                    )

                # Merge static data with dynamic data
                data.update(self._static_data)

                # v2.x: home_state, boost_state, overpressure_state share register 1181 (USERSTATECONTROL_FO)
                # 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace
                # Derive binary values for sensors that expect 0/1
                is_v2 = self.software_version == SOFTWARE_VERSION_2 or str(
                    self.software_version
                ).startswith("2.")
                if is_v2:
                    user_state = data.get("control_state")
                    if user_state is not None:
                        data["home_state"] = 1 if user_state == 2 else 0  # 2=Home
                        data["boost_state"] = 1 if user_state == 3 else 0  # 3=Boost
                        data["overpressure_state"] = (
                            1 if user_state in (4, 5) else 0
                        )  # 4=Sauna, 5=Fireplace

                _LOGGER.debug(
                    "Read data from Parmair %s: %d values (%d static, %d dynamic)",
                    self.host,
                    len(data),
                    len(self._static_data),
                    len(data) - len(self._static_data),
                )
                return data

            except Exception as ex:
                _LOGGER.error("Error reading from Modbus: %s", ex)
                raise ModbusException(f"Failed to read data: {ex}") from ex
            finally:
                with contextlib.suppress(Exception):
                    read_client.close()

    def write_register(self, key: str, value: float | int) -> bool:
        """Write a value to a Modbus register respecting scaling with pymodbus 3.x."""
        definition = get_register_definition(key, self._registers)
        try:
            with self._lock:
                if not self._client.connected and not self._client.connect():
                    return False

                # Set unit ID on client
                _set_unit_id(self._client, self.slave_id)

                raw_value = self._to_raw(definition, value)

                result = pymodbus_compat.write_register(
                    self._client, definition.address, raw_value, self.slave_id
                )

                _LOGGER.debug(
                    "Wrote %s to register %s (%d): raw=%d",
                    value,
                    definition.label,
                    definition.address,
                    raw_value,
                )

                # Small delay after write to allow device to process
                time.sleep(0.3)

                return not result.isError() if hasattr(result, "isError") else result is not None
        except Exception as ex:
            _LOGGER.error(
                "Error writing to Modbus register %s (%s): %s",
                definition.register_id,
                definition.label,
                ex,
            )
            return False

    async def async_write_register(self, key: str, value: float | int) -> bool:
        """Write a value to a Modbus register (async)."""

        return await self.hass.async_add_executor_job(self.write_register, key, value)

    async def async_shutdown(self) -> None:
        """Close the Modbus connection."""

        def _close():
            with self._lock:
                if self._client.connected:
                    self._client.close()

        await self.hass.async_add_executor_job(_close)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        sw_version = self.data.get("software_version")
        hw_type = self.data.get("hardware_type")

        # Determine MAC model from hardware type
        model = "MAC"
        if hw_type is not None:
            hw_int = int(hw_type)
            is_v2 = self.software_version == SOFTWARE_VERSION_2 or str(
                self.software_version
            ).startswith("2.")
            model_num = HARDWARE_TYPE_MAP_V2.get(hw_int, hw_int) if is_v2 else hw_int
            model = f"MAC {model_num}"

        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self._opt(CONF_NAME, DEFAULT_NAME),
            "manufacturer": "Parmair",
            "model": model,
        }

        # Add software version
        if sw_version is not None:
            if isinstance(sw_version, int | float):
                device_info["sw_version"] = f"{sw_version:.2f}"
            else:
                device_info["sw_version"] = str(sw_version)

        return device_info

    def get_register_definition(self, key: str) -> RegisterDefinition:
        """Expose register metadata for other components."""
        return get_register_definition(key, self._registers)

    def _read_register_block(
        self, address: int, count: int, client: ModbusTcpClient | None = None
    ) -> list[int] | None:
        """Read a block of consecutive registers. Returns raw values or None on failure."""
        c = client if client is not None else self._client
        try:
            result = pymodbus_compat.read_holding_registers(c, address, count, self.slave_id)
            if not result or (hasattr(result, "isError") and result.isError()):
                return None
            if hasattr(result, "registers"):
                raw_list = list(result.registers)
            elif isinstance(result, list | tuple):
                raw_list = list(result)
            else:
                return None
            if len(raw_list) != count:
                return None
            # Convert to signed int16 where needed
            out: list[int] = []
            for raw in raw_list:
                if raw > 32767:
                    raw = raw - 65536
                out.append(raw)
            return out
        except Exception as ex:
            _LOGGER.warning(
                "Exception reading block at address %d count %d: %s",
                address,
                count,
                ex,
            )
            return None

    def _read_register_value(self, definition: RegisterDefinition) -> Any | None:
        """Read and scale a single register with pymodbus 3.x."""
        try:
            result = pymodbus_compat.read_holding_registers(
                self._client, definition.address, 1, self.slave_id
            )
            if not result or (hasattr(result, "isError") and result.isError()):
                _LOGGER.warning(
                    "Failed reading register %s (%s) at address %d",
                    definition.register_id,
                    definition.label,
                    definition.address,
                )
                return None

            if hasattr(result, "registers"):
                raw = result.registers[0]
            elif isinstance(result, list | tuple):
                raw = result[0]
            else:
                raw = result

            # Convert to signed int16 if value is > 32767 (handle negative temperatures)
            if raw > 32767:
                raw = raw - 65536

            if definition.optional and raw < 0:
                # Device reports -1 when module isn't installed
                return None
        except Exception as ex:
            _LOGGER.warning(
                "Exception reading register %s (%s): %s",
                definition.register_id,
                definition.label,
                ex,
            )
            return None

        return self._from_raw(definition, raw)

    @staticmethod
    def _from_raw(definition: RegisterDefinition, raw: int) -> float | int:
        """Convert raw register value to engineering units."""

        if definition.scale == 1:
            return raw
        return raw * definition.scale

    @staticmethod
    def _to_raw(definition: RegisterDefinition, value: float | int) -> int:
        """Convert a scaled value back to raw register units."""

        if definition.scale == 1:
            return int(value)
        return int(round(float(value) / definition.scale))
