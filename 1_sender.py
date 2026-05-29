# 1_sender.py
# reads IoT_Telemetry.xlsx and sends each row to the MQTT broker
# run AFTER starting 2_receiver.py
#
# python 1_sender.py

import time
import json
import pandas as pd
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT   = 1883
TOPIC  = "iot/energy"
DELAY  = 1.0
FILE   = "IoT_Telemetry.xlsx"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-device-001")

def on_connect(c, userdata, flags, rc, props=None):
    if rc == 0:
        print("connected to broker")
    else:
        print(f"connection failed, code: {rc}")

client.on_connect = on_connect

print(f"connecting to {BROKER}:{PORT} ...")
client.connect(BROKER, PORT)
client.loop_start()
time.sleep(1)

print(f"reading {FILE} ...")
df = pd.read_excel(FILE, sheet_name="Telemetry Data", header=1)
df = df.dropna(subset=["Timestamp"])
print(f"loaded {len(df)} rows\n")

count = 0

for _, row in df.iterrows():
    msg = {
        "device":    str(row["Device"]),
        "timestamp": str(row["Timestamp"]),
        "voltage_V": round(float(row["Voltage (V)"]),    2),
        "current_A": round(float(row["Current (A)"]),    2),
        "power_W":   round(float(row["Power (W)"]),      1),
        "temp_C":    round(float(row["Temperature (°C)"]), 2),
    }

    topic = f"{TOPIC}/{msg['device']}"
    client.publish(topic, json.dumps(msg), qos=1)

    count += 1
    print(f"  sent #{count:>4}  |  {msg['device']}  |  "
          f"V={msg['voltage_V']}  I={msg['current_A']}  "
          f"P={msg['power_W']}  T={msg['temp_C']}")

    time.sleep(DELAY)

print(f"\ndone — {count} messages sent")
client.loop_stop()
client.disconnect()