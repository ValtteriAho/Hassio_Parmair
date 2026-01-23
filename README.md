# Parmair MAC - Home Assistant Integration v0.10.5

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
    - Modbus Slave ID (default: 0)
    - Polling Interval (default: 30 seconds)
    - Name (optional)

Hardware model and firmware version will be auto-detected from the device. If auto-detection fails, you can manually select firmware version and heater type.

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 0)

The hardware model (MAC80/MAC100/MAC150) and firmware version (1.x/2.x) are automatically detected. If detection fails during setup, you can manually select your firmware version and heater type.

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

> **⚠️ Heater Control Warning:**
> 
> Disabling the heating elements entirely carries inherent risks and may void warranty coverage. While heating elements are the primary energy-consuming components in the ventilation system, they are essential for freeze protection and optimal operation.
> 
> When using external automation systems (such as Home Assistant) to override the device's built-in control logic, the manufacturer cannot accept liability for component failures or malfunctions that occur during the warranty period. Any damage resulting from modified heater control settings may not be covered under warranty.

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
- **CO2 Indoor Air**: Indoor air CO2 concentration (firmware 1.x and 2.x)
- **CO2 Exhaust Air**: Exhaust air CO2 concentration (firmware 2.x only)
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
- `pymodbus>=3.11.2` for Modbus TCP communication
- Modern pymodbus 3.x API (legacy compatibility code removed in v0.10.0)
- `DataUpdateCoordinator` for efficient data fetching with configurable timing
- Config flow with auto-detection and manual fallback
- Proper error handling and connection management

## Troubleshooting

### Connection Issues
- Verify the IP address is correct and the device is on the same network
- Check that port 502 is not b(typically 0 for Parmair devices)
- If experiencing "transaction_id mismatch" errors, the integration includes timing optimizations
- Default slave ID changed from 1 to 0 in v0.9.0.5 to match Parmair device responses
- Confirm the Modbus slave ID matches your device configuration

### Missing Sensors
- Some sensors (humidity, CO2) only appear if the hardware is installed
- Check the device's Modbus configuration to ensure sensors are enabled

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## Changelog

### 0.10.2 (2026-01-18)
- **Exhaust CO2 Sensor**: Added exhaust air CO2 sensor for firmware v2.xx devices
- **Complete Monitoring**: Firmware 2.xx users now get both indoor and exhaust CO2 measurements
- **Backward Compatible**: Exhaust CO2 shows as unavailable on firmware 1.xx devices

### 0.10.1 (2026-01-18)
- **CRITICAL FIX**: Fixed heater type mapping for firmware v2.xx
- **Reversed Values**: Corrected heater type detection where values were reversed between firmware versions
- **Safety**: Ensures correct heater identification for all device configurations

### 0.10.0 (2026-01-18)
- **Code Cleanup**: Removed all legacy pymodbus compatibility code
- **Simplified API**: Now uses only modern pymodbus 3.11.2+ API
- **50% Less Complexity**: Cleaner, more maintainable codebase
- **No Functional Changes**: Drop-in replacement for 0.9.11

### 0.9.1 (Earlier)1 (2026-01-18)
- **Pymodbus 3.x Fix**: Fixed API compatibility for pymodbus 3.11.2+
- **Detection Working**: Register reads during setup now succeed
- **Version Logging**: Added pymodbus version detection for diagnostics

### 0.9.0 (Earlier).9-0.9.0.10 (2026-01-18)
- **Connection Warm-up**: Device "warm-up" phase before detection (reads power register 5 times)
- **Manual Fallback**: If auto-detection fails, user can manually select firmware version and heater type
- **Better UX**: No more forced defaults to 1.xx
x (Earlier)
### 0.9.0.5-0.9.0.8 (2026-01-17)
- **Default Slave ID Changed**: Now defaults to 0 instead of 1 (matches Parmair devices)
- **Detection Timing**: Improved delays for reliable firmware detection
- **Documentation Cleanup**: Removed Modbus register addresses from public documentation
- **Current Speed**: Speed sensor now shows numeric values (0-5) instead of text
- **Auto-Detection**: Retry logic with up to 3 attempts for version/heater detection
- **Smart Defaults**: Uses sensible defaults if detection fails
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
