import time
from database       import init_db
from mqtt_handler   import start_mqtt, publish_valve_command
from arx_model      import ARXModel
from mpc_controller import MPCController
from cloud_uplink   import upload_telemetry

# ─── Init ─────────────────────────────────────────────────────────────────────
print("[MAIN] Smart Irrigation Gateway starting...")
init_db()

model = ARXModel()
mpc   = MPCController(model)

# ─── Per-zone State ───────────────────────────────────────────────────────────
zone_state = {
    1: {"y_history": [], "u_history": []},
    2: {"y_history": [], "u_history": []},
}

# ─── Data Callback (fires on every MQTT sensor message) ──────────────────────
def on_sensor_data(data: dict):
    zone = data.get("zone", 1)
    y    = (data.get("soil_moisture_1", 0) + data.get("soil_moisture_2", 0)) / 2.0

    state = zone_state[zone]
    state["y_history"].append(y)
    state["u_history"].append(0.0)

    # Keep history length manageable
    if len(state["y_history"]) > 20:
        state["y_history"].pop(0)
        state["u_history"].pop(0)

    print(f"[MAIN] Zone {zone} | Avg moisture: {y:.1f}%")

    # Run MPC only when we have enough history
    if len(state["y_history"]) >= 2:
        u_star = mpc.compute(state["y_history"], state["u_history"])

        if u_star > 10.0:   # only irrigate if recommendation > 10 sec
            publish_valve_command(mqtt_client, zone, 1, int(u_star))
            state["u_history"][-1] = u_star

    # Upload to ThingsBoard
    upload_telemetry(zone, data)

# ─── Start MQTT ───────────────────────────────────────────────────────────────
mqtt_client = start_mqtt(on_data_callback=on_sensor_data)

# ─── Keep Alive ───────────────────────────────────────────────────────────────
print("[MAIN] Gateway running. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[MAIN] Shutting down.")