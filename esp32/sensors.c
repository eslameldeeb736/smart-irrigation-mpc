#include "sensors.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "dht.h"

static const char *TAG = "SENSORS";

// ─── ADC Handle ──────────────────────────────────────────────────────────────
static adc_oneshot_unit_handle_t adc1_handle;

// ─── Pulse Counters (set by ISRs) ────────────────────────────────────────────
static volatile uint32_t flow_pulse_count = 0;
static volatile uint32_t rain_tip_count   = 0;

// ─── ISR Handlers ────────────────────────────────────────────────────────────
static void IRAM_ATTR flow_isr_handler(void *arg)
{
    flow_pulse_count++;
}

static void IRAM_ATTR rain_isr_handler(void *arg)
{
    rain_tip_count++;
}

// ─── Init ─────────────────────────────────────────────────────────────────────
void sensors_init(void)
{
    // --- ADC init ---
    adc_oneshot_unit_init_cfg_t adc_cfg = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&adc_cfg, &adc1_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten    = ADC_ATTEN_DB_12,  // 0-3.3V range
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, SOIL_1_PIN, &chan_cfg));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, SOIL_2_PIN, &chan_cfg));

    // --- Flow sensor GPIO + ISR ---
    gpio_config_t flow_cfg = {
        .pin_bit_mask = (1ULL << FLOW_PIN),
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .intr_type    = GPIO_INTR_POSEDGE,
    };
    ESP_ERROR_CHECK(gpio_config(&flow_cfg));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(FLOW_PIN, flow_isr_handler, NULL));

    // --- Rain gauge GPIO + ISR ---
    gpio_config_t rain_cfg = {
        .pin_bit_mask = (1ULL << RAIN_PIN),
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,  // tipping bucket pulls low on tip
    };
    ESP_ERROR_CHECK(gpio_config(&rain_cfg));
    ESP_ERROR_CHECK(gpio_isr_handler_add(RAIN_PIN, rain_isr_handler, NULL));

    ESP_LOGI(TAG, "Sensors initialized");
}

// ─── Read All Sensors ─────────────────────────────────────────────────────────
void sensors_read(sensor_data_t *data)
{
    // --- Soil moisture ---
    int raw1 = 0, raw2 = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, SOIL_1_PIN, &raw1));
    ESP_ERROR_CHECK(adc_oneshot_read(adc1_handle, SOIL_2_PIN, &raw2));
    data->soil_moisture_1 = soil_adc_to_percent(raw1);
    data->soil_moisture_2 = soil_adc_to_percent(raw2);

    // --- DHT22 ---
    int16_t temp_raw = 0, hum_raw = 0;
    if (dht_read_data(DHT_TYPE_AM2301, DHT_PIN, &hum_raw, &temp_raw) == ESP_OK) {
        data->temperature = temp_raw / 10.0f;
        data->humidity    = hum_raw  / 10.0f;
    } else {
        ESP_LOGW(TAG, "DHT22 read failed");
        data->temperature = -1.0f;
        data->humidity    = -1.0f;
    }

    // --- Flow rate ---
    // Snapshot and reset counter atomically
    portDISABLE_INTERRUPTS();
    uint32_t pulses = flow_pulse_count;
    flow_pulse_count = 0;
    portENABLE_INTERRUPTS();
    // Convert pulses over 15-min window to L/min
    data->flow_rate = (pulses / FLOW_PULSES_PER_L) / 15.0f;

    // --- Rain gauge ---
    portDISABLE_INTERRUPTS();
    uint32_t tips = rain_tip_count;
    rain_tip_count = 0;
    portENABLE_INTERRUPTS();
    data->rain_mm = tips * RAIN_MM_PER_TIP;

    ESP_LOGI(TAG, "Soil: %.1f%% / %.1f%% | Temp: %.1fC | Hum: %.1f%% | Flow: %.2f L/min | Rain: %.2f mm",
             data->soil_moisture_1, data->soil_moisture_2,
             data->temperature, data->humidity,
             data->flow_rate, data->rain_mm);
}

// ─── ADC to Moisture % ───────────────────────────────────────────────────────
float soil_adc_to_percent(int raw)
{
    if (raw >= SOIL_DRY_VAL) return 0.0f;
    if (raw <= SOIL_WET_VAL) return 100.0f;
    return (float)(SOIL_DRY_VAL - raw) / (float)(SOIL_DRY_VAL - SOIL_WET_VAL) * 100.0f;
}