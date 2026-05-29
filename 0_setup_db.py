# 0_setup_db.py
# run this once to create the database and table
# python 0_setup_db.py

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

HOST     = "localhost"
PORT     = 5432
USER     = "postgres"
PASSWORD = "postgres"
DB_NAME  = "iot_pipeline"

print("setting up database...")

try:
    conn = psycopg2.connect(host=HOST, port=PORT, dbname="postgres",
                            user=USER, password=PASSWORD)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if cur.fetchone():
        print(f"'{DB_NAME}' already exists, skipping")
    else:
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"created database '{DB_NAME}'")

    cur.close()
    conn.close()

except Exception as e:
    print(f"error: {e}")
    exit(1)

try:
    conn = psycopg2.connect(host=HOST, port=PORT, dbname=DB_NAME,
                            user=USER, password=PASSWORD)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id          SERIAL PRIMARY KEY,
            device_id   VARCHAR(50)  NOT NULL,
            timestamp   TIMESTAMPTZ  NOT NULL,
            voltage_v   NUMERIC(8,3),
            current_a   NUMERIC(8,3),
            power_w     NUMERIC(10,2),
            temp_c      NUMERIC(6,2),
            received_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_device_ts
        ON telemetry (device_id, timestamp)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_device_ts
        ON telemetry (device_id, timestamp DESC)
    """)

    print("table created")
    cur.close()
    conn.close()

except Exception as e:
    if "already exists" in str(e):
        print("table already exists")
    else:
        print(f"error: {e}")
        exit(1)

print("\ndone — now run 2_receiver.py then 1_sender.py")