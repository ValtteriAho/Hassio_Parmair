"""DataUpdateCoordinator for Parmair integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_MODEL,
    CONF_SLAVE_ID,
    DEFAULT_MODEL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLING_REGISTER_KEYS,
    RegisterDefinition,
    get_register_definition,
    get_registers_for_model,
)

_LOGGER = logging.getLogger(__name__)


class ParmairCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Parmair data from Modbus."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data[CONF_SLAVE_ID]
        self.model = entry.data.get(CONF_MODEL, DEFAULT_MODEL)
        self._registers = get_registers_for_model(self.model)
        self._poll_registers: list[RegisterDefinition] = [
            self._registers[key]
            for key in POLLING_REGISTER_KEYS
            if key in self._registers
        ]

        self._client = ModbusTcpClient(host=self.host, port=self.port)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Parmair via Modbus."""
        try:
            return await self.hass.async_add_executor_job(self._read_modbus_data)
        except ModbusException as err:
            raise UpdateFailed(f"Error communicating with Parmair device: {err}") from err

    def _read_modbus_data(self) -> dict[str, Any]:
        """Read data from Modbus (runs in executor)."""
        if not self._client.connected:
            if not self._client.connect():
                raise ModbusException("Failed to connect to Modbus device")
        
        data: dict[str, Any] = {"model": self.model}

        try:
            for definition in self._poll_registers:
                value = self._read_register_value(definition)
                if value is None:
                    continue
                data[definition.key] = value

            _LOGGER.debug(
                "Read data from Parmair %s (model %s): %s",
                self.host,
                self.model,
                data,
            )
            return data
            
        except Exception as ex:
            _LOGGER.error("Error reading from Modbus: %s", ex)
            raise ModbusException(f"Failed to read data: {ex}") from ex

    def write_register(self, key: str, value: float | int) -> bool:
        """Write a value to a Modbus register respecting scaling."""

        definition = get_register_definition(self.model, key)
        try:
            if not self._client.connected:
                if not self._client.connect():
                    return False

            raw_value = self._to_raw(definition, value)
            try:
                result = self._client.write_register(
                    definition.address, raw_value, unit=self.slave_id
                )
            except TypeError:
                result = self._client.write_register(
                    definition.address, raw_value, slave=self.slave_id
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
        if self._client.connected:
            await self.hass.async_add_executor_job(self._client.close)

    def get_register_definition(self, key: str) -> RegisterDefinition:
        """Expose register metadata for other components."""

        return get_register_definition(self.model, key)

    def _read_register_value(self, definition: RegisterDefinition) -> Any | None:
        """Read and scale a single register."""

        try:
            result = self._client.read_holding_registers(
                definition.address, 1, unit=self.slave_id
            )
        except TypeError:
            result = self._client.read_holding_registers(
                definition.address, 1, slave=self.slave_id
            )
        if not result or result.isError():
            _LOGGER.debug(
                "Failed reading register %s (%s)",
                definition.register_id,
                definition.label,
            )
            return None

        raw = result.registers[0]

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
