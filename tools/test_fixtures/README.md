# Parmair Test Fixtures

This directory contains sample JSON dump files from Parmair ventilation units.
These files are used to test the integration's data interpretation logic without
requiring access to a real device.

## File Naming Convention

Files should be named to describe the device:
- `mac80_v1.json` - MAC 80 with firmware 1.x
- `mac100_v1.json` - MAC 100 with firmware 1.x
- `mac150_v2.json` - MAC 150 with firmware 2.x

## Contributing Fixtures

If you have a Parmair device, you can contribute test data:

1. **Dump your device data:**

   ```bash
   cd tools
   python dump_registers.py <your_device_ip> --output test_fixtures/macXXX_vX.json
   ```

2. **Review the dump** to ensure it doesn't contain sensitive network info
   (the host IP is recorded but can be anonymized)

3. **Test the fixture:**

   ```bash
   python test_interpretation.py test_fixtures/macXXX_vX.json --verbose
   ```

4. Submit a pull request with your fixture file

## JSON Format

Each fixture file contains:

```json
{
  "metadata": {
    "timestamp": "2026-01-10T12:00:00",
    "host": "192.168.1.100",
    "port": 502,
    "slave_id": 1,
    "register_map_version": "1.x",
    "detected_software_version": 1.83,
    "detected_hardware_type": 100
  },
  "registers": {
    "register_key": {
      "address": 1020,
      "label": "TE01_M",
      "raw": -50,
      "scaled": -5.0,
      "scale": 0.1,
      "optional": false,
      "writable": false
    }
  }
}
```

## Testing

Run tests against all fixtures:

```bash
python test_interpretation.py --all
```

Or test a specific file:

```bash
python test_interpretation.py test_fixtures/mac100_v1.json
```

