#!/usr/bin/env python3
"""Discover all readable Modbus registers on a Parmair device.

This tool scans a range of register addresses and reports which ones
return valid data. Use this to discover undocumented registers.

Usage:
    python discover_registers.py <host> [--start 1000] [--end 1300]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from pymodbus.client import ModbusTcpClient

# Known V2 documented registers (from v2_register.md)
V2_DOCUMENTED = {
    1003: "ACK_ALARMS",
    1004: "ALARM_COUNT",
    1009: "TIME_YEAR",
    1010: "TIME_MONTH",
    1011: "TIME_DAY",
    1012: "TIME_HOUR",
    1013: "TIME_MIN",
    1014: "MULTI_FW_VER",
    1015: "MULTI_SW_VER",
    1016: "MULTI_BL_VER",
    1020: "TE01_M",
    1021: "TE05_M",
    1022: "TE10_M",
    1023: "TE31_M",
    1024: "TE30_M",
    1025: "ME05_M",
    1026: "QE05_M",
    1027: "TF10_I",
    1028: "PF30_I",
    1029: "ME20_M",
    1030: "QE20_M",
    1031: "EXTERNAL_M",
    1035: "EXTERNAL_BOOST_M",
    1036: "TE10_DEFECTION_M",
    1040: "TF10_Y",
    1042: "PF30_Y",
    1044: "TV45_Y",
    1046: "FG50_Y",
    1048: "EC05_Y",
    1050: "HP_RAD_O",
    1060: "HOME_SPEED_S",
    1061: "TE10_MIN_HOME_S",
    1062: "TE10_CONTROL_MODE_S",
    1063: "AWAY_SPEED_S",
    1064: "TE10_MIN_AWAY_S",
    1065: "BOOST_SETTING_S",
    1068: "OVERP_AMOUNT_S",
    1070: "TP_ENABLE_S",
    1071: "AUTO_SUMMER_COOL_S",
    1072: "AUTO_SUMMER_POWER_S",
    1073: "TE30_S",
    1074: "AUTO_HEATER_ENABLE_S",
    1075: "AUTO_COLD_LOWSPEED_S",
    1076: "COLD_LOWSPEED_S",
    1077: "AUTO_HUMIDITY_BOOST_S",
    1078: "ME05_BOOST_SENSITIVITY",
    1079: "ME_BST_TE01_LIMIT",
    1080: "AUTO_CO2_BOOST_S",
    1081: "AUTO_HOMEAWAY_S",
    1082: "QE_HOME_S",
    1083: "QE_BOOST_S",
    1090: "FILTER_INTERVAL_S",
    1091: "HP_RAD_MODE",
    1092: "HP_RAD_WINTER",
    1093: "HP_RAD_SUMMER",
    1094: "HEATING_SEASON_AVERAGE",
    1095: "HEATING_SEASON_MOMENT",
    1096: "TE10_MIN_SUMMER_S",
    1097: "TE10_MAX_S",
    1098: "BST_TE01_LIMIT",
    1105: "M10_TYPE",
    1106: "M11_TYPE",
    1107: "M12_TYPE",
    1108: "SF_SPEED1_S",
    1109: "SF_SPEED2_S",
    1110: "SF_SPEED3_S",
    1111: "SF_SPEED4_S",
    1112: "SF_SPEED5_S",
    1113: "EF_SPEED1_S",
    1114: "EF_SPEED2_S",
    1115: "EF_SPEED3_S",
    1116: "EF_SPEED4_S",
    1117: "EF_SPEED5_S",
    1120: "SENSOR_TE_COR",
    1121: "SENSOR_ME_COR",
    1122: "SENSOR_CO2_COR",
    1124: "HEATPUMP_RADIATOR_ENABLE",
    1125: "VENT_MACHINE",
    1129: "TE10_MIN_S",
    1137: "TE10_BASE_S",
    1140: "BST_MINTIME",
    1141: "CO2_MINTIME",
    1144: "BST_TIME_LIMIT",
    1180: "UNIT_CONTROL_FO",
    1181: "USERSTATECONTROL_FO",
    1182: "DFRST_FI",
    1183: "FG50_EA_M",
    1184: "FILTER_STATE_FI",
    1185: "SENSOR_STATUS",
    1189: "SUMMER_MODE_I",
    1190: "SUMMER_POWER_CHANGE_F",
    1191: "HUMIDITY_FM",
    1192: "ME05_AVG_FM",
    1199: "PWR_LIMIT_FY",
    1213: "TE01_AVG_FM",
    1220: "TE01_FA",
    1221: "TE10_FA",
    1222: "TE05_FA",
    1223: "TE30_FA",
    1224: "TE31_FA",
    1225: "ME05_FA",
    1226: "TF10_CA",
    1227: "PF30_CA",
    1228: "TE10_HA",
    1229: "TE30_HA",
    1230: "TE10_LA",
    1240: "FILTER_FA",
}


def read_register(client: ModbusTcpClient, address: int, slave_id: int) -> int | None:
    """Try to read a single register. pymodbus 3.10+ uses device_id=; older uses slave=."""
    try:
        result = client.read_holding_registers(address, count=1, device_id=slave_id)
    except TypeError:
        try:
            result = client.read_holding_registers(address, count=1, slave=slave_id)
        except TypeError:
            try:
                result = client.read_holding_registers(address, 1, unit=slave_id)
            except TypeError:
                return None

    try:
        if hasattr(result, "isError") and result.isError():
            return None
        if hasattr(result, "registers") and result.registers:
            return result.registers[0]
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Discover Modbus registers on Parmair device")
    parser.add_argument("host", help="Device IP address")
    parser.add_argument("--port", type=int, default=502, help="Modbus port (default: 502)")
    parser.add_argument("--slave", type=int, default=1, help="Slave ID (default: 1)")
    parser.add_argument("--start", type=int, default=1000, help="Start address (default: 1000)")
    parser.add_argument("--end", type=int, default=1300, help="End address (default: 1300)")
    parser.add_argument("--output", type=str, help="Output JSON file")

    args = parser.parse_args()

    print(f"Connecting to {args.host}:{args.port}...")
    client = ModbusTcpClient(args.host, port=args.port)

    if not client.connect():
        print("Failed to connect!")
        sys.exit(1)

    print(f"Scanning registers {args.start} to {args.end}...")
    print()

    documented = []
    undocumented = []

    for addr in range(args.start, args.end + 1):
        value = read_register(client, addr, args.slave)

        if value is not None:
            is_documented = addr in V2_DOCUMENTED
            label = V2_DOCUMENTED.get(addr, "???")
            status = "✓" if is_documented else "?"

            entry = {
                "address": addr,
                "value": value,
                "label": label,
                "documented": is_documented,
            }

            if is_documented:
                documented.append(entry)
            else:
                undocumented.append(entry)

            # Print progress
            print(f"  {status} {addr:4d}: {value:6d}  {label}")

    client.close()

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Documented registers found: {len(documented)}")
    print(f"Undocumented registers found: {len(undocumented)}")
    print()

    if undocumented:
        print("UNDOCUMENTED REGISTERS (need investigation):")
        print("-" * 60)
        for entry in undocumented:
            print(f"  Address {entry['address']:4d}: value={entry['value']:6d}")

    # Save to file if requested
    if args.output:
        output_data = {
            "host": args.host,
            "timestamp": datetime.now().isoformat(),
            "scan_range": {"start": args.start, "end": args.end},
            "documented": documented,
            "undocumented": undocumented,
        }

        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
