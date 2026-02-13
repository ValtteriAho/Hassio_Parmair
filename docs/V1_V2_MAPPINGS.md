# Parmair firmware V1 vs V2 – register and mapping differences

This document lists mapping and behavioural differences between **firmware 1.x** (e.g. MAC 80/100/150) and **firmware 2.x** (e.g. MAC 120 v2, MAC 2). The integration uses these to show correct labels and options in Home Assistant.

## Power state

| Version | Register        | Values |
|--------|-----------------|--------|
| **V1** | POWER_BTN_FI    | 0=Off, 1=Shutting Down, 2=Starting, 3=Running |
| **V2** | UNIT_CONTROL_FO | 0=Off, 1=On |

**Integration:** `ParmairPowerStateSensor` uses `POWER_STATE_MAP_V1` / `POWER_STATE_MAP_V2`. Fan `is_on` treats V2 value 1 as “on” and V1 value 3 as “running”.

---

## Control state (user mode)

| Version | Register            | Values |
|--------|---------------------|--------|
| **V1** | IV01_CONTROLSTATE_FO | 0=Stop, 1=Away, 2=Home, 3=Boost, 4=Overpressure, 5=Away Timer, 6=Home Timer, 7=Boost Timer, 8=Overpressure Timer, 9=Manual |
| **V2** | USERSTATECONTROL_FO | 0=Off, 1=Away, 2=Home, 3=Boost, 4=Sauna, 5=Fireplace |

**Integration:** `ParmairControlStateSensor` uses `CONTROL_STATE_MAP_V1` / `CONTROL_STATE_MAP_V2`. Fan presets (away/home/boost) use the same numeric values 1/2/3 on both. On V2, “Overpressure” switch reflects Sauna (4) or Fireplace (5).

---

## Home / Boost / Overpressure state (V2)

On **V2**, `home_state`, `boost_state` and `overpressure_state` are not separate registers; they are derived in the coordinator from `USERSTATECONTROL_FO` (register 1181):

- **home_state:** 1 when control_state == 2 (Home), else 0  
- **boost_state:** 1 when control_state == 3 (Boost), else 0  
- **overpressure_state:** 1 when control_state in (4, 5) (Sauna, Fireplace), else 0  

So the same binary sensors and maps {0: "Away", 1: "Home"} and {0: "Off", 1: "On"} work for both versions.

---

## Heater type

| Version | Register (concept) | Values |
|--------|---------------------|--------|
| **V1** | HEAT_RADIATOR_TYPE  | 0=Water, 1=Electric, 2=None |
| **V2** | HEATPUMP_RADIATOR_ENABLE / HEAT_RADIATOR_TYPE | 0=Electric, 1=Water, 2=None |

**Integration:** `ParmairHeaterTypeSensor` uses `STATE_MAP_V1` / `STATE_MAP_V2` in `const.py` (reversed 0/1 for Water vs Electric).

---

## Filter state

| Version | Register       | Values |
|--------|----------------|--------|
| **V1** | FILTER_STATE_FI | 0=Replace, 1=OK |
| **V2** | FILTER_STATE_FI | 0=OK (Idle), 1=Acknowledge Change, 2=Replace Reminder |

**Integration:** `_filter_state_map(coordinator)` and `ParmairBinarySensor` for “Filter Status” use `FILTER_STATE_MAP_V1` / `FILTER_STATE_MAP_V2`.

---

## Summer mode (switch)

| Version | Register           | Values |
|--------|--------------------|--------|
| **V1** | SUMMER_MODE_S       | 0=Off, 1=On (typical) |
| **V2** | AUTO_SUMMER_COOL_S  | 0=Off, 1=On, 2=Auto |

**Integration:** `ParmairSwitch` for Summer Mode: on V2, `is_on` is true when value is 1 or 2. Turn on writes 1, turn off writes 0.

---

## Other mappings (same or assumed same)

- **Speed (actual_speed / speed_control):** Same 0–6 semantics (Auto, Stop, 1–5) on both; register addresses differ.
- **Defrost state:** Binary 0/1; same meaning.
- **Boost time setting:** 0=30 min … 4=180 min; same mapping used for both (no V2-specific doc).
- **Overpressure time setting:** 0=15 min … 4=120 min; same mapping used for both.
- **Filter interval:** 0=3 months, 1=4 months, 2=6 months (v2_register); same as integration.

---

## Constants and helpers in code

- **const.py:** `POWER_STATE_MAP_V1/V2`, `CONTROL_STATE_MAP_V1/V2`, `FILTER_STATE_MAP_V1/V2`, heater type constants and register definitions per version.
- **sensor.py:** `_power_state_map()`, `_control_state_map()`, `_filter_state_map()`; Power State, Control State, Heater Type and Filter Status sensors choose map from coordinator firmware version.
- **fan.py:** `is_on` uses V2 power 1 = on, V1 power 3 = running.
- **switch.py:** Summer mode `is_on` for V2 uses value in (1, 2).
- **coordinator.py:** For V2, derives `home_state`, `boost_state`, `overpressure_state` from `control_state` (USERSTATECONTROL_FO).
