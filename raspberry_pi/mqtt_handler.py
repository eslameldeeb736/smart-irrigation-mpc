import paho.mqtt.client as mqtt
import json
import threading
from database import insert_reading, insert_valve_command

# ─── Config ───────────────────────────────────────────────────────────────────
BROKER_HOST   = "localhost"
BROKER_PORT   = 1883
TOPIC_ZONE1   = "irrigation/zone1/sensors"
TOPIC_ZONE2   = "irrigation/zone2/sensors"
TOPIC_VALVE1  = "irrigation/zone1/valve"
TOPIC_VALVE2  = "irrigation/zone2/valve"

# ─── Callback: on connect ─────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[MQTT] Connected to broker.")
        client.subscribe(TOPIC_ZONE1)
        client.subscribe(TOPIC_ZONE2)
        print(f"[MQTT] Subscribed to {TOPIC_ZONE1} and {TOPIC_ZONE2}")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

# ─── Callback: on message ─────────────────────────────────────────────────────
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[MQTT] Received on {msg.topic}: {payload}")
        insert_reading(payload)

        # Trigger MPC controller if callback is set
        if userdata and "on_data" in userdata:
            userdata["on_data"](payload)

    except json.JSONDecodeError:
        print(f"[MQTT] Invalid JSON on {msg.topic}")

# ─── Publish Valve Command ────────────────────────────────────────────────────
def publish_valve_command(client, zone: int, valve_num: int, duration_sec: int):
    topic = TOPIC_VALVE1 if zone == 1 else TOPIC_VALVE2
    payload = json.dumps({
        "valve": valve_num,
        "duration": duration_sec
    })
    client.publish(topic, payload, qos=1)
    insert_valve_command(zone, valve_num, duration_sec, "MPC")
    print(f"[MQTT] Published valve command → {topic}: {payload}")

# ─── Start MQTT Client ────────────────────────────────────────────────────────
def start_mqtt(on_data_callback=None):
    userdata = {"on_data": on_data_callback} if on_data_callback else {}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    print("[MQTT] Client running in background thread.")
    return client

# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import time
    client = start_mqtt()
    time.sleep(2)

    # Simulate publishing a sensor reading
    test_payload = json.dumps({
        "zone": 1,
        "soil_moisture_1": 35.0,
        "soil_moisture_2": 31.0,
        "temperature": 29.1,
        "humidity": 58.0,
        "flow_rate": 0.0,
        "rain_mm": 0.0
    })
    client.publish(TOPIC_ZONE1, test_payload)
    print("[TEST] Published test sensor payload.")
    time.sleep(2)
    print("[TEST] Done.")