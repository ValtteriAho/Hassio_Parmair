# Parmair MAC - Home Assistant Integration v0.11.2

![Parmair MAC Logo](parmair_logo.jpg)

A custom Home Assistant integration for Parmair MAC ventilation systems via Modbus TCP communication.

## Latest Updates (v0.11.2)

**CRITICAL FIX**: Humidity and CO2 sensors now update continuously! This release removes all value filtering that was causing sensors to stop updating after ~30 minutes. Sensors now behave identically to temperature sensors - displaying all values including 0 and -1, with continuous updates every 30 seconds.

## Features

- **Fan Control**: Control your Parmair ventilation unit including:
  - Power on/off
  - Mode selection (Away, Home, Boost)
  - Speed control via presets

- **Number Controls**: Adjust ventilation settings:
  - Home Speed Preset (0-4)
  - Away Speed Preset (0-4)
  - Boost Setting (2-4)
  - Exhaust Temperature Setpoint (18-26°C)
  - Supply Temperature Setpoint (15-25°C)

- **Switch Controls**: Toggle system features:
  - Summer Mode Enable/Disable
  - Time Program Enable/Disable
  - Heater Enable/Disable
  - Boost Mode (high-speed ventilation)
  - Overpressure Mode (supply-only ventilation)

- **Action Buttons**: One-click actions:
  - Acknowledge Alarms
  - Mark Filter as Replaced
  
- **Temperature Monitoring**: Real-time monitoring of:
  - Fresh air temperature
  - Supply air temperature  
  - Exhaust air temperature
  - Waste air temperature
  - Temperature setpoints
  
- **Additional Sensors** (if available):
  - Humidity
  - CO2 levels
  - Alarm status
  - Boost timer
  - Software version (Multi24 controller)
  - Diagnostic information in entity attributes
  
- **Local Polling**: Direct communication with your device via Modbus TCP
- **Automatic Model Detection**: Reads hardware type to identify MAC80/MAC100/MAC150 automatically
- **Software Version Detection**: Automatically detects software version (1.x or 2.x) for optimal register mapping

## System Information

This integration supports Parmair "My Air Control" (MAC) ventilation systems:
- **Software 1.x**: Older MAC models (pre-2023) - Modbus spec 1.87
- **Software 2.x**: Newer MAC 2 and updated controllers (2023+) - Modbus spec 2.28

### Requirements
- Home Assistant 2023.1 or newer
- Parmair MAC device with Modbus TCP enabled
- Network connectivity between Home Assistant and the device
- Device IP address and Modbus slave ID (typically 0)

## Installation

### HACS Installation (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/ValtteriAho/Hassio_Parmair`
5. Select category: "Integration"
6. Click "Add"
7. Find "Parmair MAC" in HACS and click "Download"
8. Restart Home Assistant
9. Go to Settings → Devices & Services → Add Integration
10. Search for "Parmair MAC"
11. Enter your device's connection details:
    - IP Address
    - Port (default: 502)
    - Modbus Slave ID (default: 0)
    - Polling Interval (default: 30 seconds)
    - Name (optional)

Hardware model and software version will be auto-detected from the device. If auto-detection fails, you can manually select software version and heater type.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 0)

The hardware model (MAC80/MAC100/MAC150) and software version (1.x/2.x) are automatically detected. If detection fails during setup, you can manually select your software version and heater type.

## Entities Created

### Fan Entity
- **Parmair MAC** (`fan.parmair_mac`): Main control for the ventilation system
  - Presets: Away, Home, Boost
  - Speed control (percentage based on preset)
  - Current speed displayed

### Number Entities
- **Home Speed Preset** (`number.parmair_mac_home_speed_preset`): Fan speed for Home mode (0-4)
- **Away Speed Preset** (`number.parmair_mac_away_speed_preset`): Fan speed for Away mode (0-4)
- **Boost Setting** (`number.parmair_mac_boost_setting`): Boost fan speed level (2-4)
- **Boost Time Setting** (`number.parmair_mac_boost_time_setting`): Boost duration preset (30-180 min)
- **Overpressure Time Setting** (`number.parmair_mac_overpressure_time_setting`): Overpressure duration preset (15-120 min)
- **Exhaust Temperature Setpoint** (`number.parmair_mac_exhaust_temperature_setpoint`): Target exhaust air temperature (18-26°C)
- **Supply Temperature Setpoint** (`number.parmair_mac_supply_temperature_setpoint`): Target supply air temperature (15-25°C)
- **Summer Mode Temperature Limit** (`number.parmair_mac_summer_mode_temp_limit`): Temperature threshold for summer mode activation
- **Filter Replacement Interval** (`number.parmair_mac_filter_replacement_interval`): Days between filter changes

### Switch Entities
- **Summer Mode** (`switch.parmair_mac_summer_mode`): Enable/disable summer mode operation
- **Time Program** (`switch.parmair_mac_time_program`): Enable/disable scheduled time programs
- **Heater Enable** (`switch.parmair_mac_post_heater`): Enable/disable heating element
- **Boost Mode** (`switch.parmair_mac_boost_mode`): Activate high-speed ventilation with timer
- **Overpressure Mode** (`switch.parmair_mac_overpressure_mode`): Activate supply-only ventilation with timer

