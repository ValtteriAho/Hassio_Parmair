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
    CONF_FIRMWARE_VERSION,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_FIRMWARE,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLING_REGISTER_KEYS,
    RegisterDefinition,
    detect_firmware_version,
    get_register_definition,
    get_registers_for_firmware,
)

_LOGGER = logging.getLogger(__name__)


def _set_legacy_unit(client: ModbusTcpClient, unit_id: int) -> None:
    """Best-effort assignment for clients requiring attribute-based unit selection."""

    for attr in ("unit_id", "slave_id", "unit", "slave"):
        if hasattr(client, attr):
            try:
                setattr(client, attr, unit_id)
            except Exception:  # pragma: no cover
                continue


class ParmairCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Parmair data from Modbus."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data[CONF_SLAVE_ID]
        self.model = entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        self.firmware_version = entry.data.get(CONF_FIRMWARE_VERSION, DEFAULT_FIRMWARE)
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self._registers = get_registers_for_firmware(self.firmware_version)
        self._poll_registers: list[RegisterDefinition] = [
            self._registers[key]
            for key in POLLING_REGISTER_KEYS
            if key in self._registers
        ]

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
            
            # Ensure slave_id is set on the client for legacy pymodbus
            _set_legacy_unit(self._client, self.slave_id)
            
            data: dict[str, Any] = {"model": self.model}
            failed_registers = []

            try:
                for definition in self._poll_registers:
                    value = self._read_register_value(definition)
                    if value is None:
                        failed_registers.append(f"{definition.label}({definition.register_id})")
                        continue
                    data[definition.key] = value
                    # Small delay between reads to prevent transaction ID conflicts
                    time.sleep(0.01)
                
                # Check if we need to update firmware version detection
                if "software_version" in data and data["software_version"]:
                    detected_fw = detect_firmware_version(data["software_version"])
                    if detected_fw != self.firmware_version:
                        _LOGGER.info(
                            "Firmware version changed from %s to %s (SW Ver: %s). "
                            "Please reconfigure integration for optimal register mapping.",
                            self.firmware_version,
                            detected_fw,
                            data["software_version"]
                        )
                        data["firmware_version"] = detected_fw

                if failed_registers:
                    _LOGGER.debug(
                        "Failed to read %d registers: %s",
                        len(failed_registers),
                        ", ".join(failed_registers),
                    )
                
                _LOGGER.debug(
                    "Read data from Parmair %s (model %s): %d values - %s",
                    self.host,
                    self.model,
                    len(data) - 1,  # Exclude 'model' key
                    data,
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
        """Write a value to a Modbus register respecting scaling."""

        definition = get_register_definition(self.model, key)
        try:
            with self._lock:
                if not self._client.connected:
                    if not self._client.connect():
                        return False

                raw_value = self._to_raw(definition, value)
                try:
                    result = self._client.write_register(
                        definition.address, raw_value, unit=self.slave_id
                    )
                except TypeError:
                    try:
                        result = self._client.write_register(
                            definition.address, raw_value, slave=self.slave_id
                        )
                    except TypeError:
                        try:
                            result = self._client.write_register(
                                definition.address, raw_value, device_id=self.slave_id
                            )
                        except TypeError:
                            _set_legacy_unit(self._client, self.slave_id)
                            result = self._client.write_register(
                                definition.address, raw_value
                            )
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
        fw_version = self.data.get("firmware_version")
        
        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": self.entry.data.get("name", DEFAULT_NAME),
            "manufacturer": "Parmair",
            "model": self.model,
        }
        
        if sw_version is not None:
            if isinstance(sw_version, (int, float)):
                device_info["sw_version"] = f"{sw_version:.2f}"
            else:
                device_info["sw_version"] = str(sw_version)
        
        if fw_version is not None:
            if isinstance(fw_version, (int, float)):
                device_info["hw_version"] = f"FW {fw_version:.2f}"
            else:
                device_info["hw_version"] = f"FW {fw_version}"
        
        return device_info

    def get_register_definition(self, key: str) -> RegisterDefinition:
        """Expose register metadata for other components."""

        return get_register_definition(self.model, key, self.firmware_version)

    def _read_register_value(self, definition: RegisterDefinition) -> Any | None:
        """Read and scale a single register."""

        try:
            result = self._client.read_holding_registers(
                definition.address, 1, unit=self.slave_id
            )
        except TypeError:
            try:
                result = self._client.read_holding_registers(
                    definition.address, 1, slave=self.slave_id
                )
            except TypeError:
                try:
                    result = self._client.read_holding_registers(
                        definition.address, 1, device_id=self.slave_id
                    )
                except TypeError:
                    _set_legacy_unit(self._client, self.slave_id)
                    try:
                        result = self._client.read_holding_registers(
                            definition.address, 1
                        )
                    except TypeError:
                        result = self._client.read_holding_registers(
                            definition.address
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
