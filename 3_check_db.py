# 3_check_db.py
# shows everything stored in the database
# python 3_check_db.py

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

print("=" * 60)
print("  DATABASE — iot_pipeline.telemetry")
print("=" * 60)

cur.execute("SELECT COUNT(*) FROM telemetry")
total = cur.fetchone()[0]
print(f"\n  total rows saved : {total}")

if total == 0:
    print("\n  no data yet — run 1_sender.py and 2_receiver.py first")
    exit()

print("\n  rows per device:")
cur.execute("""
    SELECT device_id, COUNT(*) FROM telemetry
    GROUP BY device_id ORDER BY device_id
""")
for r in cur.fetchall():
    print(f"    {r[0]}  ->  {r[1]} rows")

print("\n  last 5 readings:")
print(f"  {'device':<8} {'timestamp':<22} {'voltage':>9} {'current':>9} {'power':>10} {'temp':>7}")
print("  " + "-" * 68)
cur.execute("""
    SELECT device_id, timestamp, voltage_v, current_a, power_w, temp_c
    FROM telemetry ORDER BY received_at DESC LIMIT 5
""")
for r in cur.fetchall():
    print(f"  {r[0]:<8} {str(r[1]):<22} "
          f"{r[2]:>7.2f}V  {r[3]:>7.2f}A  {r[4]:>8.1f}W  {r[5]:>5.2f}C")

print("\n  averages per device:")
print(f"  {'device':<8} {'avg V':>8} {'avg A':>8} {'avg W':>10} {'avg C':>8}")
print("  " + "-" * 48)
cur.execute("""
    SELECT device_id,
           ROUND(AVG(voltage_v)::numeric, 2),
           ROUND(AVG(current_a)::numeric, 2),
           ROUND(AVG(power_w)::numeric,   1),
           ROUND(AVG(temp_c)::numeric,    2)
    FROM telemetry GROUP BY device_id ORDER BY device_id
""")
for r in cur.fetchall():
    print(f"  {r[0]:<8} {r[1]:>7.2f}V  {r[2]:>7.2f}A  {r[3]:>9.1f}W  {r[4]:>7.2f}C")

print("\n  high temp warnings (above 32C):")
cur.execute("""
    SELECT device_id, timestamp, temp_c FROM telemetry
    WHERE temp_c > 32 ORDER BY temp_c DESC LIMIT 5
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"    {r[0]}  {str(r[1])}  ->  {r[2]}C  WARNING")
else:
    print("    none")

print("\n" + "=" * 60)
cur.close()
conn.close()