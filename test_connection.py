"""Example script to test Modbus connection to Parmair device.

Run this script to verify your Parmair device is accessible via Modbus
before setting up the Home Assistant integration.

Usage:
    python test_connection.py <host> [port] [slave_id]

Example:
    python test_connection.py 192.168.1.100
    python test_connection.py 192.168.1.100 502 0
"""

import sys

from pymodbus.client import ModbusTcpClient

# Register addresses from const.py (subtract 1 from register ID)
REGISTER_POWER = 207  # Register 208
REGISTER_CONTROL_STATE = 184  # Register 185
REGISTER_EXHAUST_TEMP = 23  # Register 24
REGISTER_SUPPLY_TEMP = 22  # Register 23


def _read_register(client, address, slave_id):
    """Read one register; pymodbus 3.10+ uses device_id=, older uses slave=."""
    try:
        return client.read_holding_registers(address, 1, device_id=slave_id)
    except TypeError:
        return client.read_holding_registers(address, 1, slave=slave_id)


def test_connection(host, port=502, slave_id=0):
    """Test connection to Parmair device."""
    print(f"Connecting to Parmair device at {host}:{port} (slave ID: {slave_id})")

    client = ModbusTcpClient(host=host, port=port)

    try:
        # Connect to device
        if not client.connect():
            print("❌ Failed to connect to device")
            print("   Check IP address, port, and network connectivity")
            return False

        print("✅ Connected successfully")

        # Test reading power status
        print("\nReading registers...")
        result = _read_register(client, REGISTER_POWER, slave_id)

        if result.isError():
            print(f"❌ Error reading register {REGISTER_POWER}: {result}")
            print("   Check slave ID and Modbus configuration")
            return False

        power_state = result.registers[0]
        power_states = {0: "Off", 1: "Shutting down", 2: "Starting", 3: "Running"}
        print(
            f"✅ Power State (Reg 208): {power_state} ({power_states.get(power_state, 'Unknown')})"
        )

        # Read control state
        result = _read_register(client, REGISTER_CONTROL_STATE, slave_id)
        if not result.isError():
            control_state = result.registers[0]
            control_states = {
                0: "STOP",
                1: "AWAY",
                2: "HOME",
                3: "BOOST",
                4: "OVERPRESSURE",
                9: "MANUAL",
            }
            print(
                f"✅ Control State (Reg 185): {control_state} ({control_states.get(control_state, f'Mode {control_state}')})"
            )

        # Read exhaust temperature
        result = _read_register(client, REGISTER_EXHAUST_TEMP, slave_id)
        if not result.isError():
            temp = result.registers[0] / 10.0
            print(f"✅ Exhaust Temperature (Reg 24): {temp}°C")

        # Read supply temperature
        result = _read_register(client, REGISTER_SUPPLY_TEMP, slave_id)
        if not result.isError():
            temp = result.registers[0] / 10.0
            print(f"✅ Supply Temperature (Reg 23): {temp}°C")

        print("\n" + "=" * 50)
        print("✅ Connection test successful!")
        print("=" * 50)
        print("\nYou can now add the Parmair integration in Home Assistant:")
        print("  1. Go to Settings → Devices & Services")
        print("  2. Click '+ ADD INTEGRATION'")
        print("  3. Search for 'Parmair'")
        print(f"  4. Enter host: {host}, port: {port}, slave ID: {slave_id}")

        return True

    except Exception as ex:
        print(f"❌ Exception occurred: {ex}")
        return False

    finally:
        client.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <host> [port] [slave_id]")
        print("Example: python test_connection.py 192.168.1.100")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    slave_id = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    try:
        success = test_connection(host, port, slave_id)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
