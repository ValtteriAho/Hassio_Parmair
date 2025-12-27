# Parmair Ventilation Modbus Register Map

This document catalogs the Modbus holding registers used by the Parmair Ventilation Home Assistant integration. The addresses below use the zero-based offset expected by most Modbus client libraries (including `pymodbus`). Register IDs match the official Parmair documentation.

**Important**: Modbus addresses are offset by +1000 from the register ID (e.g., Register ID 20 → Address 1019).

## Register Overview

| Register ID | Address (0-based) | Official ID | Symbol | Access | Scaling | Notes |
|------------:|------------------:|-------------|--------|--------|---------|-------|
| 208 | 1207 | POWER_BTN_FI | POWER_BTN | R/W | 1 | Power state (0=Off, 1=Stopping, 2=Starting, 3=Running). |
| 185 | 1184 | IV01_CONTROLSTATE_FO | CONTROL_STATE | R | 1 | Operating mode (STOP/AWAY/HOME/BOOST/etc.). |
| 187 | 1186 | IV01_SPEED_FOC | SPEED_CONTROL | R/W | 1 | Fan speed control (AUTO/STOP/1-5). |
| 20 | 1019 | TE01_M | FRESH_AIR_TEMP | R | 0.1°C | Outdoor/fresh air temperature. |
| 23 | 1022 | TE10_M | SUPPLY_TEMP | R | 0.1°C | Supply air temperature (indoors). |
| 24 | 1023 | TE30_M | EXHAUST_TEMP | R | 0.1°C | Exhaust air temperature (from rooms). |
| 25 | 1024 | TE31_M | WASTE_TEMP | R | 0.1°C | Waste air temperature (after heat exchange). |
| 60 | 1059 | TE30_S | EXHAUST_TEMP_SETPOINT | R/W | 0.1°C | Target exhaust temperature. |
| 65 | 1064 | TE10_S | SUPPLY_TEMP_SETPOINT | R/W | 0.1°C | Target supply temperature. |
| 104 | 1103 | HOME_SPEED_S | HOME_SPEED | R/W | 1 | Fan speed preset for Home mode (0-4). |
| 105 | 1104 | AWAY_SPEED_S | AWAY_SPEED | R/W | 1 | Fan speed preset for Away mode (0-4). |
| 117 | 1116 | BOOST_SETTING_S | BOOST_SETTING | R/W | 1 | Fan speed preset for Boost mode (2-4). |
| 200 | 1199 | HOME_STATE_FI | HOME_STATE | R | 1 | Home mode active (0=Away, 1=Home). |
| 201 | 1200 | BOOST_STATE_FI | BOOST_STATE | R | 1 | Boost mode active (0=Inactive, 1=Active). |
| 202 | 1201 | BOOST_TIMER_FM | BOOST_TIMER | R/W | minutes | Boost timer remaining time. |
| 180 | 1179 | MEXX_FM | HUMIDITY | R | % | Indoor humidity (65535=not installed). |
| 31 | 1030 | QE20_M | CO2 | R | ppm | Indoor CO₂ (65535=not installed). |
| 4 | 1003 | ALARM_COUNT | ALARM_COUNT | R | 1 | Number of active alarms. |
| 5 | 1004 | SUM_ALARM | SUM_ALARM | R | 1 | Summary alarm flag. |
| 244 | 1243 | VENT_MACHINE | VENT_MACHINE | R/W | 1 | Machine type code (for auto-detection). |
| 206 | 1205 | ALARMS_STATE_FI | ALARMS_STATE | R | 1 | Alarm state bitmask (0=OK, 1=Alarms, 2=Filter). |

## Operating Modes

`CONTROL_STATE` (register 185 / address 184) reports the current operating mode:

| Value | Mode |
|------:|------|
| 0 | Stop |
| 1 | Away |
| 2 | Home |
| 3 | Boost |
| 4 | Overpressure |
| 5 | Away (timer) |
| 6 | Home (timer) |
| 7 | Boost (timer) |
| 8 | Overpressure (timer) |
| 9 | Manual |

## Fan Speed Control

`SPEED_CONTROL` (register 187 / address 186) accepts the following values:

| Value | Description |
|------:|-------------|
| 0 | Auto |
| 1 | Stop |
| 2 | Speed 1 |
| 3 | Speed 2 |
| 4 | Speed 3 |
| 5 | Speed 4 |
| 6 | Speed 5 |

## Scaling and Units

- Temperatures use a scale factor of 10 (e.g., raw value 210 equals 21.0 °C).
- Fan speed presets (`HOME_SPEED`, `AWAY_SPEED`, `BOOST_SETTING`) are stored as 0-100 percentages.
- Humidity is expressed directly in percent, CO₂ in parts per million, timers in minutes.

## Access Notes

- All registers listed here are holding registers. Read operations use Modbus function code 03; writes use function codes 06 (single register) or 16 (multiple registers).
- Values marked **R/W** can be safely written when the device is reachable; **R** entries should be treated as read-only status information.
- Optional sensors (humidity, CO₂) may return negative values if the hardware module is not installed.

Use this register map as the authoritative reference when extending or troubleshooting the integration.
