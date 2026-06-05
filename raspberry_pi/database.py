import sqlite3
import os
from datetime import datetime

# ─── Database Path ────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "irrigation.db")

# ─── Init ─────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         DATETIME DEFAULT CURRENT_TIMESTAMP,
            zone              INTEGER,
            soil_moisture_1   REAL,
            soil_moisture_2   REAL,
            temperature       REAL,
            humidity          REAL,
            flow_rate         REAL,
            rain_mm           REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS valve_commands (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
            zone          INTEGER,
            valve_num     INTEGER,
            duration_sec  INTEGER,
            source        TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

# ─── Insert Sensor Reading ────────────────────────────────────────────────────
def insert_reading(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_readings
        (zone, soil_moisture_1, soil_moisture_2, temperature, humidity, flow_rate, rain_mm)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("zone"),
        data.get("soil_moisture_1"),
        data.get("soil_moisture_2"),
        data.get("temperature"),
        data.get("humidity"),
        data.get("flow_rate"),
        data.get("rain_mm")
    ))
    conn.commit()
    conn.close()

# ─── Insert Valve Command ─────────────────────────────────────────────────────
def insert_valve_command(zone: int, valve_num: int, duration_sec: int, source: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO valve_commands (zone, valve_num, duration_sec, source)
        VALUES (?, ?, ?, ?)
    ''', (zone, valve_num, duration_sec, source))
    conn.commit()
    conn.close()

# ─── Fetch Last N Readings for a Zone ────────────────────────────────────────
def fetch_last_readings(zone: int, n: int = 20) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, soil_moisture_1, soil_moisture_2,
               temperature, humidity, flow_rate, rain_mm
        FROM sensor_readings
        WHERE zone = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (zone, n))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    test_data = {
        "zone": 1,
        "soil_moisture_1": 42.5,
        "soil_moisture_2": 38.1,
        "temperature": 28.3,
        "humidity": 61.2,
        "flow_rate": 2.4,
        "rain_mm": 0.0
    }
    insert_reading(test_data)
    insert_valve_command(1, 1, 120, "MPC")
    rows = fetch_last_readings(1, 5)
    print(f"[DB] Last readings: {rows}")
    print("[DB] Test passed ✓")