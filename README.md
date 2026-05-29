# IoT Data Pipeline

A Python IoT pipeline that reads real industrial energy data (voltage, current, power, temperature) from 5 devices, transmits it over MQTT, and stores all readings in a PostgreSQL database.

---

## How to Run

### what you need installed
- Python 3.10+
- PostgreSQL 17
- Mosquitto

### install python packages
```
pip install pandas openpyxl paho-mqtt psycopg2-binary
```

### start PostgreSQL and Mosquitto
open command prompt as administrator and run:
```
net start postgresql-x64-17
net start mosquitto
```

### run the files in this order

first — setup the database (only need to do this once):
```
python 0_setup_db.py
```

second — start the receiver in one terminal and leave it running:
```
python 2_receiver.py
```

third — open a new terminal and run the sender:
```
python 1_sender.py
```

check what got saved anytime:
```
python 3_check_db.py
```

---

## Why MQTT

I used MQTT because it was built specifically for IoT devices. It keeps one connection open and just sends small messages through it, which is much better than HTTP which opens a new connection every single time.

Each reading gets published to a topic like `iot/energy/MCH_1`. The receiver listens on `iot/energy/#` which catches all machines at once. I used QoS 1 so the broker confirms every message was received — nothing gets lost silently.

Mosquitto is the broker sitting in the middle. The sender pushes messages to it, the receiver pulls them and saves to the database.

---

## Database Schema

```sql
CREATE TABLE telemetry (
    id          SERIAL PRIMARY KEY,
    device_id   VARCHAR(50)  NOT NULL,
    timestamp   TIMESTAMPTZ  NOT NULL,
    voltage_v   NUMERIC(8,3),
    current_a   NUMERIC(8,3),
    power_w     NUMERIC(10,2),
    temp_c      NUMERIC(6,2),
    received_at TIMESTAMPTZ DEFAULT NOW()
);
```

pretty straightforward — one row per reading. `received_at` is separate from `timestamp` so we know both when the device took the reading and when it actually arrived in the database. there's a unique index on `(device_id, timestamp)` so if the sender is restarted it won't create duplicate rows.

---

## Dataset

Kaggle industrial energy dataset — 1200 rows across 5 machines, 5-minute intervals over one working day. each row has voltage, current, power factor, temperature, and a bunch of production context columns. i just pulled the 4 sensor columns we needed.

---

## Results after running

```
total rows : 1200

MCH_1  240 rows   avg 400V  25.9A   9506W  27.4C
MCH_2  240 rows   avg 400V  37.0A  13524W  27.4C
MCH_3  240 rows   avg 399V  22.5A   8197W  27.9C
MCH_4  240 rows   avg 400V  34.6A  12680W  27.1C
MCH_5  240 rows   avg 400V  28.0A  10243W  27.2C

temperature warnings found: MCH_3 hit 35.0C, MCH_4 hit 34.97C
```

---

## Files

```
0_setup_db.py          creates the database and table
1_sender.py            reads excel, sends via MQTT
2_receiver.py          receives MQTT messages, saves to postgres
3_check_db.py          shows whats in the database
telemetry_simulator.py live terminal dashboard (bonus)
IoT_Telemetry.xlsx     the kaggle dataset
```
