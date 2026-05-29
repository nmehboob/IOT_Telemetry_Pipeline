# 2_receiver.py
# listens on MQTT and saves every message to PostgreSQL
# start this BEFORE 1_sender.py
#
# python 2_receiver.py

import json
import signal
import sys
import psycopg2
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT   = 1883
TOPIC  = "iot/energy/#"

DB = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "iot_pipeline",
    "user":     "postgres",
    "password": "postgres",
}

print("connecting to database...")
try:
    conn = psycopg2.connect(**DB)
    conn.autocommit = True
    cur  = conn.cursor()
    print("connected\n")
except Exception as e:
    print(f"database error: {e}")
    sys.exit(1)

INSERT = """
    INSERT INTO telemetry (device_id, timestamp, voltage_v, current_a, power_w, temp_c)
    VALUES (%(device)s, %(timestamp)s, %(voltage_V)s, %(current_A)s, %(power_W)s, %(temp_C)s)
    ON CONFLICT (device_id, timestamp) DO NOTHING
"""

saved = 0

def on_connect(client, userdata, flags, rc, props=None):
    if rc == 0:
        print(f"connected to broker — listening on {TOPIC}")
        client.subscribe(TOPIC, qos=1)
    else:
        print(f"failed to connect, code: {rc}")

def on_message(client, userdata, msg):
    global saved

    try:
        data = json.loads(msg.payload.decode())
    except Exception as e:
        print(f"bad message: {e}")
        return

    try:
        cur.execute(INSERT, data)
        saved += 1
        print(f"  saved #{saved:>4}  |  {data.get('device')}  |  "
              f"{data.get('timestamp')}  |  "
              f"P={data.get('power_W')}W  T={data.get('temp_C')}C")
    except Exception as e:
        print(f"  db error: {e}")

def on_disconnect(client, userdata, flags, rc=None, props=None):
    print("disconnected")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-db-writer")
client.on_connect    = on_connect
client.on_message    = on_message
client.on_disconnect = on_disconnect

print(f"connecting to broker at {BROKER}:{PORT} ...")
try:
    client.connect(BROKER, PORT)
except Exception as e:
    print(f"broker error: {e}")
    sys.exit(1)

def stop(sig, frame):
    print(f"\nsaved {saved} rows total — stopping")
    client.loop_stop()
    client.disconnect()
    cur.close()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT,  stop)
signal.signal(signal.SIGTERM, stop)

print("waiting for messages... (Ctrl+C to stop)\n")
client.loop_forever()