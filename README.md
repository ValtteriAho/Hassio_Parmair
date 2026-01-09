# Parmair MAC - Home Assistant Integration v0.9.0

![Parmair MAC Logo](parmair_logo.jpg)

A custom Home Assistant integration for Parmair MAC ventilation systems via Modbus TCP communication.

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
  - Software version (Multi24 firmware)
  - Register metadata exposed via entity attributes for diagnostics
  
- **Local Polling**: Direct communication with your device via Modbus TCP
- **Automatic Model Detection**: Reads hardware type register to identify MAC80/MAC100/MAC150 automatically
- **Firmware Version Detection**: Automatically detects firmware version (1.x or 2.x) for optimal register mapping

## System Information

This integration supports Parmair "My Air Control" systems:
- **Firmware 1.x**: Fully supported (Modbus spec 1.87)
- **Firmware 2.x**: Fully supported (Modbus spec 2.28)

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
    - Modbus Slave ID (default: 1)
    - Polling Interval (default: 30 seconds)
    - Name (optional)

Hardware model will be auto-detected from the device.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 1)

The hardware model (MAC80/MAC100/MAC150) and firmware version (1.x/2.x) are automatically detected by reading the VENT_MACHINE and MULTI_SW_VER registers.

## Entities Created

### Fan Entity
- **parmair_mac**: Main control for the ventilation system
  - Presets: Away, Home, Boost
  - Speed control (percentage based on preset)

### Number Entities
- **Home Speed Preset**: Adjust fan speed for Home mode (0-4)
- **Away Speed Preset**: Adjust fan speed for Away mode (0-4)
- **Boost Setting**: Set boost fan speed level (2-4)
- **Exhaust Temperature Setpoint**: Target exhaust air temperature (18-26°C)
- **Supply Temperature Setpoint**: Target supply air temperature (15-25°C)

### Switch Entities
- **Summer Mode**: Enable/disable summer mode operation
- **Time Program Enable**: Enable/disable scheduled time programs
- **Heater Enable**: Enable/disable heating element

### Sensor Entities
- **Fresh Air Temperature**: Outdoor air temperature
- **Supply Air Temperature**: Air temperature being supplied to rooms
- **Exhaust Air Temperature**: Air temperature being extracted
- **Waste Air Temperature**: Air temperature being exhausted outside
- **Exhaust/Supply Temperature Setpoints**: Target temperatures
- **Control State**: Current operating mode (Stop, Away, Home, Boost, etc.)
- **Power State**: Power status (Off, Shutting Down, Starting, Running)
- **Home/Away State**: Whether system is in home or away mode (Home/Away)
- **Boost State**: Whether boost mode is active (On/Off)
- **Boost Timer**: Remaining boost time in minutes
- **Alarm Count**: Number of active alarms
- **Summary Alarm**: Overall alarm status

Optional sensors (if hardware is present):
- **Humidity**: Indoor humidity level
- **CO2**: Indoor CO2 concentration
- Entity attributes include diagnostic information to aid troubleshooting

Diagnostic sensors:
- **Software Version**: Multi24 firmware application version (used for firmware family detection)
- **Firmware Family**: Automatically detected as 1.x or 2.x based on software version

## Modbus Registers

All register mappings are documented in `MODBUS_REGISTERS.md`. The integration uses:
- Holding registers (Function codes 03, 06, 16)
- int16 data type
- Temperature scaling factor of 10 (210 = 21.0°C)

## Development

This integration follows Home Assistant's development guidelines and uses:
- `pymodbus` (tested with 3.11.x bundled in Home Assistant 2025.12) for Modbus communication
- `DataUpdateCoordinator` for efficient data fetching (30-second polling)
- Config flow for user-friendly setup
- Proper error handling and retry logic

## Troubleshooting

### Connection Issues
- Verify the IP address is correct and the device is on the same network
- Check that port 502 is not blocked by firewalls
- Confirm the Modbus slave ID matches your device configuration

### Missing Sensors
- Some sensors (humidity, CO2) only appear if the hardware is installed
- Check the device's Modbus configuration to ensure sensors are enabled

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## Release Notes

### 0.9.0
- **Full Firmware 2.xx Support**: Complete Modbus register mappings for firmware 2.28
- **Automatic Version Detection**: Seamless switching between 1.xx and 2.xx register maps
- **Control Compatibility**: Enhanced control system for firmware 2.xx
- **All Features Working**: Sensors, controls, switches, numbers, and buttons fully functional on both firmware versions

### 0.8.1
- **Timer Fix**: Fixed boost and overpressure timer minimum value from 0 to -1
- **Inactive Display**: Timers now correctly show -1 when inactive per Modbus specification

### 0.8.0
- **Device Info**: Clarified software version display in device information
- **Label Consistency**: Home Assistant controls display label (Firmware/Software)

### 0.7.7.3
- **Syntax Fix**: Corrected indentation in heater type detection retry logic

### 0.7.7.2
- **Documentation Cleanup**: Removed Modbus register addresses from public documentation

### 0.7.7.1
- **Current Speed**: Speed sensor now shows numeric values (0-5) instead of text

### 0.7.7
- **Auto-Detection**: Retry logic with up to 3 attempts for version/heater detection
- **Smart Defaults**: Uses sensible defaults if detection fails

### 0.7.6
- **Real Speed**: Speed sensor now shows actual running speed instead of control setting

## License

MIT License

---

## Disclaimer

This is an independent, personal project developed by a community member and is **not affiliated with, endorsed by, or supported by Parmair or its parent companies**. This integration is provided as-is, without any warranty or guarantee. The Parmair name and product references are used solely for identification purposes.

For official support, product information, or warranty claims, please contact Parmair directly through their official channels.

Use of this integration is at your own risk. The author assumes no liability for any damage, malfunction, or warranty voidance that may result from using this software with your Parmair ventilation system.
