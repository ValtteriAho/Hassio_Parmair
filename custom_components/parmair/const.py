"""Constants and register metadata for the Parmair integration."""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "parmair"

# Configuration
CONF_HEATER_TYPE = "heater_type"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SLAVE_ID = "slave_id"
CONF_SOFTWARE_VERSION = "software_version"

DEFAULT_NAME = "Parmair MAC"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 60  # seconds
DEFAULT_SLAVE_ID = 0  # Parmair devices respond with unit ID 0

# Software versions
SOFTWARE_VERSION_1 = "1.x"
SOFTWARE_VERSION_2 = "2.x"
SOFTWARE_VERSION_UNKNOWN = "unknown"

# V2 VENT_MACHINE codes -> display model number (v2 uses different encoding than v1)
HARDWARE_TYPE_MAP_V2: dict[int, int] = {
    112: 120,  # MAC 120
}

# Heater types - NOTE: Values are REVERSED between firmware versions!
# Firmware 1.xx (register 1240): 0=Water, 1=Electric, 2=None
# Firmware 2.xx (register 1127): 0=Electric, 1=Water, 2=None

# v1.xx heater type values
HEATER_TYPE_ELECTRIC_V1 = 1
HEATER_TYPE_NONE_V1 = 2
HEATER_TYPE_WATER_V1 = 0

# v2.xx heater type values
HEATER_TYPE_ELECTRIC_V2 = 0
HEATER_TYPE_NONE_V2 = 2
HEATER_TYPE_WATER_V2 = 1

# Legacy constants (v1.xx mapping for backward compatibility)
HEATER_TYPE_ELECTRIC = 1
HEATER_TYPE_NONE = 2
HEATER_TYPE_UNKNOWN = -1
HEATER_TYPE_WATER = 0


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


# Register keys (alphabetical)
REG_ACKNOWLEDGE_ALARMS = "acknowledge_alarms"
REG_ACTUAL_SPEED = "actual_speed"
REG_ALARM_COUNT = "alarm_count"
REG_ALARMS_STATE = "alarms_state"
REG_AWAY_SPEED = "away_speed"
REG_BOOST_SETTING = "boost_setting"
REG_BOOST_STATE = "boost_state"
REG_BOOST_TIMER = "boost_timer"
REG_BOOST_TIME_SETTING = "boost_time_setting"
REG_CO2_EXHAUST = "co2_exhaust"  # MAC 2 only (v2.xx) - combination sensor in exhaust duct
REG_CONTROL_STATE = "control_state"
REG_DEFROST_STATE = "defrost_state"
REG_EXHAUST_FAN_SPEED = "exhaust_fan_speed"
REG_EXHAUST_TEMP = "exhaust_temp"
REG_EXHAUST_TEMP_SETPOINT = "exhaust_temp_setpoint"
REG_FILTER_DAY = "filter_day"
REG_FILTER_INTERVAL = "filter_interval"
REG_FILTER_MONTH = "filter_month"
REG_FILTER_NEXT_DAY = "filter_next_day"
REG_FILTER_NEXT_MONTH = "filter_next_month"
REG_FILTER_NEXT_YEAR = "filter_next_year"
REG_FILTER_REPLACED = "filter_replaced"
REG_FILTER_STATE = "filter_state"
REG_FILTER_YEAR = "filter_year"
REG_FRESH_AIR_TEMP = "fresh_air_temp"
REG_HARDWARE_TYPE = "hardware_type"
REG_HEAT_RECOVERY_EFFICIENCY = "heat_recovery_efficiency"
REG_HEATER_ENABLE = "heater_enable"
REG_HEATER_TYPE = "heater_type"
REG_HOME_SPEED = "home_speed"
REG_HOME_STATE = "home_state"
REG_HUMIDITY = "humidity"
REG_HUMIDITY_24H_AVG = "humidity_24h_avg"
REG_LTO_HEAT_RECOVERY_CONTROL = "lto_heat_recovery_control"
REG_OVERPRESSURE_STATE = "overpressure_state"
REG_OVERPRESSURE_TIMER = "overpressure_timer"
REG_OVERPRESSURE_TIME_SETTING = "overpressure_time_setting"
REG_POST_HEATER_OUTPUT = "post_heater_output"
REG_POWER = "power"
REG_PRE_HEATER_OUTPUT = "pre_heater_output"
REG_SPEED_CONTROL = "speed_control"
REG_SUM_ALARM = "sum_alarm"
REG_SUMMER_MODE = "summer_mode"
REG_SUMMER_MODE_TEMP_LIMIT = "summer_mode_temp_limit"
REG_SUPPLY_AFTER_RECOVERY_TEMP = "supply_after_recovery_temp"
REG_SUPPLY_FAN_SPEED = "supply_fan_speed"
REG_SUPPLY_TEMP = "supply_temp"
REG_SUPPLY_TEMP_SETPOINT = "supply_temp_setpoint"
REG_SOFTWARE_VERSION = "software_version"
REG_TIME_PROGRAM_ENABLE = "time_program_enable"
REG_WASTE_TEMP = "waste_temp"


