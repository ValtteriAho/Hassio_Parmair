"""Constants and register metadata for the Parmair integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

DOMAIN = "parmair"

# Configuration
CONF_SLAVE_ID = "slave_id"
CONF_MODEL = "model"

DEFAULT_NAME = "Parmair MAC"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# Supported hardware profiles
MODEL_MAC80 = "MAC80"
MODEL_MAC150 = "MAC150"
MODEL_UNKNOWN = "Unknown"
DEFAULT_MODEL = MODEL_MAC80

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
REG_POWER = "power"
REG_CONTROL_STATE = "control_state"
REG_SPEED_CONTROL = "speed_control"
REG_FRESH_AIR_TEMP = "fresh_air_temp"
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
REG_CO2 = "co2"
REG_ALARM_COUNT = "alarm_count"
REG_SUM_ALARM = "sum_alarm"
REG_ALARMS_STATE = "alarms_state"

# Switch register keys
REG_SUMMER_MODE = "summer_mode"
REG_TIME_PROGRAM_ENABLE = "time_program_enable"
REG_HEATER_ENABLE = "heater_enable"


def _build_mac80_registers() -> Dict[str, RegisterDefinition]:
    """Return register map for the MAC80 firmware."""

    return {
        REG_HARDWARE_TYPE: RegisterDefinition(REG_HARDWARE_TYPE, 1244, "VENT_MACHINE"),
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
    }


MAC80_REGISTERS = _build_mac80_registers()
# Placeholder: MAC150 currently mirrors MAC80 until official register sheet is available.
MAC150_REGISTERS = dict(MAC80_REGISTERS)

REGISTER_MAP: Dict[str, Dict[str, RegisterDefinition]] = {
    MODEL_MAC80: MAC80_REGISTERS,
    MODEL_MAC150: MAC150_REGISTERS,
}

SUPPORTED_MODELS = tuple(REGISTER_MAP.keys())

# Ordered list of registers to poll on each update.
POLLING_REGISTER_KEYS = (
    REG_POWER,
    REG_CONTROL_STATE,
    REG_SPEED_CONTROL,
    REG_FRESH_AIR_TEMP,
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
    REG_CO2,
    REG_ALARM_COUNT,
    REG_SUM_ALARM,
    REG_ALARMS_STATE,
)


def get_registers_for_model(model: str) -> Dict[str, RegisterDefinition]:
    """Return the register map for the requested model."""

    return REGISTER_MAP.get(model, REGISTER_MAP[DEFAULT_MODEL])


def get_register_definition(model: str, key: str) -> RegisterDefinition:
    """Return the register definition for a given model and key."""

    registers = get_registers_for_model(model)
    if key not in registers:
        raise KeyError(f"Register '{key}' not defined for model '{model}'")
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
