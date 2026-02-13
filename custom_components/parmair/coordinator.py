"""DataUpdateCoordinator for Parmair integration."""
from __future__ import annotations

import logging
import threading
import time
from datetime import timedelta
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_HEATER_TYPE,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_SOFTWARE_VERSION,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HARDWARE_TYPE_MAP_V2,
    HEATER_TYPE_UNKNOWN,
    POLLING_REGISTER_KEYS,
    REGISTERS,
    SOFTWARE_VERSION_1,
    SOFTWARE_VERSION_2,
    SOFTWARE_VERSION_UNKNOWN,
    STATIC_REGISTER_KEYS,
    RegisterDefinition,
    get_register_definition,
    get_registers_for_version,
)

_LOGGER = logging.getLogger(__name__)


def _set_unit_id(client: ModbusTcpClient, unit_id: int) -> None:
    """Set unit ID on the Modbus client for pymodbus 3.x."""
    # Pymodbus 3.x uses 'slave' attribute
    if hasattr(client, 'slave'):
        client.slave = unit_id
    # Fallback to other common attributes
    elif hasattr(client, 'unit_id'):
        client.unit_id = unit_id
    elif hasattr(client, 'slave_id'):
        client.slave_id = unit_id


class ParmairCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Parmair data from Modbus."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data[CONF_SLAVE_ID]
        self.software_version = entry.data.get(CONF_SOFTWARE_VERSION, SOFTWARE_VERSION_1)
        self.heater_type = entry.data.get(CONF_HEATER_TYPE, HEATER_TYPE_UNKNOWN)
        
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        # Get version-specific register map
        self._registers = get_registers_for_version(self.software_version)
        
        # Separate static and dynamic register lists
        self._static_registers: list[RegisterDefinition] = [
            self._registers[key]
            for key in STATIC_REGISTER_KEYS
            if key in self._registers
        ]
        
        self._poll_registers: list[RegisterDefinition] = [
            self._registers[key]
            for key in POLLING_REGISTER_KEYS
            if key in self._registers
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
            # Close and reconnect to flush any stale responses in buffer
            if self._client.connected:
                try:
                    self._client.close()
                except:
                    pass  # Ignore close errors
            
            if not self._client.connect():
                raise ModbusException("Failed to connect to Modbus device")
            
            # Set slave/unit ID on the client
            _set_unit_id(self._client, self.slave_id)
            
            # Longer delay after connect to allow device to stabilize and clear buffers
            time.sleep(0.3)
            
            # Wake-up read: power register (1001) to keep device responsive
            try:
                _ = self._client.read_holding_registers(address=1001, count=1)
            except Exception:
                pass
            time.sleep(0.3)

            # Read static registers once on first poll
            if not self._static_data_read:
                _LOGGER.info("Reading static device information (one-time read)")
                for definition in self._static_registers:
                    value = self._read_register_value(definition)
                    if value is not None:
                        self._static_data[definition.key] = value
                        _LOGGER.debug(
                            "Static register %s: %s",
                            definition.label,
                            value,
                        )
                    time.sleep(0.3)
                self._static_data_read = True
            
            data: dict[str, Any] = {}
            failed_registers = []

            try:
                # Group definitions by address to avoid duplicate reads (e.g. v2 USERSTATECONTROL)
                address_to_definitions: dict[int, list[RegisterDefinition]] = {}
                for definition in self._poll_registers:
                    address_to_definitions.setdefault(definition.address, []).append(definition)

                # Read each unique address once, distribute value to all keys using it
                for address, definitions in address_to_definitions.items():
                    # Use first definition for scaling (shared addresses have same scale)
                    value = self._read_register_value(definitions[0])
                    if value is None:
                        failed_registers.append(f"{definitions[0].label}({definitions[0].register_id})")
                        continue
                    for definition in definitions:
                        data[definition.key] = value
                    # Longer delay between reads to prevent transaction ID conflicts
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
                is_v2 = (
                    self.software_version == SOFTWARE_VERSION_2
                    or str(self.software_version).startswith("2.")
                )
                if is_v2:
                    user_state = data.get("control_state")
                    if user_state is not None:
                        data["home_state"] = 1 if user_state == 2 else 0  # 2=Home
                        data["boost_state"] = 1 if user_state == 3 else 0  # 3=Boost
                        data["overpressure_state"] = 1 if user_state in (4, 5) else 0  # 4=Sauna, 5=Fireplace
                
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
                # Always close after reading to prevent buffer buildup
                try:
                    self._client.close()
                except:
                    pass

    def write_register(self, key: str, value: float | int) -> bool:
        """Write a value to a Modbus register respecting scaling with pymodbus 3.x."""
        definition = get_register_definition(key, self._registers)
        try:
            with self._lock:
                if not self._client.connected:
                    if not self._client.connect():
                        return False
                
                # Set unit ID on client
                _set_unit_id(self._client, self.slave_id)

                raw_value = self._to_raw(definition, value)
                
                # Write using pymodbus 3.x API
                result = self._client.write_register(definition.address, raw_value)
                
                _LOGGER.debug(
                    "Wrote %s to register %s (%d): raw=%d",
                    value, definition.label, definition.address, raw_value
                )
                
                # Small delay after write to allow device to process
                time.sleep(0.3)
                
                return not result.isError() if hasattr(result, 'isError') else result is not None
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
            is_v2 = (
                self.software_version == SOFTWARE_VERSION_2
                or str(self.software_version).startswith("2.")
            )
            model_num = HARDWARE_TYPE_MAP_V2.get(hw_int, hw_int) if is_v2 else hw_int
            model = f"MAC {model_num}"
        
        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self.entry.data.get("name", DEFAULT_NAME),
            "manufacturer": "Parmair",
            "model": model,
        }
        
        # Add software version
        if sw_version is not None:
            if isinstance(sw_version, (int, float)):
                device_info["sw_version"] = f"{sw_version:.2f}"
            else:
                device_info["sw_version"] = str(sw_version)
        
        return device_info

    def get_register_definition(self, key: str) -> RegisterDefinition:
        """Expose register metadata for other components."""
        return get_register_definition(key, self._registers)

    def _read_register_value(self, definition: RegisterDefinition) -> Any | None:
        """Read and scale a single register with pymodbus 3.x."""
        try:
            # Read using pymodbus 3.x API (unit ID already set on client)
            result = self._client.read_holding_registers(
                address=definition.address, count=1
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
            elif isinstance(result, (list, tuple)):
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
