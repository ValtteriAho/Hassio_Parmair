"""Constants and register metadata for the Parmair integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

DOMAIN = "parmair"

# Configuration
CONF_SLAVE_ID = "slave_id"
CONF_MODEL = "model"
CONF_FIRMWARE_VERSION = "firmware_version"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "Parmair MAC"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# Supported hardware profiles
MODEL_MAC80 = "MAC80"
MODEL_MAC100 = "MAC100"
MODEL_MAC150 = "MAC150"
MODEL_UNKNOWN = "Unknown"
DEFAULT_MODEL = MODEL_MAC80

# Firmware versions (based on MULTI_SW_VER register)
FIRMWARE_V1 = "1.x"  # Firmware 1.xx (Modbus spec 1.87)
FIRMWARE_V2 = "2.x"  # Firmware 2.xx (Modbus spec 2.x - placeholder)
DEFAULT_FIRMWARE = FIRMWARE_V1

# Hardware type code to model mapping (from VENT_MACHINE register)
HARDWARE_TYPE_MAP = {
    1: MODEL_MAC80,
    # Add more mappings as hardware codes are discovered
}


@dataclass(frozen=True)
class RegisterDefinition:
    """Describe a Modbus holding register used by the integration."""

    key: str
    address: int  # zero-based address expected by pymodbus
    label: str
    scale: float = 1.0
    writable: bool = False
    optional: bool = False
    description: str | None = None

    @property
    def register_id(self) -> int:
        """Return the register ID (Address - 1000 = Register ID)."""

        return self.address - 1000


# Register keys
REG_HARDWARE_TYPE = "hardware_type"
REG_SOFTWARE_VERSION = "software_version"
REG_POWER = "power"
REG_CONTROL_STATE = "control_state"
REG_SPEED_CONTROL = "speed_control"
REG_FRESH_AIR_TEMP = "fresh_air_temp"
REG_SUPPLY_AFTER_RECOVERY_TEMP = "supply_after_recovery_temp"
REG_SUPPLY_TEMP = "supply_temp"
REG_EXHAUST_TEMP = "exhaust_temp"
REG_WASTE_TEMP = "waste_temp"
REG_EXHAUST_TEMP_SETPOINT = "exhaust_temp_setpoint"
REG_SUPPLY_TEMP_SETPOINT = "supply_temp_setpoint"
REG_HOME_SPEED = "home_speed"
REG_AWAY_SPEED = "away_speed"
REG_BOOST_SETTING = "boost_setting"
REG_HOME_STATE = "home_state"
REG_BOOST_STATE = "boost_state"
REG_BOOST_TIMER = "boost_timer"
REG_HUMIDITY = "humidity"
REG_HUMIDITY_24H_AVG = "humidity_24h_avg"
REG_CO2 = "co2"
REG_ALARM_COUNT = "alarm_count"
REG_SUM_ALARM = "sum_alarm"
REG_ALARMS_STATE = "alarms_state"

# Switch register keys
REG_SUMMER_MODE = "summer_mode"
REG_TIME_PROGRAM_ENABLE = "time_program_enable"
REG_HEATER_ENABLE = "heater_enable"

# Button register keys
REG_ACKNOWLEDGE_ALARMS = "acknowledge_alarms"
REG_FILTER_REPLACED = "filter_replaced"

# Select register keys
REG_HEATER_TYPE = "heater_type"

# Additional number register keys
REG_SUMMER_MODE_TEMP_LIMIT = "summer_mode_temp_limit"
REG_FILTER_INTERVAL = "filter_interval"

# Additional sensor register keys
REG_HEAT_RECOVERY_EFFICIENCY = "heat_recovery_efficiency"
REG_OVERPRESSURE_TIMER = "overpressure_timer"
REG_DEFROST_STATE = "defrost_state"
REG_SUPPLY_FAN_SPEED = "supply_fan_speed"
REG_EXHAUST_FAN_SPEED = "exhaust_fan_speed"
REG_FILTER_STATE = "filter_state"


def _build_v1_registers() -> Dict[str, RegisterDefinition]:
    """Return register map for firmware version 1.xx (Modbus spec 1.87)."""

    return {
        REG_HARDWARE_TYPE: RegisterDefinition(REG_HARDWARE_TYPE, 1244, "VENT_MACHINE"),
        REG_SOFTWARE_VERSION: RegisterDefinition(REG_SOFTWARE_VERSION, 1018, "MULTI_SW_VER", scale=0.01),
        REG_POWER: RegisterDefinition(REG_POWER, 1208, "POWER_BTN_FI", writable=True),
        REG_CONTROL_STATE: RegisterDefinition(
            REG_CONTROL_STATE, 1185, "IV01_CONTROLSTATE_FO", writable=True
        ),
        REG_SPEED_CONTROL: RegisterDefinition(
            REG_SPEED_CONTROL, 1187, "IV01_SPEED_FOC", writable=True
        ),
        REG_FRESH_AIR_TEMP: RegisterDefinition(
            REG_FRESH_AIR_TEMP, 1020, "TE01_M", scale=0.1
        ),
        REG_SUPPLY_AFTER_RECOVERY_TEMP: RegisterDefinition(
            REG_SUPPLY_AFTER_RECOVERY_TEMP, 1022, "TE05_M", scale=0.1
        ),
        REG_SUPPLY_TEMP: RegisterDefinition(
            REG_SUPPLY_TEMP, 1023, "TE10_M", scale=0.1
        ),
        REG_EXHAUST_TEMP: RegisterDefinition(
            REG_EXHAUST_TEMP, 1024, "TE30_M", scale=0.1
        ),
        REG_WASTE_TEMP: RegisterDefinition(
            REG_WASTE_TEMP, 1025, "TE31_M", scale=0.1
        ),
        REG_EXHAUST_TEMP_SETPOINT: RegisterDefinition(
            REG_EXHAUST_TEMP_SETPOINT, 1060, "TE30_S", scale=0.1, writable=True
        ),
        REG_SUPPLY_TEMP_SETPOINT: RegisterDefinition(
            REG_SUPPLY_TEMP_SETPOINT, 1065, "TE10_S", scale=0.1, writable=True
        ),
        REG_HOME_SPEED: RegisterDefinition(
            REG_HOME_SPEED, 1104, "HOME_SPEED_S", writable=True
        ),
        REG_AWAY_SPEED: RegisterDefinition(
            REG_AWAY_SPEED, 1105, "AWAY_SPEED_S", writable=True
        ),
        REG_BOOST_SETTING: RegisterDefinition(
            REG_BOOST_SETTING, 1117, "BOOST_SETTING_S", writable=True
        ),
        REG_HOME_STATE: RegisterDefinition(
            REG_HOME_STATE, 1200, "HOME_STATE_FI"
        ),
        REG_BOOST_STATE: RegisterDefinition(
            REG_BOOST_STATE, 1201, "BOOST_STATE_FI"
        ),
        REG_BOOST_TIMER: RegisterDefinition(
            REG_BOOST_TIMER, 1202, "BOOST_TIMER_FM"
        ),
        REG_HUMIDITY: RegisterDefinition(
            REG_HUMIDITY, 1180, "MEXX_FM", optional=True
        ),
        REG_HUMIDITY_24H_AVG: RegisterDefinition(
            REG_HUMIDITY_24H_AVG, 1192, "ME05_AVG_FM", scale=0.1, optional=True
        ),
        REG_CO2: RegisterDefinition(
            REG_CO2, 1031, "QE20_M", optional=True
        ),
        REG_ALARM_COUNT: RegisterDefinition(
            REG_ALARM_COUNT, 1004, "ALARM_COUNT"
        ),
        REG_SUM_ALARM: RegisterDefinition(
            REG_SUM_ALARM, 1005, "SUM_ALARM"
        ),
        REG_ALARMS_STATE: RegisterDefinition(
            REG_ALARMS_STATE, 1206, "ALARMS_STATE_FI"
        ),
        REG_SUMMER_MODE: RegisterDefinition(
            REG_SUMMER_MODE, 1079, "SUMMER_MODE_S", writable=True
        ),
        REG_TIME_PROGRAM_ENABLE: RegisterDefinition(
            REG_TIME_PROGRAM_ENABLE, 1108, "TP_ENABLE_S", writable=True
        ),
        REG_HEATER_ENABLE: RegisterDefinition(
            REG_HEATER_ENABLE, 1109, "HEATER_ENABLE_S", writable=True
        ),
        # Button registers
        REG_ACKNOWLEDGE_ALARMS: RegisterDefinition(
            REG_ACKNOWLEDGE_ALARMS, 1003, "ACK_ALARMS", writable=True
        ),
        REG_FILTER_REPLACED: RegisterDefinition(
            REG_FILTER_REPLACED, 1205, "FILTER_STATE_FI", writable=True
        ),
        # Select registers
        REG_HEATER_TYPE: RegisterDefinition(
            REG_HEATER_TYPE, 1240, "HEAT_RADIATOR_TYPE", writable=True
        ),
        # Additional number registers
        REG_SUMMER_MODE_TEMP_LIMIT: RegisterDefinition(
            REG_SUMMER_MODE_TEMP_LIMIT, 1078, "SUMMER_MODE_TE01_LIMIT", scale=0.1, writable=True
        ),
        REG_FILTER_INTERVAL: RegisterDefinition(
            REG_FILTER_INTERVAL, 1085, "FILTER_INTERVAL_S", writable=True
        ),
        # Additional sensor registers
        REG_HEAT_RECOVERY_EFFICIENCY: RegisterDefinition(
            REG_HEAT_RECOVERY_EFFICIENCY, 1190, "FG50_EA_M", scale=0.1
        ),
        REG_OVERPRESSURE_TIMER: RegisterDefinition(
            REG_OVERPRESSURE_TIMER, 1204, "OVERP_TIMER_FM"
        ),
        REG_DEFROST_STATE: RegisterDefinition(
            REG_DEFROST_STATE, 1183, "DFRST_FI"
        ),
        REG_SUPPLY_FAN_SPEED: RegisterDefinition(
            REG_SUPPLY_FAN_SPEED, 1040, "TF10_Y", scale=0.1
        ),
        REG_EXHAUST_FAN_SPEED: RegisterDefinition(
            REG_EXHAUST_FAN_SPEED, 1042, "PF30_Y", scale=0.1
        ),
        REG_FILTER_STATE: RegisterDefinition(
            REG_FILTER_STATE, 1205, "FILTER_STATE_FI"
        ),
    }


def _build_v2_registers() -> Dict[str, RegisterDefinition]:
    """Return register map for firmware version 2.xx (Modbus spec 2.x - PLACEHOLDER).
    
    Note: This is a placeholder for future firmware 2.x support.
    Register mappings may differ from v1.x and will be updated when
    the Modbus specification for firmware 2.x becomes available.
    
    Currently mirrors v1.x registers as a fallback.
    """
    # TODO: Update with actual v2.x register mappings when specification is available
    return _build_v1_registers()


# Build register maps for each firmware version
V1_REGISTERS = _build_v1_registers()
V2_REGISTERS = _build_v2_registers()

# Firmware version to register map
FIRMWARE_REGISTER_MAP: Dict[str, Dict[str, RegisterDefinition]] = {
    FIRMWARE_V1: V1_REGISTERS,
    FIRMWARE_V2: V2_REGISTERS,
}

# Legacy: Keep model-based maps for backward compatibility
MAC80_REGISTERS = V1_REGISTERS
MAC100_REGISTERS = V1_REGISTERS
MAC150_REGISTERS = V1_REGISTERS

REGISTER_MAP: Dict[str, Dict[str, RegisterDefinition]] = {
    MODEL_MAC80: MAC80_REGISTERS,
    MODEL_MAC100: MAC100_REGISTERS,
    MODEL_MAC150: MAC150_REGISTERS,
}

SUPPORTED_MODELS = tuple(REGISTER_MAP.keys())
SUPPORTED_FIRMWARES = tuple(FIRMWARE_REGISTER_MAP.keys())

# Ordered list of registers to poll on each update.
POLLING_REGISTER_KEYS = (
    REG_SOFTWARE_VERSION,
    REG_POWER,
    REG_CONTROL_STATE,
    REG_SPEED_CONTROL,
    REG_FRESH_AIR_TEMP,
    REG_SUPPLY_AFTER_RECOVERY_TEMP,
    REG_SUPPLY_TEMP,
    REG_EXHAUST_TEMP,
    REG_WASTE_TEMP,
    REG_EXHAUST_TEMP_SETPOINT,
    REG_SUPPLY_TEMP_SETPOINT,
    REG_HOME_SPEED,
    REG_AWAY_SPEED,
    REG_HOME_STATE,
    REG_BOOST_STATE,
    REG_BOOST_TIMER,
    REG_HUMIDITY,
    REG_HUMIDITY_24H_AVG,
    REG_CO2,
    REG_ALARM_COUNT,
    REG_SUM_ALARM,
    REG_ALARMS_STATE,
    REG_HEAT_RECOVERY_EFFICIENCY,
    REG_OVERPRESSURE_TIMER,
    REG_DEFROST_STATE,
    REG_SUPPLY_FAN_SPEED,
    REG_EXHAUST_FAN_SPEED,
    REG_FILTER_STATE,
)


def get_registers_for_model(model: str) -> Dict[str, RegisterDefinition]:
    """Return the register map for the requested model (legacy, uses v1)."""

    return REGISTER_MAP.get(model, REGISTER_MAP[DEFAULT_MODEL])


def get_registers_for_firmware(firmware_version: str) -> Dict[str, RegisterDefinition]:
    """Return the register map for the requested firmware version."""

    # Determine firmware family (1.x or 2.x) from version string
    if firmware_version:
        try:
            major_version = int(float(firmware_version))
            if major_version >= 2:
                return FIRMWARE_REGISTER_MAP.get(FIRMWARE_V2, V1_REGISTERS)
        except (ValueError, TypeError):
            pass
    
    return FIRMWARE_REGISTER_MAP.get(FIRMWARE_V1, V1_REGISTERS)


def detect_firmware_version(sw_version_value: float) -> str:
    """Detect firmware family from MULTI_SW_VER register value.
    
    Args:
        sw_version_value: Raw value from MULTI_SW_VER register (e.g., 1.87, 2.15)
    
    Returns:
        Firmware version identifier (FIRMWARE_V1 or FIRMWARE_V2)
    """
    if sw_version_value and sw_version_value >= 2.0:
        return FIRMWARE_V2
    return FIRMWARE_V1


def get_register_definition(model: str, key: str, firmware_version: str = None, firmware_version: str = None) -> RegisterDefinition:
    """Return the register definition for a given model/firmware and key.
    
    Args:
        model: Hardware model (MAC80, MAC100, MAC150) - used for legacy support
        key: Register key to look up
        firmware_version: Firmware version string (e.g., FIRMWARE_V1, FIRMWARE_V2)
    
    Returns:
        RegisterDefinition for the requested register
    """
    # Prefer firmware-based lookup if provided
    if firmware_version:
        registers = get_registers_for_firmware(firmware_version)
    else:
        # Fall back to model-based lookup (legacy)
        registers = get_registers_for_model(model)
    
    if key not in registers:
        raise KeyError(f"Register '{key}' not defined for model '{model}' firmware '{firmware_version}'")
    return registers[key]


# Operating modes for IV01_CONTROLSTATE
MODE_STOP = 0
MODE_AWAY = 1
MODE_HOME = 2
MODE_BOOST = 3
MODE_OVERPRESSURE = 4
MODE_AWAY_TIMER = 5
MODE_HOME_TIMER = 6
MODE_BOOST_TIMER = 7
MODE_OVERPRESSURE_TIMER = 8
MODE_MANUAL = 9

# Speed control values for IV01_SPEED
SPEED_AUTO = 0
SPEED_STOP = 1
SPEED_1 = 2
SPEED_2 = 3
SPEED_3 = 4
SPEED_4 = 5
SPEED_5 = 6

# POWER_BTN states
POWER_OFF = 0
POWER_SHUTTING_DOWN = 1
POWER_STARTING = 2
POWER_RUNNING = 3
