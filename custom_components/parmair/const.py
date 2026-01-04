"""Constants and register metadata for the Parmair integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

DOMAIN = "parmair"

# Configuration
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "Parmair MAC"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1


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
REG_OVERPRESSURE_STATE = "overpressure_state"
REG_OVERPRESSURE_TIMER = "overpressure_timer"
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

# Predefined settings register keys
REG_BOOST_TIME_SETTING = "boost_time_setting"
REG_OVERPRESSURE_TIME_SETTING = "overpressure_time_setting"
REG_SUMMER_MODE_TEMP_LIMIT = "summer_mode_temp_limit"

# Button register keys
REG_ACKNOWLEDGE_ALARMS = "acknowledge_alarms"
REG_FILTER_REPLACED = "filter_replaced"

# Select register keys
REG_HEATER_TYPE = "heater_type"

# Additional number register keys
REG_FILTER_INTERVAL = "filter_interval"

# Additional sensor register keys
REG_HEAT_RECOVERY_EFFICIENCY = "heat_recovery_efficiency"
REG_OVERPRESSURE_TIMER = "overpressure_timer"
REG_DEFROST_STATE = "defrost_state"
REG_SUPPLY_FAN_SPEED = "supply_fan_speed"
REG_EXHAUST_FAN_SPEED = "exhaust_fan_speed"
REG_FILTER_STATE = "filter_state"
REG_FILTER_DAY = "filter_day"
REG_FILTER_MONTH = "filter_month"
REG_FILTER_YEAR = "filter_year"
REG_FILTER_NEXT_DAY = "filter_next_day"
REG_FILTER_NEXT_MONTH = "filter_next_month"
REG_FILTER_NEXT_YEAR = "filter_next_year"


def _build_registers() -> Dict[str, RegisterDefinition]:
    """Build the complete register map for Parmair MAC devices."""

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
            REG_BOOST_TIMER, 1202, "BOOST_TIMER_FM", writable=True
        ),
        REG_OVERPRESSURE_STATE: RegisterDefinition(
            REG_OVERPRESSURE_STATE, 1203, "OVERP_STATE_FI"
        ),
        REG_OVERPRESSURE_TIMER: RegisterDefinition(
            REG_OVERPRESSURE_TIMER, 1204, "OVERP_TIMER_FM", writable=True
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
        # Predefined settings registers
        REG_BOOST_TIME_SETTING: RegisterDefinition(
            REG_BOOST_TIME_SETTING, 1106, "BOOST_TIME_S", writable=True
        ),
        REG_OVERPRESSURE_TIME_SETTING: RegisterDefinition(
            REG_OVERPRESSURE_TIME_SETTING, 1107, "OVERP_TIME_S", writable=True
        ),
        REG_SUMMER_MODE_TEMP_LIMIT: RegisterDefinition(
            REG_SUMMER_MODE_TEMP_LIMIT, 1078, "SUMMER_MODE_TE01_LIMIT", scale=0.1, writable=True
        ),
        # Additional number registers
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
        REG_FILTER_DAY: RegisterDefinition(
            REG_FILTER_DAY, 1086, "FILTER_DAY", writable=True
        ),
        REG_FILTER_MONTH: RegisterDefinition(
            REG_FILTER_MONTH, 1087, "FILTER_MONTH", writable=True
        ),
        REG_FILTER_YEAR: RegisterDefinition(
            REG_FILTER_YEAR, 1088, "FILTER_YEAR", writable=True
        ),
        REG_FILTER_NEXT_DAY: RegisterDefinition(
            REG_FILTER_NEXT_DAY, 1089, "FILTERNEXT_DAY", writable=True
        ),
        REG_FILTER_NEXT_MONTH: RegisterDefinition(
            REG_FILTER_NEXT_MONTH, 1090, "FILTERNEXT_MONTH", writable=True
        ),
        REG_FILTER_NEXT_YEAR: RegisterDefinition(
            REG_FILTER_NEXT_YEAR, 1091, "FILTERNEXT_YEAR", writable=True
        ),
    }


# Build the complete register map
REGISTERS = _build_registers()

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
    REG_OVERPRESSURE_STATE,
    REG_OVERPRESSURE_TIMER,
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
    REG_FILTER_DAY,
    REG_FILTER_MONTH,
    REG_FILTER_YEAR,
    REG_FILTER_NEXT_DAY,
    REG_FILTER_NEXT_MONTH,
    REG_FILTER_NEXT_YEAR,
    REG_SUMMER_MODE,
    REG_TIME_PROGRAM_ENABLE,
    REG_HEATER_ENABLE,
    REG_BOOST_TIME_SETTING,
    REG_OVERPRESSURE_TIME_SETTING,
    REG_SUMMER_MODE_TEMP_LIMIT,
    REG_BOOST_SETTING,
    REG_FILTER_INTERVAL,
)


def get_register_definition(key: str) -> RegisterDefinition:
    """Return the register definition for a given key.
    
    Args:
        key: Register key to look up
    
    Returns:
        RegisterDefinition for the requested register
    """
    if key not in REGISTERS:
        raise KeyError(f"Register '{key}' not defined")
    return REGISTERS[key]


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
