#ifndef APP_MQTT_H
#define APP_MQTT_H

#include "sensors.h"

// ─── WiFi & MQTT Config ───────────────────────────────────────────────────────
#define WIFI_SSID        "YOUR_WIFI_SSID"
#define WIFI_PASS        "YOUR_WIFI_PASSWORD"
#define MQTT_BROKER_URI  "mqtt://192.168.1.100"   // Raspberry Pi IP

// ─── MQTT Topics ─────────────────────────────────────────────────────────────
#define TOPIC_SENSORS    "irrigation/zone1/sensors"
#define TOPIC_VALVE      "irrigation/zone1/valve"

// ─── Function Prototypes ─────────────────────────────────────────────────────
void mqtt_app_init(void);
void mqtt_publish_sensors(const sensor_data_t *data);

#endif // APP_MQTT_H