def _build_registers_v1() -> dict[str, RegisterDefinition]:
    """Build the complete register map for Parmair MAC devices with software version 1.xx.

    This is the current register map from the CSV documentation.
    """

    return {
        REG_HARDWARE_TYPE: RegisterDefinition(REG_HARDWARE_TYPE, 1244, "VENT_MACHINE"),
        REG_SOFTWARE_VERSION: RegisterDefinition(
            REG_SOFTWARE_VERSION, 1018, "MULTI_SW_VER", scale=0.01
        ),
        REG_POWER: RegisterDefinition(REG_POWER, 1208, "POWER_BTN_FI", writable=True),
        REG_CONTROL_STATE: RegisterDefinition(
            REG_CONTROL_STATE, 1185, "IV01_CONTROLSTATE_FO", writable=True
        ),
        REG_ACTUAL_SPEED: RegisterDefinition(REG_ACTUAL_SPEED, 1186, "IV01_SPEED_FO"),
        REG_SPEED_CONTROL: RegisterDefinition(
            REG_SPEED_CONTROL, 1187, "IV01_SPEED_FOC", writable=True
        ),
        REG_FRESH_AIR_TEMP: RegisterDefinition(REG_FRESH_AIR_TEMP, 1020, "TE01_M", scale=0.1),
        REG_SUPPLY_AFTER_RECOVERY_TEMP: RegisterDefinition(
            REG_SUPPLY_AFTER_RECOVERY_TEMP, 1022, "TE05_M", scale=0.1
        ),
        REG_SUPPLY_TEMP: RegisterDefinition(REG_SUPPLY_TEMP, 1023, "TE10_M", scale=0.1),
        REG_EXHAUST_TEMP: RegisterDefinition(REG_EXHAUST_TEMP, 1024, "TE30_M", scale=0.1),
        REG_WASTE_TEMP: RegisterDefinition(REG_WASTE_TEMP, 1025, "TE31_M", scale=0.1),
        REG_EXHAUST_TEMP_SETPOINT: RegisterDefinition(
            REG_EXHAUST_TEMP_SETPOINT, 1060, "TE30_S", scale=0.1, writable=True
        ),
        REG_SUPPLY_TEMP_SETPOINT: RegisterDefinition(
            REG_SUPPLY_TEMP_SETPOINT, 1065, "TE10_S", scale=0.1, writable=True
        ),
        REG_HOME_SPEED: RegisterDefinition(REG_HOME_SPEED, 1104, "HOME_SPEED_S", writable=True),
        REG_AWAY_SPEED: RegisterDefinition(REG_AWAY_SPEED, 1105, "AWAY_SPEED_S", writable=True),
        REG_BOOST_SETTING: RegisterDefinition(
            REG_BOOST_SETTING, 1117, "BOOST_SETTING_S", writable=True
        ),
        REG_HOME_STATE: RegisterDefinition(REG_HOME_STATE, 1200, "HOME_STATE_FI"),
        REG_BOOST_STATE: RegisterDefinition(REG_BOOST_STATE, 1201, "BOOST_STATE_FI"),
        REG_BOOST_TIMER: RegisterDefinition(REG_BOOST_TIMER, 1202, "BOOST_TIMER_FM", writable=True),
        REG_OVERPRESSURE_STATE: RegisterDefinition(REG_OVERPRESSURE_STATE, 1203, "OVERP_STATE_FI"),
        REG_OVERPRESSURE_TIMER: RegisterDefinition(
            REG_OVERPRESSURE_TIMER, 1204, "OVERP_TIMER_FM", writable=True
        ),
        REG_HUMIDITY: RegisterDefinition(REG_HUMIDITY, 1180, "MEXX_FM", optional=True),
        REG_HUMIDITY_24H_AVG: RegisterDefinition(
            REG_HUMIDITY_24H_AVG, 1192, "ME05_AVG_FM", scale=0.1, optional=True
        ),
        REG_LTO_HEAT_RECOVERY_CONTROL: RegisterDefinition(
            REG_LTO_HEAT_RECOVERY_CONTROL, 1046, "FG50_Y", scale=0.1
        ),
        REG_ALARM_COUNT: RegisterDefinition(REG_ALARM_COUNT, 1004, "ALARM_COUNT"),
        REG_SUM_ALARM: RegisterDefinition(REG_SUM_ALARM, 1005, "SUM_ALARM"),
        REG_ALARMS_STATE: RegisterDefinition(REG_ALARMS_STATE, 1206, "ALARMS_STATE_FI"),
        REG_SUMMER_MODE: RegisterDefinition(REG_SUMMER_MODE, 1079, "SUMMER_MODE_S", writable=True),
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
        REG_DEFROST_STATE: RegisterDefinition(REG_DEFROST_STATE, 1183, "DFRST_FI"),
        REG_SUPPLY_FAN_SPEED: RegisterDefinition(REG_SUPPLY_FAN_SPEED, 1040, "TF10_Y", scale=0.1),
        REG_EXHAUST_FAN_SPEED: RegisterDefinition(REG_EXHAUST_FAN_SPEED, 1042, "PF30_Y", scale=0.1),
        REG_PRE_HEATER_OUTPUT: RegisterDefinition(REG_PRE_HEATER_OUTPUT, 1048, "EC05_Y", scale=0.1),
        REG_POST_HEATER_OUTPUT: RegisterDefinition(
            REG_POST_HEATER_OUTPUT, 1044, "TV45_Y", scale=0.1
        ),
        REG_FILTER_STATE: RegisterDefinition(REG_FILTER_STATE, 1205, "FILTER_STATE_FI"),
        REG_FILTER_DAY: RegisterDefinition(REG_FILTER_DAY, 1086, "FILTER_DAY", writable=True),
        REG_FILTER_MONTH: RegisterDefinition(REG_FILTER_MONTH, 1087, "FILTER_MONTH", writable=True),
        REG_FILTER_YEAR: RegisterDefinition(REG_FILTER_YEAR, 1088, "FILTER_YEAR", writable=True),
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


def _build_registers_v2() -> dict[str, RegisterDefinition]:
    """Build the complete register map for Parmair MAC devices with software version 2.xx.

    Firmware 2.xx uses Register ID + 1000 addressing scheme.
    For example: Register ID 20 (TE01_M) -> Address 1020

    Note: These registers are NOT compatible with 1.xx firmware which uses different
    control registers (POWER_BTN_FI, IV01_CONTROLSTATE_FO, etc.). Firmware 2.xx uses
    UNIT_CONTROL_FO and USERSTATECONTROL_FO instead.
    """
    return {
        # System information - same register IDs as v1 but +1000 offset
        REG_HARDWARE_TYPE: RegisterDefinition(REG_HARDWARE_TYPE, 1125, "VENT_MACHINE"),
        REG_SOFTWARE_VERSION: RegisterDefinition(
            REG_SOFTWARE_VERSION, 1015, "MULTI_SW_VER", scale=0.01
        ),
        # Control registers - v2 uses different control scheme
        REG_POWER: RegisterDefinition(REG_POWER, 1180, "UNIT_CONTROL_FO", writable=True),
        REG_CONTROL_STATE: RegisterDefinition(
            REG_CONTROL_STATE, 1181, "USERSTATECONTROL_FO", writable=True
        ),
        REG_ACTUAL_SPEED: RegisterDefinition(REG_ACTUAL_SPEED, 1187, "IV01_SPEED_FO"),
        REG_SPEED_CONTROL: RegisterDefinition(
            REG_SPEED_CONTROL, 1187, "IV01_SPEED_FO", writable=True
        ),
        # Temperature sensors (×0.1°C scaling)
        REG_FRESH_AIR_TEMP: RegisterDefinition(REG_FRESH_AIR_TEMP, 1020, "TE01_M", scale=0.1),
        REG_SUPPLY_AFTER_RECOVERY_TEMP: RegisterDefinition(
            REG_SUPPLY_AFTER_RECOVERY_TEMP, 1021, "TE05_M", scale=0.1
        ),
        REG_SUPPLY_TEMP: RegisterDefinition(REG_SUPPLY_TEMP, 1022, "TE10_M", scale=0.1),
        REG_EXHAUST_TEMP: RegisterDefinition(REG_EXHAUST_TEMP, 1024, "TE30_M", scale=0.1),
        REG_WASTE_TEMP: RegisterDefinition(REG_WASTE_TEMP, 1023, "TE31_M", scale=0.1),
        # Temperature setpoints (×0.1°C scaling)
        # TE30_S: shared with REG_SUMMER_MODE_TEMP_LIMIT (target room temp / summer mode limit)
        REG_EXHAUST_TEMP_SETPOINT: RegisterDefinition(
            REG_EXHAUST_TEMP_SETPOINT, 1073, "TE30_S", scale=0.1, writable=True
        ),
        REG_SUPPLY_TEMP_SETPOINT: RegisterDefinition(
            REG_SUPPLY_TEMP_SETPOINT, 1061, "TE10_MIN_HOME_S", scale=0.1, writable=True
        ),
        # Speed presets
        REG_HOME_SPEED: RegisterDefinition(REG_HOME_SPEED, 1060, "HOME_SPEED_S", writable=True),
        REG_AWAY_SPEED: RegisterDefinition(REG_AWAY_SPEED, 1063, "AWAY_SPEED_S", writable=True),
        REG_BOOST_SETTING: RegisterDefinition(
            REG_BOOST_SETTING, 1065, "BOOST_SETTING_S", writable=True
        ),
        # State indicators - using soft measurements for v2
        REG_HOME_STATE: RegisterDefinition(REG_HOME_STATE, 1181, "USERSTATECONTROL_FO"),
        REG_BOOST_STATE: RegisterDefinition(REG_BOOST_STATE, 1181, "USERSTATECONTROL_FO"),
        REG_BOOST_TIMER: RegisterDefinition(REG_BOOST_TIMER, 1200, "BOOST_TIMER_FM", writable=True),
        REG_OVERPRESSURE_STATE: RegisterDefinition(
            REG_OVERPRESSURE_STATE, 1181, "USERSTATECONTROL_FO"
        ),
        REG_OVERPRESSURE_TIMER: RegisterDefinition(
            REG_OVERPRESSURE_TIMER, 1201, "OVERP_TIMER_FM", writable=True
        ),
        # Standard sensors (v2.xx)
        REG_HUMIDITY: RegisterDefinition(REG_HUMIDITY, 1025, "ME05_M"),
        REG_HUMIDITY_24H_AVG: RegisterDefinition(
            REG_HUMIDITY_24H_AVG, 1192, "ME05_AVG_FM", scale=0.1
        ),
        REG_CO2_EXHAUST: RegisterDefinition(
            REG_CO2_EXHAUST, 1026, "QE05_M"
        ),  # MAC 2 standard sensor (v2.xx)
        REG_LTO_HEAT_RECOVERY_CONTROL: RegisterDefinition(
            REG_LTO_HEAT_RECOVERY_CONTROL, 1046, "FG50_Y", scale=0.1
        ),
        # Alarm registers
        REG_ALARM_COUNT: RegisterDefinition(REG_ALARM_COUNT, 1004, "ALARM_COUNT"),
        REG_SUM_ALARM: RegisterDefinition(REG_SUM_ALARM, 1005, "SUM_ALARM"),
        REG_ALARMS_STATE: RegisterDefinition(REG_ALARMS_STATE, 1204, "ALARMS_STATE_FI"),
        # Switch registers
        REG_SUMMER_MODE: RegisterDefinition(
            REG_SUMMER_MODE, 1071, "AUTO_SUMMER_COOL_S", writable=True
        ),
        REG_TIME_PROGRAM_ENABLE: RegisterDefinition(
            REG_TIME_PROGRAM_ENABLE, 1070, "TP_ENABLE_S", writable=True
        ),
        REG_HEATER_ENABLE: RegisterDefinition(
            REG_HEATER_ENABLE, 1074, "AUTO_HEATER_ENABLE_S", writable=True
        ),
        # Button registers
        REG_ACKNOWLEDGE_ALARMS: RegisterDefinition(
            REG_ACKNOWLEDGE_ALARMS, 1003, "ACK_ALARMS", writable=True
        ),
        REG_FILTER_REPLACED: RegisterDefinition(
            REG_FILTER_REPLACED, 1184, "FILTER_STATE_FI", writable=True
        ),
        # Select registers
        REG_HEATER_TYPE: RegisterDefinition(
            REG_HEATER_TYPE, 1127, "HEAT_RADIATOR_TYPE", writable=True
        ),
        # Predefined settings registers
        REG_BOOST_TIME_SETTING: RegisterDefinition(
            REG_BOOST_TIME_SETTING, 1066, "BOOST_TIME_S", writable=True
        ),
        REG_OVERPRESSURE_TIME_SETTING: RegisterDefinition(
            REG_OVERPRESSURE_TIME_SETTING, 1069, "OVERP_TIME_S", writable=True
        ),
        # TE30_S: same physical register as REG_EXHAUST_TEMP_SETPOINT (target room temp in summer)
        REG_SUMMER_MODE_TEMP_LIMIT: RegisterDefinition(
            REG_SUMMER_MODE_TEMP_LIMIT, 1073, "TE30_S", scale=0.1, writable=True
        ),
        # Additional number registers
        REG_FILTER_INTERVAL: RegisterDefinition(
            REG_FILTER_INTERVAL, 1090, "FILTER_INTERVAL_S", writable=True
        ),
        # Additional sensor registers
        REG_HEAT_RECOVERY_EFFICIENCY: RegisterDefinition(
            REG_HEAT_RECOVERY_EFFICIENCY, 1183, "FG50_EA_M", scale=0.1
        ),
        REG_DEFROST_STATE: RegisterDefinition(REG_DEFROST_STATE, 1182, "DFRST_FI"),
        REG_SUPPLY_FAN_SPEED: RegisterDefinition(REG_SUPPLY_FAN_SPEED, 1040, "TF10_Y", scale=0.1),
        REG_EXHAUST_FAN_SPEED: RegisterDefinition(REG_EXHAUST_FAN_SPEED, 1042, "PF30_Y", scale=0.1),
        REG_PRE_HEATER_OUTPUT: RegisterDefinition(REG_PRE_HEATER_OUTPUT, 1048, "EC05_Y", scale=0.1),
        REG_POST_HEATER_OUTPUT: RegisterDefinition(
            REG_POST_HEATER_OUTPUT, 1044, "TV45_Y", scale=0.1
        ),
        REG_FILTER_STATE: RegisterDefinition(REG_FILTER_STATE, 1184, "FILTER_STATE_FI"),
        REG_FILTER_DAY: RegisterDefinition(REG_FILTER_DAY, 1193, "FILTER_DAY", writable=True),
        REG_FILTER_MONTH: RegisterDefinition(REG_FILTER_MONTH, 1194, "FILTER_MONTH", writable=True),
        REG_FILTER_YEAR: RegisterDefinition(REG_FILTER_YEAR, 1195, "FILTER_YEAR", writable=True),
        REG_FILTER_NEXT_DAY: RegisterDefinition(
            REG_FILTER_NEXT_DAY, 1196, "FILTERNEXT_DAY", writable=True
        ),
        REG_FILTER_NEXT_MONTH: RegisterDefinition(
            REG_FILTER_NEXT_MONTH, 1197, "FILTERNEXT_MONTH", writable=True
        ),
        REG_FILTER_NEXT_YEAR: RegisterDefinition(
            REG_FILTER_NEXT_YEAR, 1198, "FILTERNEXT_YEAR", writable=True
        ),
    }


def get_registers_for_version(software_version: str) -> dict[str, RegisterDefinition]:
    """Get the appropriate register map based on software version.

    Args:
        software_version: Software version string (e.g., "1.x", "2.x", "1.83", "2.28")

    Returns:
        Dictionary mapping register keys to RegisterDefinition objects
    """
    # Check for firmware 2.00-2.99 range (handles both "2.x" constant and "2.28" actual versions)
    if software_version == SOFTWARE_VERSION_2 or software_version.startswith("2."):
        return _build_registers_v2()
    else:
        # Default to v1 for firmware 1.00-1.99 or unknown versions
        return _build_registers_v1()


# Build the default register map (v1)
REGISTERS = _build_registers_v1()

# Static registers (read once at startup - values don't change during operation)
STATIC_REGISTER_KEYS = (
    REG_SOFTWARE_VERSION,  # Software version never changes
    REG_HARDWARE_TYPE,  # Hardware model (80/100/150) never changes
    REG_HEATER_TYPE,  # Heater type (water/electric) rarely changes
)

# Dynamic registers (polled regularly - values change during operation)
POLLING_REGISTER_KEYS = (
    REG_POWER,
    REG_CONTROL_STATE,
    REG_ACTUAL_SPEED,
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
    REG_CO2_EXHAUST,  # MAC 2 only (will be unavailable in older devices)
    REG_LTO_HEAT_RECOVERY_CONTROL,
    REG_ALARM_COUNT,
    REG_SUM_ALARM,
    REG_ALARMS_STATE,
    REG_HEAT_RECOVERY_EFFICIENCY,
    REG_OVERPRESSURE_TIMER,
    REG_DEFROST_STATE,
    REG_SUPPLY_FAN_SPEED,
    REG_EXHAUST_FAN_SPEED,
    REG_PRE_HEATER_OUTPUT,
    REG_POST_HEATER_OUTPUT,
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


def get_register_definition(
    key: str, registers: dict[str, RegisterDefinition] | None = None
) -> RegisterDefinition:
    """Return the register definition for a given key.

    Args:
        key: Register key to look up
        registers: Optional register map to use. If None, uses default REGISTERS.

    Returns:
        RegisterDefinition for the requested register
    """
    reg_map = registers if registers is not None else REGISTERS
    if key not in reg_map:
        raise KeyError(f"Register '{key}' not defined")
    return reg_map[key]


# Operating modes for IV01_CONTROLSTATE (V1) / USERSTATECONTROL_FO (V2)
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

# Control state display mapping (differs by firmware version)
# V1.x IV01_CONTROLSTATE_FO: Stop, Away, Home, Boost, Overpressure, timers, Manual
# V2.x USERSTATECONTROL_FO: 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace
CONTROL_STATE_MAP_V1: dict[int, str] = {
    MODE_STOP: "Stop",
    MODE_AWAY: "Away",
    MODE_HOME: "Home",
    MODE_BOOST: "Boost",
    MODE_OVERPRESSURE: "Overpressure",
    5: "Away Timer",
    6: "Home Timer",
    7: "Boost Timer",
    8: "Overpressure Timer",
    MODE_MANUAL: "Manual",
}
CONTROL_STATE_MAP_V2: dict[int, str] = {
    0: "Off",
    1: "Away",
    2: "Home",
    3: "Boost",
    4: "Sauna",
    5: "Fireplace",
}

# Speed control values for IV01_SPEED
SPEED_AUTO = 0
SPEED_STOP = 1
SPEED_1 = 2
SPEED_2 = 3
SPEED_3 = 4
SPEED_4 = 5
SPEED_5 = 6

# POWER_BTN states (V1: POWER_BTN_FI = Off/Shutting Down/Starting/Running)
POWER_OFF = 0
POWER_SHUTTING_DOWN = 1
POWER_STARTING = 2
POWER_RUNNING = 3

# Power state display mapping (differs by firmware version)
# V1.x POWER_BTN_FI: 0=Off, 1=Shutting Down, 2=Starting, 3=Running
# V2.x UNIT_CONTROL_FO: 0=Off, 1=On
POWER_STATE_MAP_V1: dict[int, str] = {
    POWER_OFF: "Off",
    POWER_SHUTTING_DOWN: "Shutting Down",
    POWER_STARTING: "Starting",
    POWER_RUNNING: "Running",
}
POWER_STATE_MAP_V2: dict[int, str] = {0: "Off", 1: "On"}

# Filter state display mapping (differs by firmware version)
# V1.x FILTER_STATE_FI: 0=Replace, 1=OK
FILTER_STATE_MAP_V1: dict[int, str] = {0: "Replace", 1: "OK"}
# V2.x FILTER_STATE_FI: 0=Idle/OK, 1=Acknowledge Change, 2=Replace Reminder
FILTER_STATE_MAP_V2: dict[int, str] = {
    0: "OK",
    1: "Acknowledge Change",
    2: "Replace Reminder",
}
