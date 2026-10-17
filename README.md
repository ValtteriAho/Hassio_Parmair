# Parmair MAC for Home Assistant (v1.1.2)

![Parmair MAC Logo](parmair_logo.jpg)

**Control your Parmair ventilation system from Home Assistant.**

Perfect for creating smart automations, monitoring air quality, and managing your home's ventilation from anywhere.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub release](https://img.shields.io/github/v/release/ValtteriAho/Hassio_Parmair?include_prereleases)](https://github.com/ValtteriAho/Hassio_Parmair/releases)
[![License](https://img.shields.io/github/license/ValtteriAho/Hassio_Parmair)](LICENSE)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-yellow.svg?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/valtteriah0)
[![Donate PayPal](https://img.shields.io/badge/Donate-PayPal-00457C.svg?logo=paypal&logoColor=white)](https://paypal.me/valtteriah0)

---

## What You Can Do

✅ **Control ventilation modes** - Switch between Away, Home, Boost, and more (Sauna/Fireplace for v2.x)  
✅ **Monitor air quality** - Track temperature, humidity, and CO2 levels  
✅ **Track power & heat recovery** - Live electrical power (fans, post-heater, total) and thermal power recovered by heat exchanger (Watts)  
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

## ⚙️ Configuration Options

You can adjust runtime settings anytime via **Settings → Devices & Services → Parmair MAC → Configure**:

- **Update Interval (`scan_interval`):** Polling frequency between 5 and 300 seconds (default: `60` seconds).
- **Custom Fan Rating (`custom_fan_rating`):** Override the default nominal fan power (W per fan) to calibrate power calculations with your own energy meter (e.g. Shelly).
- **Custom Heater Rating (`custom_heater_rating`):** Override electric post-heater wattage (e.g. 1000 W or 2000 W).
- **Connection Details:** Update Host IP or device name without needing to remove and re-add the integration.

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
- Sensors update every 60 seconds (or your configured polling interval)
- -1 means "calibrating" for CO2 sensors
- 0% humidity is a valid reading

### Need More Help?

[Open an issue on GitHub](https://github.com/ValtteriAho/Hassio_Parmair/issues) with:
- **Diagnostic download:** In Home Assistant, go to *Settings → Devices & Services → Parmair MAC*, click the three dots (**⋮**) and select **Download diagnostics** (IP addresses and personal identifiers are automatically redacted).
- Your device model (MAC 70, 80, 100, 105, 120, 150, 170, 220, 250, Rexo, Lämpöiivari II)
- Software version (visible on device page, e.g. `2.28` or `1.87`)
- What's not working or error logs from Home Assistant

---

## What You Get

Once installed, you'll have control over:

### Main Controls
- **Control State** - Dedicated mode selector (`select.parmair_mac_control_state`) to switch between Away, Home, Boost (plus Sauna and Fireplace on v2.x) with no awkward on/off toggles
- **Speed Presets** - Configure preset fan speeds for each mode (Home Speed, Away Speed, Boost Speed)
- **Manual Speed Control** - Direct fan speed override *(v1.x only; on v2.x speed is managed via mode presets)*
- **Temperature Targets** - Adjust supply and exhaust temperature setpoints with 0.5 °C precision
- **Timers** - Control how long Boost and Overpressure modes run

### Power & Energy (Energy Dashboard Ready)
- **Total Energy (`kWh`)** - State-restoring cumulative electrical energy (`sensor.parmair_mac_total_energy`). Adds directly to the official **Home Assistant Energy Dashboard** (*Individual Devices*) with zero manual helpers.
- **Total Power (`W`)** - Real-time electrical power consumption of the entire ventilation unit (fans + active electric heating + 5 W standby electronics).
- **Fan Power (`W`)** - Active electrical power drawn by EC supply and exhaust fans, calculated via a calibrated empirical affinity law model ($P = P_{\text{max}} \times (\text{speed}/100)^{2.55}$).
- **Post-Heater Power (`W`)** - Active electrical power consumed by electric post-heating (0 W for water-heated or unequipped systems).
- **Heat Recovery Thermal Power (`W`)** - Live thermal power recovered from exhaust air by the rotary heat exchanger (LTO).
- **Heat Recovery Efficiency (`%`)** - Real-time thermal efficiency percentage of heat recovery.

### Monitoring
- **Temperatures** - Fresh air (*ulkoilma*), supply air (*tuloilma*), exhaust air (*poistoilma*), waste air (*jäteilma*), and supply after recovery (*LTO jälkeen*)
- **Fan Speeds** - Running fan speed percentages for supply and exhaust fans
- **Humidity** - Current level and 24-hour average (if equipped)
- **CO2 Levels** - Exhaust air quality monitoring (if equipped)
- **Operating Status** - Current mode, speed, and power state
- **Heater Type** - Detected heater hardware (Electric, Water, or None)
- **Alarms** - Active warnings, defrost status, and filter replacement counter

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

## Dashboard & Lovelace Custom Card

### Built-in Parmair MAC Card (`custom:parmair-mac-card`)

The integration ships with a built-in Lovelace card featuring an authentic Scandinavian 2D schematic, animated airflow arrows, live air duct temperatures, rotating heat recovery exchanger (LTO), heating element glow effects, real-time power metrics, and one-touch mode buttons.

#### ✨ Key Features
- **Interactive 2D HVAC Schematic:**
  - **4 Air Duct Badges:** Fresh air (*Ulkoilma*), Supply air (*Tuloilma*), Exhaust air (*Poistoilma*), and Waste air (*Jäteilma*) with live temperatures.
  - **Animated Airflow Arrows:** Directional glowing chevron arrows representing physical air circulation.
  - **Rotary Heat Exchanger (LTO):** Animated rotating rotor showing thermal recovery efficiency (%) and recovered heat power (W).
  - **Electric / Water Post-Heater:** Visual heater glow with active heating output (%) and real-time heating power (W).
  - **Interactive Tap Actions:** Clicking any temperature badge or metric opens Home Assistant's detailed `more-info` dialog with history graphs.
- **Power & Energy Metrics:**
  - Live EC fan power (W) and speed percentages (*Tulo / Poisto*).
  - Post-heater electric power (W) and total ventilation unit electrical power (W).
- **One-Touch Mode Selector:**
  - Direct touch controls matching the Parmair physical controller: **Poissa** (*Away*), **Kotona** (*Home*), **Tehostus** (*Boost*), **Sauna**, and **Takka** (*Fireplace*).
- **Maintenance & Diagnostics:**
  - Filter replacement countdown bar (days remaining).
  - Active alarms and defrost protection status.

#### 🚀 How to Add the Card to Your Dashboard

##### Method 1: Graphical Card Picker (Recommended)
1. In Home Assistant, open any Dashboard.
2. Click the three dots (**⋮**) in the top right corner → **Edit Dashboard**.
3. Click **Add Card** (at the bottom).
4. Search for or select **Parmair MAC Card**.
5. The visual card editor will preview your ventilation unit immediately. Click **Save**!

##### Method 2: Manual YAML Card
If editing in YAML or using a manual card:
```yaml
type: custom:parmair-mac-card
```

*(Optional customization parameters)*:
```yaml
type: custom:parmair-mac-card
title: "Ilmanvaihto" # Custom card title (defaults to Parmair MAC)
```

> [!TIP]
> **Browser Cache Notice (Ctrl + F5):**  
> When installing for the first time or updating via HACS, your browser may cache older frontend assets. If the card does not immediately appear in the "Add Card" picker, perform a hard refresh in your browser (**Ctrl + F5** / **Cmd + Shift + R**) or clear the cache in the Home Assistant Companion App (*Settings → Companion App → Debugging → Clear Cache*).

### Alternative YAML Cards
- **[docs/dashboard_manual_card_examples.yaml](docs/dashboard_manual_card_examples.yaml)**: Manual YAML cards (Mushroom chips, picture-elements, entities).
- **[docs/dashboard_example.yaml](docs/dashboard_example.yaml)**: Full multi-section dashboard view configuration.

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
      - action: select.select_option
        target:
          entity_id: select.parmair_mac_control_state
        data:
          option: "Boost"
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
      - action: select.select_option
        target:
          entity_id: select.parmair_mac_control_state
        data:
          option: "Away"
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
      - action: notify.mobile_app
        data:
          title: "Ventilation Filter"
          message: "Time to change the air filter!"
```

---

## Supported Devices

The integration automatically detects your hardware model and software generation, loading the appropriate register mapping and power profiles:

### Hardware Models Supported
- **MAC Series:** MAC 70, MAC 80, MAC 100, MAC 105, MAC 105 SLIM, MAC 120, MAC 150, MAC 170, MAC 220, MAC 250
- **Rexo Series:** MAC Rexo 120, MAC Rexo 150
- **Lämpöiivari Series:** MAC Lämpöiivari II

### Firmware Generations
- **Software v2.x (Modbus 2.28+)**: Newer Parmair units with unified control state register (Away, Home, Boost, Sauna, Fireplace) and automatic boost logic.
- **Software v1.x (Modbus 1.87)**: Earlier units with IoT module (Away, Home, Boost).

---

## Advanced Information

<details>
<summary>Complete Entity List (Click to expand)</summary>

### Controls
- Control State: Ventilation mode selector (`select.parmair_mac_control_state`: Away, Home, Boost; plus Sauna & Fireplace on v2.x)
- Speed Presets: Fan speed preset per mode (Home Speed, Away Speed, Boost Speed)
- Manual Speed: Direct fan speed selector *(v1.x only)*
- Boost Duration: How long Boost mode runs (30–180 min)
- Overpressure Duration: How long Overpressure mode runs (15–120 min)
- Exhaust Temperature: Target temperature for exhaust air (18–26 °C, 0.5 °C steps)
- Supply Temperature: Target temperature for supply air (15–25 °C, 0.5 °C steps)
- Summer Mode Temperature: Outdoor temp limit for summer mode
- Filter Interval: Filter change interval (3 / 4 / 6 months)
- CO2 Home Threshold: CO2 level (ppm) that triggers Home mode *(v2.x)*
- CO2 Boost Threshold: CO2 level (ppm) that triggers Boost mode *(v2.x)*
- Heat Pump Winter Limit: Outdoor temp below which heat pump activates in winter *(v2.x, if installed)*
- Heat Pump Summer Limit: Outdoor temp above which heat pump activates in summer *(v2.x, if installed)*

### Switches
- Summer Mode: Enable/disable summer cooling automation *(v1.x switch; v2.x uses select)*
- Time Program: Enable/disable weekly scheduled operation
- Post Heater: Enable/disable post-heating element
- Auto CO2 Boost: Automatically boost when CO2 exceeds threshold *(v2.x)*
- Auto Humidity Boost: Automatically boost when humidity is elevated *(v2.x)*
- Auto CO2 Home/Away: Switch Home/Away mode based on CO2 level *(v2.x)*
- Auto Cold Speed Reduction: Reduce speed in very cold outdoor conditions *(v2.x)*

### Buttons
- Acknowledge Alarms: Clear active warnings
- Filter Replaced: Reset filter change counter

### Sensors
- **Total Energy**: Cumulative electrical energy consumption in `kWh` (`SensorDeviceClass.ENERGY`, Energy Dashboard ready)
- **Total Power**: Real-time electrical power consumption in `W` (fans + post-heater + standby electronics)
- **Fan Power**: Active electrical power drawn by EC supply and exhaust fans in `W`
- **Post Heater Power**: Active electrical power consumed by electric heating in `W`
- **Heat Recovery Thermal Power**: Heat power transferred to supply air by rotary heat exchanger in `W`
- **Heat Recovery Efficiency**: Thermal recovery efficiency percentage (%)
- **Operational Mode**: Derived status showing effective mode and automation trigger (Off / Away / Home / Boost / CO2 Boost / Humidity Boost / Summer Cooling / Sauna / Fireplace) *(v2.x)*
- **Heat Pump Output**: Whether the heat pump module is currently active *(v2.x, if installed)*
- **Heat Pump Mode**: Automation mode for the heat pump module (Off / On / Auto) *(v2.x, if installed)*
- **Heater Type**: Detected heater hardware (Electric / Water / None)
- **Temperatures**: Fresh air, supply air, exhaust air, waste air, supply after heat recovery
- **Fan Speeds**: Running fan speeds in % (Supply and Exhaust)
- **Humidity & CO2**: Current relative humidity, 24h average humidity, and exhaust CO2 levels (if equipped)
- **Alarms & Diagnostics**: Active alarms, filter days counter, software version, hardware model

</details>

<details>
<summary>Technical Details (Click to expand)</summary>

### Communication
- Protocol: Modbus TCP
- Default Port: 502
- Slave ID: 0 (changed from 1 in v0.9.0.5)
- Polling: Every 60 seconds by default (configurable 5–300s in options)

### Requirements
- Home Assistant 2023.1 or newer
- Network connectivity to Parmair device
- Modbus TCP must be enabled on device

### Performance
The integration batches register reads into optimized contiguous blocks with delays between requests to prevent overwhelming the device's Modbus stack. Updates occur every 60 seconds by default (configurable). Sub-zero temperatures are handled via signed 16-bit integer conversion.

### Version Detection
The integration automatically reads:
- Hardware model (MAC 70, 80, 100, 105, 120, 150, 170, 220, 250, Rexo 120/150, Lämpöiivari II)
- Software version (1.x or 2.x)
- Heater type (Water / Electric / None)
- Available sensors (humidity, CO2)

If auto-detection fails, you can manually select these during setup.

</details>

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

- **v1.1.2**: Harmonize dark mode background with official Home Assistant theme (`#1c1c1c` / `--ha-card-background`), full dynamic light theme compatibility (`.theme-dark` vs `.theme-light`), theme-adaptive vector chassis, and dynamic CSS text/border variables.
- **v1.1.1**: Dynamic manifest-driven cache-busting (`integration.version`), resilient resource lifecycle during configuration reloads, customElements double-definition protection, and DevTools console version badge.
- **v1.1.0**: Detected unit hardware model displayed dynamically in card header (e.g. `PARMAIR MAC 120`), in-card filter replacement confirmation and direct Modbus counter acknowledgment (`✓ Kuittaa`), locked 48px metric element height for zero layout shift, and new diagnostic `ParmairModelSensor` entity.
- **v1.0.0**: Official major production release and HACS default inclusion milestone, complete support for v1.x and v2.x Parmair MAC units, built-in dynamic Lovelace card (`custom:parmair-mac-card`), and calibrated power & energy telemetry.
- **v0.90.1**: Precision `<clipPath>` core boundary eliminating any lamella overhang beyond diamond perimeter, with 16 symmetrical crossing heat exchange lamellas (8+8) creating an authentic counterflow plate matrix.
- **v0.90.0**: Constant heat recovery (LTO) counterflow visualization subtly visible in the background through a modern translucent frosted metrics badge (`rgba(8, 12, 18, 0.76)`), with diamond base and lamella layering precision.
- **v0.80.0**: Full canonical English foundation, dynamic bilingual card localization (English & Finnish), Home Assistant native `_attr_translation_key` architecture, and automated Lovelace cache-busting.
- **v0.51.0**: Symmetrical 16px chevron arrow gaps with zero badge collision across all 4 ducts, two-line stacked post-heater badge (`Lämmitin` / `0.0 W`) preventing text overflow, comprehensive typography enlargement for mobile dashboards, and balanced 750px viewBox.
- **v0.50.1**: Compact two-line duct badges embedded inside pipes (`Ulkoilma`, `Poistoilma`, `Jäteilma`, `Tuloilma`), narrowed SVG viewBox (`68 15 664 438`) for better aspect ratio, unified central LTO diamond badge combining efficiency, intermediate temperature, and recovery power, physically accurate G4/G4/F7 filter placements, symmetric fan elevations, and mobile typography boost.
- **v0.30.1**: Instant Lovelace card static path registration during early component startup (`async_setup`), immediate card shadowRoot initialization for zero-wait dashboard card picker previews, and automated cache-busting Lovelace resource URL management.
- **v0.21.12**: Unobstructed duct airflow paths with channel temperature badges relocated above/below ducts, header chips for Humidity and CO2 sensors, 98% card loading speedup via Parmair entity caching, and enabled frontend HTTP caching.
- **v0.21.11**: Finnish LVI standard color palette, swapped supply/waste duct layout (crossed airflow architecture: Tuloilma on bottom-right, Jäteilma on bottom-left), and added interactive Humidity and CO2 sensor badges in the exhaust stream.
- **v0.21.10**: Optimize Home Assistant entity categories: promote waste air temperature, heat recovery efficiency, and fan speeds to primary Sensors, and move post-heater switch to Controls.
- **v0.21.9**: Calibrate EC fan power calculation exponent from 2.2 to 2.55 based on real-world Shelly energy meter measurements on Parmair MAC 150 across all 5 speeds, achieving 1–2 W precision.
- **v0.21.8**: Fix card element spacing and add real-time fan speed percentages directly beneath fan icons on the built-in card.
- **v0.21.7**: Built-in card overhaul (`custom:parmair-mac-card` / Tapa 1) with glowing multi-chevron airflow direction arrows and native click-to-inspect (`hass-more-info`) popup interaction across all sensors and metrics, establishing automatic zero-YAML HACS updates.
- **v0.21.6**: Add prominent multi-chevron airflow direction arrows with soft glowing tips in schematic SVG, make all card values interactive with `more-info` tap actions, and optimize channel coordinate alignment.
- **v0.21.5**: Fix post-heater electric power and energy estimation on firmware v2.xx units by correctly handling heater type enum inversion.
- **v0.21.4**: Add crisp vector channel titles (**ULKOILMA**, **POISTOILMA**, **TULOILMA**, **JÄTEILMA**) to schematic SVG, clear center LTO backdrop plate to prevent double-text overlapping in `picture-elements` cards, and align coordinate templates in dashboard examples.
- **v0.21.3**: Fully responsive Inline-SVG card architecture (`custom:parmair-mac-card`) with 100% vector-locked coordinates across all card sizes, physically accurate counterflow heat recovery airflow, fan speed and filter entity detection fixes, dynamic heater element illumination, and Ruff code formatting.
- **v0.21.2**: Fix automatic Lovelace card registration using `add_extra_js_url` and resource storage pre-loading so `custom:parmair-mac-card` is immediately available in the visual "Add Card" picker.
- **v0.21.1**: Add automatic Lovelace resource registration and visual editor support so `Parmair MAC Card` appears directly in the standard graphical **Add Card** dialog.
- **v0.21.0**: Ship built-in Lovelace custom card (`custom:parmair-mac-card`) served directly by the integration, providing an interactive Scandinavian 2D schematic, live temperatures, LTO recovery, electric heater monitoring, and mode control buttons.
- **v0.20.1**: Add native `sensor.parmair_mac_total_energy` (kWh) state-restoring sensor for out-of-the-box Home Assistant Energy Dashboard integration, and provide a full Scandinavian 2D schematic card in dashboard examples.
- **v0.20.0**: Add model-based power and energy estimation (EC fan power, electric heater power, total power, heat recovery thermal power) across all Parmair MAC hardware models, Home Assistant diagnostics support, and options flow overrides.
- **v0.19.0**: Refine v1/v2 select architecture (remove incompatible manual speed control on firmware 2.xx), enforce Home Assistant Core ENUM sensor contracts, fix typing annotations, and clean up switch logic.
- **v0.18.4**: Clean up coordinator connection lifecycle, remove redundant fan platform registration, type number device classes, and align polling documentation.
- **v0.18.3**: Fix decimal temperature setpoint truncation (0.5 °C steps), heater type auto-detection on firmware 2.xx, and options schema.
- **v0.18.2**: Ensure reliable Modbus write persistence with fresh connection per write; surface proper Home Assistant errors on write failures.
- **v0.18.1**: Fix Operational Mode automation detection (Humidity & CO2 Boost) in Home state.

## ☕ Support Ongoing Development

This integration is completely free and open source. Developing and maintaining a hardware-level HVAC integration requires continuous effort: reverse-engineering Parmair MAC Modbus registers across hardware generations (v1.x & v2.x), implementing safe thermal & fan control algorithms, modeling energy and power consumption, developing the built-in Lovelace card, and keeping up with monthly Home Assistant Core updates.

If this integration keeps your indoor air fresh, helps optimize your home heating, or brings value to your smart home, consider supporting its continued development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/valtteriah0)
[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/valtteriah0)

*Every coffee or donation is deeply appreciated and directly helps support ongoing maintenance, testing, and new features!*

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
