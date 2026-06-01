# Parmair MAC for Home Assistant (v0.15.0)

![Parmair MAC Logo](parmair_logo.jpg)

**Control your Parmair ventilation system from Home Assistant.**

Perfect for creating smart automations, monitoring air quality, and managing your home's ventilation from anywhere.

---

## What You Can Do

✅ **Control ventilation modes** - Switch between Home, Away, and Boost  
✅ **Monitor air quality** - Track temperature, humidity, and CO2 levels  
✅ **Create automations** - Schedule ventilation based on time, occupancy, or air quality  
✅ **Get notifications** - Alerts when filters need changing or alarms occur  
✅ **Adjust settings remotely** - Change fan speeds and temperature targets from anywhere  

---

## Quick Start

### Installation (3 Steps)

**1. Add to HACS**
- Open HACS → Click ⋮ (top right) → Custom repositories
- Add: `https://github.com/ValtteriAho/Hassio_Parmair`
- Category: Integration → Add
- Find "Parmair MAC" → Download
- Restart Home Assistant

**2. Find Your Device IP**
- Check your router's connected devices list
- Look for "Parmair" or "MAC" device
- Note the IP address (e.g., 192.168.1.100)

**3. Add Integration**
- Settings → Devices & Services → Add Integration
- Search "Parmair MAC"
- Enter your device's IP address
- Click Submit → Done!

> 💡 **That's it!** The integration automatically detects your device model, software version, and available features.

---

## Troubleshooting

### Can't Connect?

**Check your IP address**
- Make sure the IP is correct (check your router)
- Device must be on the same network as Home Assistant

**Still not working?**
- Port: Should be `502` (usually auto-configured)
- **Slave ID: Must be `0` (not 1!)** ← Most common issue!
  - If you installed before February 2026, your Slave ID might be wrong
  - Delete the integration and re-add it

### Sensors Not Updating?

**Restart Home Assistant** after installing the integration.

**Some sensors missing?**
- Humidity and CO2 sensors only appear if your device has that hardware
- Check your Parmair device specifications

**Sensors showing 0 or -1?**
- This is normal! The device reports these values during calibration
- Sensors update every 30 seconds
- -1 means "calibrating" for CO2 sensors
- 0% humidity is a valid reading

### Need More Help?

