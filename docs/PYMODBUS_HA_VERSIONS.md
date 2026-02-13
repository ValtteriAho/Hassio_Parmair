# Home Assistant vs pymodbus versions

Home Assistant’s **built-in Modbus** integration pins a specific pymodbus version in `homeassistant/components/modbus/manifest.json`. That version can differ between HA releases and changes when you upgrade HA.

This integration supports all of these by detecting the correct unit-ID parameter on first use (see `custom_components/parmair/pymodbus_compat.py`).

## Unit/slave ID parameter by pymodbus version

| pymodbus version | Parameter for unit/slave ID | Notes |
|------------------|-----------------------------|--------|
| **3.10.0+**      | `device_id=`                | Renamed from `slave=` in 3.10.0 (API change). |
| **3.7.x – 3.9.x**| `slave=`                    | Default unit ID in calls is often 1. |
| **3.5.x – 3.6.x**| `slave=` or `unit=`         | Older 3.x. |
| **3.1.x – 3.4.x**| `slave=` or `unit=`         | Even older 3.x. |
| **2.x**          | `unit=`                     | Legacy; HA modbus moved to 3.x in 2023. |

So: **pymodbus ≥ 3.10** use `device_id=`, **&lt; 3.10** use `slave=` (or `unit=` in some older releases).

## HA Modbus manifest history (which HA ships which pymodbus)

From `home-assistant/core` `homeassistant/components/modbus/manifest.json`:

| Date (commit) | pymodbus version | Likely HA release |
|---------------|------------------|-------------------|
| Sep 2025      | **3.11.2**      | 2025.10.x         |
| Aug 2025      | 3.11.1, 3.11.0  | 2025.9, 2025.8    |
| Jun 2025      | **3.9.2**       | 2025.6.x          |
| Jan 2025      | **3.8.3**       | 2025.1.x          |
| Dec 2024      | **3.7.4**       | 2024.12.x         |
| Jul 2024      | 3.6.9           | 2024.7.x          |
| Apr 2024      | 3.6.8, 3.6.7    | 2024.4.x          |
| Mar 2024      | 3.6.6, 3.6.5    | 2024.3.x          |
| Feb 2024      | **3.6.4**      | 2024.2.x          |
| Jan 2024      | 2.6.3 → 3.6.x   | 2024.1.x          |
| Oct 2023      | 3.5.4           | 2023.10.x         |
| Sep 2023      | 3.5.0–3.5.2     | 2023.9.x          |
| Aug 2023      | 3.4.1           | 2023.8.x          |
| Jun 2023      | 3.3.1           | 2023.6.x          |
| Feb 2023      | 3.1.0–3.1.3     | 2023.2.x          |
| Oct 2021      | 2.5.3           | 2021.10.x         |

So:

- **HA 2025.8+** (pymodbus 3.11.0+): use **`device_id=`**.
- **HA 2025.6 and earlier** in the table (pymodbus 3.9.2 and below): use **`slave=`** (or `unit=` on very old 3.x / 2.x).

Custom integrations like Parmair can declare their own `pymodbus` requirement (e.g. `pymodbus>=3.11.2`), but when installed as a custom component they often end up using the **same pymodbus** as the HA environment (e.g. the one installed for the built-in Modbus integration). So in practice, the version that runs may still be the one from the HA release.

That’s why the Parmair integration does **not** assume a single pymodbus API: it tries `device_id=` then `slave=` then `unit=` on first use and caches the one that works, so it behaves correctly across HA versions and after upgrades.

## References

- [HA modbus manifest.json](https://github.com/home-assistant/core/blob/dev/homeassistant/components/modbus/manifest.json)
- [HA modbus manifest commit history](https://github.com/home-assistant/core/commits/dev/homeassistant/components/modbus/manifest.json)
- [pymodbus API changes (3.10+: device_id)](https://pymodbus.readthedocs.io/en/stable/source/api_changes.html)
