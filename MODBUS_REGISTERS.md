# Parmair Ventilation Modbus Register Map

This document catalogs the Modbus holding registers used by the Parmair Ventilation Home Assistant integration. The addresses below use the zero-based offset expected by most Modbus client libraries (including `pymodbus`). If your tooling expects one-based register numbers, add 1 to the address shown in the table.

## Register Overview

| Register ID (1-based) | Address (0-based) | Symbol | Access | Scaling | Notes |
|----------------------:|------------------:|--------|--------|---------|-------|
| 208 | 207 | POWER_BTN | R/W | 1 | Power state command and feedback (0=Off, 3=Running). |
| 185 | 184 | CONTROL_STATE | R | 1 | Current operating mode (STOP/AWAY/HOME/BOOST/etc.). |
| 187 | 186 | SPEED_CONTROL | R/W | 1 | Requested fan speed (AUTO/STOP/1-5). |
| 20 | 19 | FRESH_AIR_TEMP | R | 0.1°C | Outdoor air temperature. |
| 23 | 22 | SUPPLY_TEMP | R | 0.1°C | Air supplied indoors. |
| 24 | 23 | EXHAUST_TEMP | R | 0.1°C | Air extracted from rooms. |
| 25 | 24 | WASTE_TEMP | R | 0.1°C | Exhausted air after heat exchange. |
| 60 | 59 | EXHAUST_TEMP_SETPOINT | R/W | 0.1°C | Target exhaust temperature. |
| 65 | 64 | SUPPLY_TEMP_SETPOINT | R/W | 0.1°C | Target supply temperature. |
| 104 | 103 | HOME_SPEED | R/W | % | Fan percentage for Home mode (0-100). |
| 105 | 104 | AWAY_SPEED | R/W | % | Fan percentage for Away mode (0-100). |
| 117 | 116 | BOOST_SETTING | R/W | % | Fan percentage for Boost mode (0-100). |
| 200 | 199 | HOME_STATE | R | 1 | Indicates if unit is currently in Home mode. |
| 201 | 200 | BOOST_STATE | R | 1 | Indicates if Boost mode is active. |
| 202 | 201 | BOOST_TIMER | R | minutes | Remaining Boost time. |
| 180 | 179 | HUMIDITY | R | % | Indoor humidity (available when hardware fitted). |
| 31 | 30 | CO2 | R | ppm | Indoor CO₂ (available when hardware fitted). |
| 4 | 3 | ALARM_COUNT | R | 1 | Active alarm count. |
| 5 | 4 | SUM_ALARM | R | 1 | Summary alarm flag. |
| 206 | 205 | ALARMS_STATE | R | 1 | Bitmask of alarm states. |

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
