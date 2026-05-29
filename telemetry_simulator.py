# telemetry_simulator.py
# reads IoT_Telemetry.xlsx and shows a live terminal dashboard
# python telemetry_simulator.py

import time
import sys
import pandas as pd

EXCEL_FILE = "IoT_Telemetry.xlsx"
DELAY = 1.0

safe_ranges = {
    "voltage":     (390, 410),
    "current":     (0,   45),
    "power":       (0,   15000),
    "temperature": (0,   32),
}

LINES = 46


def load_data():
    print("loading Excel file...")
    df = pd.read_excel(EXCEL_FILE, sheet_name="Telemetry Data", header=1)
    df = df.dropna(subset=["Timestamp"])

    data = []
    for _, row in df.iterrows():
        data.append({
            "device": str(row["Device"]),
            "time":   str(row["Timestamp"]),
            "volt":   round(float(row["Voltage (V)"]),      2),
            "curr":   round(float(row["Current (A)"]),      2),
            "pwr":    round(float(row["Power (W)"]),        1),
            "temp":   round(float(row["Temperature (°C)"]), 2),
        })

    print(f"loaded {len(data)} readings\n")
    return data


def status(key, val):
    lo, hi = safe_ranges[key]
    if val > hi: return "WARNING HIGH !"
    if val < lo: return "WARNING LOW  !"
    return "ok"


def bar(val, lo, hi, w=25):
    pct = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    n = int(pct * w)
    return "[" + "=" * n + " " * (w - n) + "]" + f" {int(pct*100)}%"


first = True

def show(r, row_num, total):
    global first

    v, i, p, t = r["volt"], r["curr"], r["pwr"], r["temp"]

    lines = [
        "=" * 60,
        "   IoT Telemetry Simulator",
        "=" * 60,
        "",
        f"  device   : {r['device']}",
        f"  time     : {r['time']}",
        f"  row      : {row_num} / {total}",
        f"  speed    : {DELAY}s per reading  |  Ctrl+C to stop",
        "",
        "-" * 60,
        "  sensor readings",
        "-" * 60,
        "",
        "  voltage",
        f"    value  : {v:.2f} V",
        f"    level  : {bar(v, 379, 415)}",
        f"    status : {status('voltage', v):<20}",
        "",
        "  current",
        f"    value  : {i:.2f} A",
        f"    level  : {bar(i, 16, 51)}",
        f"    status : {status('current', i):<20}",
        "",
        "  power",
        f"    value  : {p:.0f} W  /  {p/1000:.2f} kW",
        f"    level  : {bar(p, 5000, 18500)}",
        f"    status : {status('power', p):<20}",
        "",
        "  temperature",
        f"    value  : {t:.2f} C",
        f"    level  : {bar(t, 20, 35)}",
        f"    status : {status('temperature', t):<20}",
        "",
        "-" * 60,
        f"  mqtt topic : iot/energy/{r['device']}",
        "-" * 60,
        "  {",
        f'    "device"    : "{r["device"]}",',
        f'    "time"      : "{r["time"]}",',
        f'    "voltage_V" : {v},',
        f'    "current_A" : {i},',
        f'    "power_W"   : {p},',
        f'    "temp_C"    : {t}',
        "  }",
        "",
        "=" * 60,
    ]

    if not first:
        sys.stdout.write(f"\033[{LINES}A")
    first = False

    for line in lines:
        sys.stdout.write(line.ljust(62) + "\n")
    sys.stdout.flush()


def main():
    print("\n  starting up...\n")
    readings = load_data()
    total = len(readings)

    print(f"  {total} readings ready")
    print(f"  starting in 3 seconds...\n")
    time.sleep(3)

    for n, r in enumerate(readings, start=1):
        show(r, n, total)
        time.sleep(DELAY)

    print(f"\n  done — {total} readings simulated\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nstopped\n")