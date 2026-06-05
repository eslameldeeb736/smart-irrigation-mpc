#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "sensors.h"
#include "actuators.h"
#include "app_mqtt.h"

static const char *TAG = "MAIN";

// ─── Sensor Task ──────────────────────────────────────────────────────────────
static void sensor_task(void *pvParameters)
{
    sensor_data_t data;

    while (1) {
        sensors_read(&data);
        mqtt_publish_sensors(&data);
        ESP_LOGI(TAG, "Cycle complete. Sleeping 15 min...");
        vTaskDelay(pdMS_TO_TICKS(15 * 60 * 1000));
    }
}

// ─── App Entry Point ──────────────────────────────────────────────────────────
void app_main(void)
{
    ESP_LOGI(TAG, "Smart Irrigation Zone 1 starting...");

    sensors_init();
    actuators_init();
    mqtt_app_init();

    xTaskCreate(sensor_task, "sensor_task", 4096, NULL, 5, NULL);

    ESP_LOGI(TAG, "All tasks running.");
}