# 4_show_schema.py
# shows the database schema and live stats
# python 4_show_schema.py

import psycopg2

DB = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "iot_pipeline",
    "user":     "postgres",
    "password": "postgres",
}

try:
    conn = psycopg2.connect(**DB)
    cur  = conn.cursor()
except Exception as e:
    print(f"could not connect: {e}")
    exit(1)

print()
print("=" * 65)
print("  DATABASE : iot_pipeline")
print("  TABLE    : telemetry")
print("=" * 65)

print()
print("  COLUMNS")
print("  " + "-" * 62)
print(f"  {'column':<16} {'type':<22} {'description':<24}")
print("  " + "-" * 62)

columns = [
    ("id",          "SERIAL",             "auto-increment primary key"),
    ("device_id",   "VARCHAR(50)",        "machine name e.g. MCH_1"),
    ("timestamp",   "TIMESTAMPTZ",        "when reading was taken"),
    ("voltage_v",   "NUMERIC(8,3)",       "voltage in Volts"),
    ("current_a",   "NUMERIC(8,3)",       "current in Amperes"),
    ("power_w",     "NUMERIC(10,2)",      "power in Watts"),
    ("temp_c",      "NUMERIC(6,2)",       "temperature in Celsius"),
    ("received_at", "TIMESTAMPTZ",        "auto-filled when row arrives"),
]

for col, dtype, desc in columns:
    print(f"  {col:<16} {dtype:<22} {desc:<24}")

print()
print("  CONSTRAINTS")
print("  " + "-" * 62)
print("  PRIMARY KEY  ->  id")
print("  UNIQUE       ->  (device_id, timestamp)")
print("  INDEX        ->  (device_id, timestamp DESC)")

print()
print("  SQL")
print("  " + "-" * 62)
print("""  CREATE TABLE telemetry (
      id          SERIAL PRIMARY KEY,
      device_id   VARCHAR(50)  NOT NULL,
      timestamp   TIMESTAMPTZ  NOT NULL,
      voltage_v   NUMERIC(8,3),
      current_a   NUMERIC(8,3),
      power_w     NUMERIC(10,2),
      temp_c      NUMERIC(6,2),
      received_at TIMESTAMPTZ DEFAULT NOW()
  );""")

print()
print("  LIVE STATS")
print("  " + "-" * 62)

cur.execute("SELECT COUNT(*) FROM telemetry")
total = cur.fetchone()[0]
print(f"  total rows    : {total}")

cur.execute("SELECT COUNT(DISTINCT device_id) FROM telemetry")
devices = cur.fetchone()[0]
print(f"  devices       : {devices}")

cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM telemetry")
mn, mx = cur.fetchone()
print(f"  date range    : {str(mn)[:19]}  ->  {str(mx)[:19]}")

print()
print("  ROWS PER DEVICE")
print("  " + "-" * 62)
cur.execute("""
    SELECT device_id, COUNT(*) FROM telemetry
    GROUP BY device_id ORDER BY device_id
""")
rows = cur.fetchall()
max_rows = max(r[1] for r in rows)
for row in rows:
    bar_len = int((row[1] / max_rows) * 40)
    bar = "[" + "=" * bar_len + " " * (40 - bar_len) + "]"
    print(f"  {row[0]}   {bar}  {row[1]} rows")

print()
print("  SAMPLE DATA (last 5 rows)")
print("  " + "-" * 62)
print(f"  {'device':<8} {'timestamp':<22} {'voltage':>9} {'current':>9} {'power':>10} {'temp':>7}")
print("  " + "-" * 62)
cur.execute("""
    SELECT device_id, timestamp, voltage_v, current_a, power_w, temp_c
    FROM telemetry ORDER BY received_at DESC LIMIT 5
""")
for r in cur.fetchall():
    print(f"  {r[0]:<8} {str(r[1])[:19]:<22} "
          f"{r[2]:>7.2f}V  {r[3]:>7.2f}A  {r[4]:>8.1f}W  {r[5]:>5.2f}C")

print()
print("  AVERAGES PER DEVICE")
print("  " + "-" * 62)
print(f"  {'device':<8} {'avg V':>9} {'avg A':>9} {'avg W':>10} {'avg C':>8}")
print("  " + "-" * 62)
cur.execute("""
    SELECT device_id,
           ROUND(AVG(voltage_v)::numeric, 2),
           ROUND(AVG(current_a)::numeric, 2),
           ROUND(AVG(power_w)::numeric,   1),
           ROUND(AVG(temp_c)::numeric,    2)
    FROM telemetry GROUP BY device_id ORDER BY device_id
""")
for r in cur.fetchall():
    print(f"  {r[0]:<8} {r[1]:>7.2f}V  {r[2]:>7.2f}A  {r[3]:>8.1f}W  {r[4]:>6.2f}C")

print()
print("=" * 65)
cur.close()
conn.close()