[Open an issue on GitHub](https://github.com/ValtteriAho/Hassio_Parmair/issues) with:
- Your device model (MAC80/100/150)
- Software version (visible in Home Assistant after setup)
- What's not working

---

## What You Get

Once installed, you'll have control over:

### Main Controls
- **Fan Entity** - Power on/off and mode switching (Away/Home/Boost)
- **Speed Presets** - Set fan speeds for each mode (Home, Away, Boost)
- **Temperature Targets** - Adjust supply and exhaust temperature setpoints
- **Timers** - Control how long Boost and Overpressure modes run

### Monitoring
- **Temperatures** - Fresh air, supply, exhaust, and waste air
- **Humidity** - Current level and 24-hour average (if equipped)
- **CO2 Levels** - Exhaust air quality monitoring (if equipped)
- **Operating Status** - Current mode, speed, and power state
- **Alarms** - Active warnings and filter status

### Smart Features
- **Operational Mode** - See exactly what the unit is doing and why (Home, Away, Boost, CO2 Boost, Humidity Boost, Summer Cooling, etc.) *(v2.x)*
- **Summer Mode** - Automatically adjusts ventilation based on outdoor temperature
- **CO2 Automations** - Auto Boost or Home/Away switching when CO2 exceeds thresholds *(v2.x)*
- **Humidity Automation** - Auto Boost when humidity rises above 24h average *(v2.x)*
- **Cold Speed Reduction** - Automatically reduce fan speed in very cold conditions *(v2.x)*
- **Heat Pump Module** - Status and settings for the maalämpömoduuli add-on, when installed *(v2.x)*
- **Time Programs** - Enable/disable scheduled operation
- **Heater Control** - Manage heating elements (see warning below)
- **Filter Tracking** - Monitor when filters need replacement

> **⚠️ Heater Control Warning:**
> 
> Disabling the heating elements entirely carries inherent risks and may void warranty coverage. While heating elements are the primary energy-consuming components in the ventilation system, they are essential for freeze protection and optimal operation.
> 
> When using external automation systems (such as Home Assistant) to override the device's built-in control logic, the manufacturer cannot accept liability for component failures or malfunctions that occur during the warranty period. Any damage resulting from modified heater control settings may not be covered under warranty.

---

## Dashboard Example

Use the ready-made Lovelace view template in [docs/dashboard_example.yaml](docs/dashboard_example.yaml).

- [docs/dashboard_example.yaml](docs/dashboard_example.yaml) is for the dashboard raw YAML editor (full view config with `title:` and `views:`)
- For Add card -> Manual, use a single-card config from [docs/dashboard_manual_card_examples.yaml](docs/dashboard_manual_card_examples.yaml)
- Replace entity IDs with your own (entity IDs can vary by device name)

## Example Automations

More complete examples are available in [docs/automation_examples.yaml](docs/automation_examples.yaml).

### Boost When Cooking
```yaml
automation:
  - alias: "Boost ventilation when cooking"
    trigger:
      - platform: state
        entity_id: binary_sensor.kitchen_motion
        to: "on"
    action:
      - service: fan.set_preset_mode
        target:
          entity_id: fan.parmair_mac
        data:
          preset_mode: "Boost"
```

### Away Mode When Nobody Home
```yaml
automation:
  - alias: "Reduce ventilation when away"
    trigger:
      - platform: state
        entity_id: group.all_persons
        to: "not_home"
        for: "00:30:00"
    action:
      - service: fan.set_preset_mode
        target:
          entity_id: fan.parmair_mac
        data:
          preset_mode: "Away"
```

### Filter Change Reminder
```yaml
automation:
  - alias: "Remind to change filter"
    trigger:
      - platform: state
        entity_id: sensor.parmair_mac_filter_status
        to: "Replace"
    action:
      - service: notify.mobile_app
        data:
          title: "Ventilation Filter"
          message: "Time to change the air filter!"
```

---

## Supported Devices

This integration supports Parmair MAC units by firmware generation:

- **Software v2.x**: Supported across MAC product variants.
- **Software v1.x**: Supported when the Parmair IoT package is installed and Modbus TCP is available.

The integration automatically detects your software version and uses the correct register map.

---

## Advanced Information

<details>
<summary>Complete Entity List (Click to expand)</summary>

### Controls
- Fan: Main power and mode control
- Home Speed: Fan speed when in Home mode (v1: 0–4, v2: 1–5)
- Away Speed: Fan speed when in Away mode (v1: 0–4, v2: 1–5)
- Boost Speed: Fan speed level for Boost mode (v1: 2–4, v2: 3–5)
- Boost Duration: How long Boost mode runs (30–180 min)
- Overpressure Duration: How long Overpressure mode runs (15–120 min)
- Exhaust Temperature: Target temperature for exhaust air (18–26 °C)
- Supply Temperature: Target temperature for supply air (15–25 °C)
- Summer Mode Temperature: Outdoor temp limit for summer mode
- Filter Interval: Filter change interval (3 / 4 / 6 months)
- CO2 Home Threshold: CO2 level (ppm) that triggers Home mode *(v2.x)*
- CO2 Boost Threshold: CO2 level (ppm) that triggers Boost mode *(v2.x)*
- Heat Pump Winter Limit: Outdoor temp below which heat pump activates in winter *(v2.x, if installed)*
- Heat Pump Summer Limit: Outdoor temp above which heat pump activates in summer *(v2.x, if installed)*

### Switches
- Summer Mode: Enable/disable summer cooling automation *(v2.x)*
- Time Program: Enable/disable scheduled operation
- Heater: Enable/disable heating elements
- Boost Mode: Activate high-speed ventilation
- Overpressure Mode: Supply-only ventilation (fireplace/overpressure mode)
- Auto CO2 Boost: Automatically boost when CO2 exceeds threshold *(v2.x)*
- Auto Humidity Boost: Automatically boost when humidity is elevated *(v2.x)*
- Auto CO2 Home/Away: Switch Home/Away mode based on CO2 level *(v2.x)*
- Auto Cold Speed Reduction: Reduce speed in very cold outdoor conditions *(v2.x)*

### Buttons
- Acknowledge Alarms: Clear active warnings
- Filter Replaced: Reset filter change counter

### Sensors
- **Operational Mode**: Derived status showing effective mode and automation trigger (Off / Away / Home / Boost / CO2 Boost / Humidity Boost / Summer Cooling / Sauna / Fireplace) *(v2.x)*
- **Heat Pump Output**: Whether the heat pump module is currently active *(v2.x, if installed)*
- **Heat Pump Mode**: Automation mode for the heat pump module (Off / On / Auto) *(v2.x, if installed)*
- All temperature sensors, humidity, CO2, fan speeds, operating states, timers, alarms, and diagnostic information

</details>

<details>
<summary>Technical Details (Click to expand)</summary>

### Communication
- Protocol: Modbus TCP
- Default Port: 502
- Slave ID: 0 (changed from 1 in v0.9.0.5)
- Polling: Every 30 seconds (configurable 10-120s)

### Requirements
- Home Assistant 2023.1 or newer
- Network connectivity to Parmair device
- Modbus TCP must be enabled on device

### Performance
The integration reads registers sequentially with 200ms delays to prevent overwhelming the device. Updates occur every 30 seconds by default. More frequent polling may cause communication errors.

### Version Detection
The integration automatically reads:
- Hardware model (MAC80/100/150)
- Software version (1.x or 2.x)
- Heater type (Water/Electric/None)
- Available sensors (humidity, CO2)

If auto-detection fails, you can manually select these during setup.

</details>

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

**Latest:** v0.15.0 - Heat pump module (maalämpömoduuli) support

---

## Support & Contributing

- **Issues or Questions**: [GitHub Issues](https://github.com/ValtteriAho/Hassio_Parmair/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **License**: MIT

---

## Disclaimer

⚠️ **Not Official**: This is an independent project, not affiliated with or endorsed by Parmair.

**Use at your own risk.** The author assumes no liability for damage, malfunction, or warranty voidance. For official support, contact Parmair directly.

Modifying heater control or other critical settings through automation may void your warranty. Understand the risks before disabling safety features.
