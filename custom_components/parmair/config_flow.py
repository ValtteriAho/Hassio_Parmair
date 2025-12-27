"""Config flow for Parmair integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_MODEL,
    CONF_SLAVE_ID,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    REG_POWER,
    SUPPORTED_MODELS,
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
        vol.Required(CONF_MODEL, default=DEFAULT_MODEL): vol.In(SUPPORTED_MODELS),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = ModbusTcpClient(host=data[CONF_HOST], port=data[CONF_PORT])
    model = data.get(CONF_MODEL, DEFAULT_MODEL)
    power_register = get_register_definition(model, REG_POWER)
    
    def _connect():
        """Connect to the Modbus device."""
        return client.connect()
    
    # Run the blocking connection in executor
    connected = await hass.async_add_executor_job(_connect)
    
    if not connected:
        client.close()
        raise CannotConnect
    
    # Try to read a register to verify communication
    def _read_test():
        """Test reading from the device."""
        try:
            result = client.read_holding_registers(
                power_register.address, 1, unit=data[CONF_SLAVE_ID]
            )
        except TypeError:
            # Older pymodbus versions expect the keyword 'slave'
            result = client.read_holding_registers(
                power_register.address, 1, slave=data[CONF_SLAVE_ID]
            )
        return not result.isError() if hasattr(result, 'isError') else result is not None
    
    try:
        success = await hass.async_add_executor_job(_read_test)
        if not success:
            raise CannotConnect
    finally:
        client.close()
    
    return {"title": data[CONF_NAME], "model": model}


class ParmairConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Parmair."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Create unique ID based on host and slave ID
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}_{user_input[CONF_SLAVE_ID]}"
            )
            self._abort_if_unique_id_configured()
            
            try:
                info = await validate_connection(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
