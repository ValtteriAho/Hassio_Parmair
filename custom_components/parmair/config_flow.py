"""Config flow for Parmair integration."""
from __future__ import annotations

import logging
import time
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_integration


def _set_legacy_unit(client: ModbusTcpClient, unit_id: int) -> None:
    """Best-effort assignment for clients requiring attribute-based unit selection."""

    for attr in ("unit_id", "slave_id", "unit", "slave"):
        if hasattr(client, attr):
            try:
                setattr(client, attr, unit_id)
            except Exception:  # pragma: no cover
                continue


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
    HEATER_TYPE_ELECTRIC,
    HEATER_TYPE_NONE,
    HEATER_TYPE_UNKNOWN,
    HEATER_TYPE_WATER,
    REG_HEATER_TYPE,
    REG_POWER,
    REG_SOFTWARE_VERSION,
    SOFTWARE_VERSION_1,
    SOFTWARE_VERSION_2,
    SOFTWARE_VERSION_UNKNOWN,
    get_register_definition,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=247)
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=300)
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect and detect device info."""
    client = ModbusTcpClient(host=data[CONF_HOST], port=data[CONF_PORT])
    
    def _connect():
        """Connect to the Modbus device."""
        return client.connect()
    
    # Run the blocking connection in executor
    connected = await hass.async_add_executor_job(_connect)
    
    if not connected:
        client.close()
        raise CannotConnect
    
    # Auto-detect software version and heater type with retry logic
    def _detect_device_info():
        """Detect software version and heater type from device with retries."""
        detected_sw_version = SOFTWARE_VERSION_UNKNOWN
        detected_heater_type = HEATER_TYPE_UNKNOWN
        
        # Try detection multiple times with increasing delays
        for attempt in range(3):
            if attempt > 0:
                # Wait longer between retries
                delay = 0.2 * attempt  # 0.2s, 0.4s
                _LOGGER.info("Retrying detection (attempt %d/3) after %.1fs delay", attempt + 1, delay)
                time.sleep(delay)
            else:
                # Initial delay after connection
                time.sleep(0.15)
            
            # Try to read software version
            try:
                sw_reg = get_register_definition(REG_SOFTWARE_VERSION)
                try:
                    # Try modern pymodbus with keyword arguments
                    result = client.read_holding_registers(
                        address=sw_reg.address, count=1, slave=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    try:
                        # Try with 'unit' instead of 'slave'
                        result = client.read_holding_registers(
                            address=sw_reg.address, count=1, unit=data[CONF_SLAVE_ID]
                        )
                    except TypeError:
                        # Try older versions with positional + keyword
                        try:
                            result = client.read_holding_registers(
                                sw_reg.address, 1, unit=data[CONF_SLAVE_ID]
                            )
                        except TypeError:
                            try:
                                result = client.read_holding_registers(
                                    sw_reg.address, 1, slave=data[CONF_SLAVE_ID]
                                )
                            except TypeError:
                                _set_legacy_unit(client, data[CONF_SLAVE_ID])
                                result = client.read_holding_registers(
                                    sw_reg.address, 1
                                )
                
                # Check if read was successful
                if result and not (hasattr(result, "isError") and result.isError()):
                    # Extract and scale software version
                    if hasattr(result, "registers"):
                        raw_sw = result.registers[0]
                    elif isinstance(result, (list, tuple)):
                        raw_sw = result[0]
                    else:
                        raw_sw = result
                    
                    sw_version = raw_sw * sw_reg.scale
                    
                    # Determine version family
                    if sw_version >= 2.0:
                        detected_sw_version = SOFTWARE_VERSION_2
                    elif sw_version >= 1.0:
                        detected_sw_version = SOFTWARE_VERSION_1
                    else:
                        detected_sw_version = SOFTWARE_VERSION_UNKNOWN
                    
                    if detected_sw_version != SOFTWARE_VERSION_UNKNOWN:
                        _LOGGER.info(
                            "Auto-detected software version: %.2f, family: %s (attempt %d/3)",
                            sw_version,
                            detected_sw_version,
                            attempt + 1,
                        )
                        break  # Success, exit retry loop
                else:
                    _LOGGER.debug("Attempt %d/3: Failed to read software version - invalid response", attempt + 1)
            except Exception as ex:
                _LOGGER.debug("Attempt %d/3: Could not auto-detect software version: %s", attempt + 1, ex)
        
        # Try to read heater type with same retry logic
        for attempt in range(3):
            if attempt > 0:
                delay = 0.1 * attempt
                time.sleep(delay)
            
            try:
                heater_reg = get_register_definition(REG_HEATER_TYPE)
                try:
                    # Try modern pymodbus with keyword arguments
                    result = client.read_holding_registers(
                        address=heater_reg.address, count=1, slave=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    try:
                        # Try with 'unit' instead of 'slave'
                        result = client.read_holding_registers(
                            address=heater_reg.address, count=1, unit=data[CONF_SLAVE_ID]
                        )
                    except TypeError:
                        # Try older versions with positional + keyword
                        try:
                            result = client.read_holding_registers(
                                heater_reg.address, 1, unit=data[CONF_SLAVE_ID]
                            )
                        except TypeError:
                            try:
                                result = client.read_holding_registers(
                                    heater_reg.address, 1, slave=data[CONF_SLAVE_ID]
                                )
                            except TypeError:
                                _set_legacy_unit(client, data[CONF_SLAVE_ID])
                                result = client.read_holding_registers(
                                    heater_reg.address, 1
                                )
            
            # Check if read was successful
            if result and not (hasattr(result, "isError") and result.isError()):
                # Extract heater type value
                if hasattr(result, "registers"):
                    heater_type = result.registers[0]
                elif isinstance(result, (list, tuple)):
                    heater_type = result[0]
                else:
                    heater_type = result
                
                detected_heater_type = int(heater_type)
                
                heater_names = {
                    HEATER_TYPE_NONE: "None",
                    HEATER_TYPE_WATER: "Water",
                    HEATER_TYPE_ELECTRIC: "Electric",
                }
                
                _LOGGER.info(
                    "Auto-detected heater type: %s (%s) (attempt %d/3)",
                    detected_heater_type,
                    heater_names.get(detected_heater_type, "Unknown"),
                    attempt + 1,
                )
                break  # Success, exit retry loop
            else:
                _LOGGER.debug("Attempt %d/3: Failed to read heater type - invalid response", attempt + 1)
        except Exception as ex:
            _LOGGER.debug("Attempt %d/3: Could not auto-detect heater type: %s", attempt + 1, ex)
        
        # Use defaults if detection failed after all retries
        if detected_sw_version == SOFTWARE_VERSION_UNKNOWN:
            detected_sw_version = SOFTWARE_VERSION_1
            _LOGGER.warning(
                "Auto-detection failed after 3 attempts, defaulting to software version 1.x"
            )
        
        if detected_heater_type == HEATER_TYPE_UNKNOWN:
            detected_heater_type = HEATER_TYPE_NONE
            _LOGGER.warning(
                "Heater type detection failed after 3 attempts, defaulting to None (no heater)"
            )
        
        return detected_sw_version, detected_heater_type
    
    detected_sw_version, detected_heater_type = await hass.async_add_executor_job(_detect_device_info)
    
    # Verify communication by reading power register
    power_register = get_register_definition(REG_POWER)
    
    # Try to read a register to verify communication
    def _read_test():
        """Test reading from the device."""
        try:
            result = client.read_holding_registers(
                power_register.address, 1, unit=data[CONF_SLAVE_ID]
            )
        except TypeError:
            try:
                # Older pymodbus versions expect the keyword 'slave'
                result = client.read_holding_registers(
                    power_register.address, 1, slave=data[CONF_SLAVE_ID]
                )
            except TypeError:
                try:
                    # Even older pymodbus versions expect 'device_id' keyword
                    result = client.read_holding_registers(
                        power_register.address, 1, device_id=data[CONF_SLAVE_ID]
                    )
                except TypeError:
                    # Very old clients require positional arguments only or attribute assignment
                    _set_legacy_unit(client, data[CONF_SLAVE_ID])
                    try:
                        result = client.read_holding_registers(
                            power_register.address, 1
                        )
                    except TypeError:
                        result = client.read_holding_registers(
                            power_register.address
                        )
        return not result.isError() if hasattr(result, 'isError') else result is not None
    
    try:
        success = await hass.async_add_executor_job(_read_test)
        if not success:
            raise CannotConnect
    finally:
        client.close()
    
    return {
        "title": data[CONF_NAME],
        CONF_SOFTWARE_VERSION: detected_sw_version,
        CONF_HEATER_TYPE: detected_heater_type,
    }


class ParmairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parmair."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._integration_version: str | None = None
        self._user_input: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if self._integration_version is None:
            try:
                integration = await async_get_integration(self.hass, DOMAIN)
                self._integration_version = integration.version or "unknown"
            except Exception:  # pragma: no cover - fallback if manifest missing
                self._integration_version = "unknown"

        if user_input is not None:
            # Create unique ID based on host and slave ID
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}_{user_input[CONF_SLAVE_ID]}"
            )
            self._abort_if_unique_id_configured()
            
            try:
                info = await validate_connection(self.hass, user_input)
                
                # Store detected software version and heater type
                user_input[CONF_SOFTWARE_VERSION] = info[CONF_SOFTWARE_VERSION]
                user_input[CONF_HEATER_TYPE] = info[CONF_HEATER_TYPE]
                
                # Create entry with detected or default values
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "version": self._integration_version or "unknown",
            },
        )

    # Manual configuration step removed - now uses auto-detection with defaults
