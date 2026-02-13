"""Config flow for Parmair integration."""

from __future__ import annotations

import logging
import time
from typing import Any

import homeassistant.helpers.config_validation as cv
import pymodbus
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.loader import async_get_integration
from pymodbus.client import ModbusTcpClient

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
    HEATER_TYPE_ELECTRIC,
    HEATER_TYPE_NONE,
    HEATER_TYPE_UNKNOWN,
    HEATER_TYPE_WATER,
    REG_POWER,
    SOFTWARE_VERSION_1,
    SOFTWARE_VERSION_2,
    SOFTWARE_VERSION_UNKNOWN,
    get_register_definition,
    get_registers_for_version,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
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
        detected_firmware_registers = None  # Track which address set worked
        detected_machine_type = None  # Track detected machine type value

        # Log pymodbus version for debugging
        pymodbus_version = getattr(pymodbus, "__version__", "unknown")
        _LOGGER.info("Starting device auto-detection... (pymodbus version: %s)", pymodbus_version)

        # Longer initial delay after connection for device to stabilize during setup
        time.sleep(1.0)

        # Two-register consensus detection for robust firmware identification
        # Each firmware version has unique SOFTWARE_VERSION and VENT_MACHINE addresses
        # Both registers must be readable for positive identification
        detection_sets = [
            {
                "firmware": "2.xx",
                "sw_address": 1015,  # SOFTWARE_VERSION for firmware 2.xx
                "vm_address": 1125,  # VENT_MACHINE for firmware 2.xx
                "sw_range": (2.0, 2.99),
            },
            {
                "firmware": "1.xx",
                "sw_address": 1018,  # SOFTWARE_VERSION for firmware 1.xx
                "vm_address": 1244,  # VENT_MACHINE for firmware 1.xx
                "sw_range": (1.0, 1.99),
            },
        ]

        unit_id = data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

        def _read_register(address: int) -> int | None:
            """Read a single register (works with any pymodbus 3.x: device_id= or slave=)."""
            try:
                result = pymodbus_compat.read_holding_registers(client, address, 1, unit_id)
                # Check if read was successful
                if result and not (hasattr(result, "isError") and result.isError()):
                    # Extract register value
                    if hasattr(result, "registers"):
                        return result.registers[0]
                    elif isinstance(result, list | tuple):
                        return result[0]
                    else:
                        return result
            except Exception as ex:
                _LOGGER.debug("Failed to read register at address %d: %s", address, ex)
            return None

        # Warm-up: Read universal register (1001 - power) repeatedly until device responds
        # This "wakes up" the device and ensures it's ready for version detection
        _LOGGER.debug("Warming up connection by reading power register (1001)...")
        warmup_success = False
        for attempt in range(5):  # Try up to 5 times
            warmup_value = _read_register(1001)
            if warmup_value is not None:
                _LOGGER.debug("Warm-up successful on attempt %d, device is responding", attempt + 1)
                warmup_success = True
                break
            _LOGGER.debug("Warm-up attempt %d failed, waiting 500ms...", attempt + 1)
            time.sleep(0.5)

        if not warmup_success:
            _LOGGER.warning("Device warm-up failed after 5 attempts, detection may fail")

        # Try each firmware detection set
        for detection_set in detection_sets:
            firmware = detection_set["firmware"]
            sw_address = detection_set["sw_address"]
            vm_address = detection_set["vm_address"]
            sw_min, sw_max = detection_set["sw_range"]

            _LOGGER.debug(
                "Trying two-register consensus detection for firmware %s (SW:%d, VM:%d)",
                firmware,
                sw_address,
                vm_address,
            )

            # Read both registers with delay between reads
            raw_sw = _read_register(sw_address)
            time.sleep(0.2)  # Delay between register reads during detection
            raw_vm = _read_register(vm_address)
            time.sleep(0.1)  # Small delay before validation

            # Validate both registers
            sw_valid = False
            vm_readable = False

            if raw_sw is not None and 0 < raw_sw < 10000:
                sw_version = raw_sw * 0.01
                if sw_min <= sw_version <= sw_max:
                    sw_valid = True
                    _LOGGER.debug(
                        "Address %d returned valid version %.2f for firmware %s",
                        sw_address,
                        sw_version,
                        firmware,
                    )
                else:
                    _LOGGER.debug(
                        "Address %d version %.2f outside expected range %.2f-%.2f",
                        sw_address,
                        sw_version,
                        sw_min,
                        sw_max,
                    )
            else:
                _LOGGER.debug("Address %d returned invalid or no data", sw_address)

            if raw_vm is not None:
                vm_readable = True
                _LOGGER.debug("Address %d returned machine type value %d", vm_address, raw_vm)
            else:
                _LOGGER.debug("Address %d returned no data", vm_address)

            # Both registers must be readable for consensus
            if sw_valid and vm_readable:
                if firmware == "2.xx":
                    detected_sw_version = SOFTWARE_VERSION_2
                else:
                    detected_sw_version = SOFTWARE_VERSION_1

                detected_firmware_registers = firmware
                detected_machine_type = raw_vm  # Store detected machine type

                _LOGGER.info(
                    "Firmware %s confirmed by two-register consensus: "
                    "SW version %.2f (addr %d) + Machine type %d (addr %d)",
                    firmware,
                    sw_version,
                    sw_address,
                    raw_vm,
                    vm_address,
                )
                break  # Success, exit detection loop
            else:
                _LOGGER.debug(
                    "Firmware %s consensus failed (SW valid: %s, VM readable: %s)",
                    firmware,
                    sw_valid,
                    vm_readable,
                )

        # If software version was not detected, return None to trigger manual selection
        if detected_sw_version == SOFTWARE_VERSION_UNKNOWN:
            _LOGGER.warning("Could not auto-detect software version via two-register consensus")
            # Return None to indicate detection failed - user will be asked to select manually
            return None

        # Now detect heater type using the correct address for detected firmware
        heater_addresses = []
        if detected_firmware_registers == "2.xx":
            # Firmware 2.xx: heater type at address 1127
            heater_addresses = [(1127, "2.xx")]
        else:
            # Firmware 1.xx: heater type at address 1240
            heater_addresses = [(1240, "1.xx")]

        # Try to read heater type from the correct address
        for heater_address, fw_label in heater_addresses:
            _LOGGER.debug(
                "Trying heater type detection with address %d (firmware %s)",
                heater_address,
                fw_label,
            )

            raw_heater = _read_register(heater_address)

            # Validate heater type (0=Water, 1=Electric, 2=None)
            if raw_heater is not None and raw_heater in [0, 1, 2]:
                detected_heater_type = int(raw_heater)

                heater_names = {
                    HEATER_TYPE_NONE: "None",
                    HEATER_TYPE_WATER: "Water",
                    HEATER_TYPE_ELECTRIC: "Electric",
                }

                _LOGGER.info(
                    "Auto-detected heater type: %s (%s) from address %d (firmware %s)",
                    detected_heater_type,
                    heater_names.get(detected_heater_type, "Unknown"),
                    heater_address,
                    fw_label,
                )
                break  # Success, exit address loop
            else:
                _LOGGER.debug(
                    "Address %d returned invalid heater type: %s", heater_address, raw_heater
                )

        # Use defaults if detection failed
        if detected_heater_type == HEATER_TYPE_UNKNOWN:
            detected_heater_type = HEATER_TYPE_NONE
            _LOGGER.warning("Heater type detection failed, defaulting to None (no heater)")

        # Log final detection summary
        _LOGGER.info(
            "=== Detection Complete === Firmware: %s | Machine Type: %s | Heater: %s",
            detected_sw_version,
            detected_machine_type if detected_machine_type is not None else "Unknown",
            {
                HEATER_TYPE_NONE: "None",
                HEATER_TYPE_WATER: "Water",
                HEATER_TYPE_ELECTRIC: "Electric",
            }.get(detected_heater_type, "Unknown"),
        )

        return detected_sw_version, detected_heater_type

    detection_result = await hass.async_add_executor_job(_detect_device_info)

    # If detection returned None, firmware version couldn't be determined
    if detection_result is None:
        client.close()
        return None  # Signal to caller that manual selection is needed

    detected_sw_version, detected_heater_type = detection_result

    # Verify communication by reading power register (use version-specific address)
    registers = get_registers_for_version(detected_sw_version)
    power_register = get_register_definition(REG_POWER, registers)

    # Try to read a register to verify communication
    def _read_test():
        """Test reading from the device (works with any pymodbus 3.x)."""
        try:
            unit_id = data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
            result = pymodbus_compat.read_holding_registers(
                client, power_register.address, 1, unit_id
            )
            return not result.isError() if hasattr(result, "isError") else result is not None
        except Exception as ex:
            _LOGGER.debug("Test read failed: %s", ex)
            return False

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
        self._detection_failed: bool = False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if self._integration_version is None:
            try:
                integration = await async_get_integration(self.hass, DOMAIN)
                self._integration_version = integration.version or "unknown"
            except Exception:  # pragma: no cover - fallback if manifest missing
                self._integration_version = "unknown"

        if user_input is not None:
            # Always use slave ID 0 (Parmair devices use unit 0)
            user_input[CONF_SLAVE_ID] = DEFAULT_SLAVE_ID

            # Create unique ID based on host and slave ID
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}_{user_input[CONF_SLAVE_ID]}")
            self._abort_if_unique_id_configured()

            try:
                info = await validate_connection(self.hass, user_input)

                # If info is None, detection failed - ask user to manually select
                if info is None:
                    self._user_input = user_input
                    self._detection_failed = True
                    return await self.async_step_manual_version()

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

    async def async_step_manual_version(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual software version selection when auto-detection fails."""
        if user_input is not None:
            # Combine stored connection info with manual selections
            final_data = {**self._user_input, **user_input}

            # Create entry with manually selected version
            return self.async_create_entry(title=final_data[CONF_NAME], data=final_data)

        # Show form for manual selection
        return self.async_show_form(
            step_id="manual_version",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SOFTWARE_VERSION, default=SOFTWARE_VERSION_1): vol.In(
                        {
                            SOFTWARE_VERSION_1: "Software 1.xx",
                            SOFTWARE_VERSION_2: "Software 2.xx",
                        }
                    ),
                    vol.Required(CONF_HEATER_TYPE, default=HEATER_TYPE_NONE): vol.In(
                        {
                            HEATER_TYPE_NONE: "None",
                            HEATER_TYPE_WATER: "Water",
                            HEATER_TYPE_ELECTRIC: "Electric",
                        }
                    ),
                }
            ),
            description_placeholders={
                "info": "Auto-detection failed. Please select your device's software version and heater type manually.",
            },
        )

    @staticmethod
    async def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return ParmairOptionsFlowHandler(config_entry)


class ParmairOptionsFlowHandler(config_entries.OptionsFlowWithConfigEntry):
    """Handle Parmair options (change host, port, name, scan interval, software version, heater type)."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        options = self.config_entry.options or {}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=options.get(CONF_HOST, data.get(CONF_HOST, "")),
                    ): cv.string,
                    vol.Required(
                        CONF_PORT,
                        default=options.get(CONF_PORT, data.get(CONF_PORT, DEFAULT_PORT)),
                    ): cv.port,
                    vol.Optional(
                        CONF_NAME,
                        default=options.get(CONF_NAME, data.get(CONF_NAME, DEFAULT_NAME)),
                    ): cv.string,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=options.get(
                            CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                    vol.Required(
                        CONF_SOFTWARE_VERSION,
                        default=options.get(
                            CONF_SOFTWARE_VERSION,
                            data.get(CONF_SOFTWARE_VERSION, SOFTWARE_VERSION_1),
                        ),
                    ): vol.In(
                        {
                            SOFTWARE_VERSION_1: "Software 1.xx",
                            SOFTWARE_VERSION_2: "Software 2.xx",
                        }
                    ),
                    vol.Required(
                        CONF_HEATER_TYPE,
                        default=options.get(
                            CONF_HEATER_TYPE, data.get(CONF_HEATER_TYPE, HEATER_TYPE_NONE)
                        ),
                    ): vol.In(
                        {
                            HEATER_TYPE_NONE: "None",
                            HEATER_TYPE_WATER: "Water",
                            HEATER_TYPE_ELECTRIC: "Electric",
                        }
                    ),
                }
            ),
        )
