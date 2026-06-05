import time
import json
import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883)
client.loop_start()
time.sleep(1)

payload = json.dumps({
    "zone": 1,
    "soil_moisture_1": 32.0,
    "soil_moisture_2": 30.0,
    "temperature": 29.5,
    "humidity": 60.0,
    "flow_rate": 0.0,
    "rain_mm": 0.0
})

client.publish("irrigation/zone1/sensors", payload)
print("[TEST] Published sensor payload.")
time.sleep(2)
client.loop_stop()