### Button Entities
- **Acknowledge Alarms** (`button.parmair_mac_acknowledge_alarms`): Clear active alarms
- **Filter Replaced** (`button.parmair_mac_filter_replaced`): Reset filter replacement counter

### Select Entities
- **Heater Type** (`select.parmair_mac_heater_type`): Configure heater type (None, Water, Electric)

> **⚠️ Heater Control Warning:**
> 
> Disabling the heating elements entirely carries inherent risks and may void warranty coverage. While heating elements are the primary energy-consuming components in the ventilation system, they are essential for freeze protection and optimal operation.
> 
> When using external automation systems (such as Home Assistant) to override the device's built-in control logic, the manufacturer cannot accept liability for component failures or malfunctions that occur during the warranty period. Any damage resulting from modified heater control settings may not be covered under warranty.

### Sensor Entities

**Temperature Sensors:**
- **Fresh Air Temperature** (`sensor.parmair_mac_fresh_air_temperature`): Outdoor air temperature
- **Supply Air Temperature** (`sensor.parmair_mac_supply_air_temperature`): Air temperature being supplied to rooms
- **Exhaust Air Temperature** (`sensor.parmair_mac_exhaust_air_temperature`): Air temperature being extracted
- **Waste Air Temperature** (`sensor.parmair_mac_waste_air_temperature`): Air temperature being exhausted outside

**State Sensors:**
- **Control State** (`sensor.parmair_mac_control_state`): Current operating mode (Stop, Away, Home, Boost, Overpressure)
- **Power State** (`sensor.parmair_mac_power_state`): Power status (Off, Shutting Down, Starting, Running)
- **Current Speed** (`sensor.parmair_mac_current_speed`): Active fan speed (0-5)
- **Boost Timer** (`sensor.parmair_mac_boost_timer`): Remaining boost time in minutes (-1 when inactive)
- **Overpressure Timer** (`sensor.parmair_mac_overpressure_timer`): Remaining overpressure time in minutes (-1 when inactive)

**Alarm Sensors:**
- **Alarm Count** (`sensor.parmair_mac_alarm_count`): Number of active alarms
- **Summary Alarm** (`sensor.parmair_mac_summary_alarm`): Overall alarm status
- **Alarms State** (`sensor.parmair_mac_alarms_state`): Detailed alarm information

**Optional Sensors** (if hardware is present):
- **Humidity** (`sensor.parmair_mac_humidity`): Indoor humidity level (displays all values including 0%, updates continuously)
- **Humidity 24h Average** (`sensor.parmair_mac_humidity_24h_avg`): Daily average humidity (displays all values including negatives)
- **CO2 Exhaust Air** (`sensor.parmair_mac_co2_exhaust_air`): Exhaust air CO2 concentration (software 2.x only, MAC 2 devices, displays all values including -1 during calibration)

**Diagnostic Sensors:**
- **Software Version** (`sensor.parmair_mac_software_version`): Multi24 controller software version
- **Hardware Type** (`sensor.parmair_mac_hardware_type`): Device model (80, 100, or 150)
- **Heater Type** (`sensor.parmair_mac_heater_type`): Installed heater configuration

## Performance

The integration uses a **default polling interval of 30 seconds**, which balances responsiveness with device performance:

- **Why 30 seconds?** The Parmair device has limited Modbus TCP processing capacity. More frequent polling can cause transaction conflicts.
- **Sequential reads**: Registers are read one at a time with 200ms delays to prevent overwhelming the device
- **Connection cycling**: The integration reconnects on each poll to clear stale responses
- **Configurable**: You can adjust the polling interval during setup (10-120 seconds recommended)

**Note**: If you see "transaction_id mismatch" errors in logs, the integration includes timing optimizations to handle these. They typically don't affect functionality.

## Troubleshooting

For developer documentation, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Connection Issues
- Verify the IP address is correct and the device is on the same network
- Check that Modbus TCP port is accessible (default port 502)
- Confirm the Modbus slave ID matches your device configuration (typically 0 for Parmair devices)
- If experiencing "transaction_id mismatch" errors, the integration includes timing optimizations
- Default slave ID changed from 1 to 0 in v0.9.0.5 to match Parmair device responses

### Missing Sensors
- Some sensors (humidity, CO2) only appear if the hardware is installed
- Check the device's Modbus configuration to ensure sensors are enabled

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## License

MIT License

---

## Disclaimer

This is an independent, personal project developed by a community member and is **not affiliated with, endorsed by, or supported by Parmair or its parent companies**. This integration is provided as-is, without any warranty or guarantee. The Parmair name and product references are used solely for identification purposes.

For official support, product information, or warranty claims, please contact Parmair directly through their official channels.

Use of this integration is at your own risk. The author assumes no liability for any damage, malfunction, or warranty voidance that may result from using this software with your Parmair ventilation system.
