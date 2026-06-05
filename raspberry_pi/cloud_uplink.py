import requests
import json

# ─── ThingsBoard Config ───────────────────────────────────────────────────────
# Replace with your actual ThingsBoard instance and device token
THINGSBOARD_HOST  = "http://demo.thingsboard.io"
ACCESS_TOKEN_Z1   = "YOUR_ZONE1_DEVICE_TOKEN"
ACCESS_TOKEN_Z2   = "YOUR_ZONE2_DEVICE_TOKEN"

TELEMETRY_URL     = "{host}/api/v1/{token}/telemetry"

# ─── Upload Telemetry ─────────────────────────────────────────────────────────
def upload_telemetry(zone: int, data: dict) -> bool:
    token = ACCESS_TOKEN_Z1 if zone == 1 else ACCESS_TOKEN_Z2
    url   = TELEMETRY_URL.format(host=THINGSBOARD_HOST, token=token)

    payload = {
        "soil_moisture_1": data.get("soil_moisture_1"),
        "soil_moisture_2": data.get("soil_moisture_2"),
        "temperature":     data.get("temperature"),
        "humidity":        data.get("humidity"),
        "flow_rate":       data.get("flow_rate"),
        "rain_mm":         data.get("rain_mm"),
    }

    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=5
        )
        if response.status_code == 200:
            print(f"[CLOUD] Zone {zone} telemetry uploaded ✓")
            return True
        else:
            print(f"[CLOUD] Upload failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[CLOUD] Connection error: {e}")
        return False


# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_data = {
        "soil_moisture_1": 42.5,
        "soil_moisture_2": 38.1,
        "temperature":     28.3,
        "humidity":        61.2,
        "flow_rate":       2.4,
        "rain_mm":         0.0
    }
    print("[CLOUD] Testing ThingsBoard uplink...")
    print("[CLOUD] Note: Will fail until you set your device token.")
    upload_telemetry(1, test_data)