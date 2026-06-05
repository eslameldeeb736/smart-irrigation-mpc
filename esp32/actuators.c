#include "actuators.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ACTUATORS";

// ─── Init ─────────────────────────────────────────────────────────────────────
void actuators_init(void)
{
    gpio_config_t relay_cfg = {
        .pin_bit_mask = (1ULL << RELAY_1_PIN) | (1ULL << RELAY_2_PIN),
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&relay_cfg));

    // Start with both valves closed
    valve_close_all();

    ESP_LOGI(TAG, "Actuators initialized");
}

// ─── Open Valve for N Seconds ─────────────────────────────────────────────────
void valve_open(uint8_t valve_num, uint32_t duration_sec)
{
    gpio_num_t pin = (valve_num == 1) ? RELAY_1_PIN : RELAY_2_PIN;

    gpio_set_level(pin, RELAY_ON);
    ESP_LOGI(TAG, "Valve %d OPEN for %lu sec", valve_num, duration_sec);

    vTaskDelay(pdMS_TO_TICKS(duration_sec * 1000));

    gpio_set_level(pin, RELAY_OFF);
    ESP_LOGI(TAG, "Valve %d CLOSED", valve_num);
}

// ─── Close Single Valve ───────────────────────────────────────────────────────
void valve_close(uint8_t valve_num)
{
    gpio_num_t pin = (valve_num == 1) ? RELAY_1_PIN : RELAY_2_PIN;
    gpio_set_level(pin, RELAY_OFF);
    ESP_LOGI(TAG, "Valve %d CLOSED", valve_num);
}

// ─── Close All Valves ─────────────────────────────────────────────────────────
void valve_close_all(void)
{
    gpio_set_level(RELAY_1_PIN, RELAY_OFF);
    gpio_set_level(RELAY_2_PIN, RELAY_OFF);
    ESP_LOGI(TAG, "All valves CLOSED");
}