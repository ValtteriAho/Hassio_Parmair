# Parmair Ventilation - Home Assistant Integration

A custom Home Assistant integration for Parmair ventilation systems via Modbus TCP communication.

## Features

- **Fan Control**: Control your Parmair ventilation unit including:
  - Power on/off
  - Mode selection (Away, Home, Boost)
  - Speed control via presets
  
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
  
- **Local Polling**: Direct communication with your device via Modbus TCP

## System Information

This integration targets Parmair "My Air Control" firmware V1.87 behaviour observed on production units.

## Installation

### Manual Installation

1. Copy the `custom_components/parmair` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Parmair Ventilation"
5. Enter your device's connection details:
   - IP Address
   - Port (default: 502)
   - Modbus Slave ID (default: 1)
   - Name (optional)

## Configuration

The integration is configured through the Home Assistant UI. You'll need:

- **IP Address**: The IP address of your Parmair device
- **Port**: The Modbus TCP port (typically 502)
- **Slave ID**: The Modbus slave ID of your device (typically 1)

## Entities Created

### Fan Entity
- **parmair_ventilation**: Main control for the ventilation system
  - Presets: Away, Home, Boost
  - Speed control (percentage based on preset)

### Sensor Entities
- **Fresh Air Temperature**: Outdoor air temperature
- **Supply Air Temperature**: Air temperature being supplied to rooms
- **Exhaust Air Temperature**: Air temperature being extracted
- **Waste Air Temperature**: Air temperature being exhausted outside
- **Exhaust/Supply Temperature Setpoints**: Target temperatures
- **Control State**: Current operating mode
- **Power State**: Power status (0=Off, 3=Running)
- **Home/Away State**: Whether system is in home or away mode
- **Boost State**: Whether boost mode is active
- **Boost Timer**: Remaining boost time in minutes
- **Alarm Count**: Number of active alarms
- **Summary Alarm**: Overall alarm status

Optional sensors (if hardware is present):
- **Humidity**: Indoor humidity level
- **CO2**: Indoor CO2 concentration

## Modbus Registers

All register mappings are documented in `MODBUS_REGISTERS.md`. The integration uses:
- Holding registers (Function codes 03, 06, 16)
- int16 data type
- Temperature scaling factor of 10 (210 = 21.0°C)
- Register addresses offset by -1 from documentation IDs

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

## Documentation

- [Modbus Register Documentation](MODBUS_REGISTERS.md)

## License

MIT License
