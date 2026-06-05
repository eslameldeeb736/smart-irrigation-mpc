#ifndef SENSORS_H
#define SENSORS_H

#include <stdint.h>

// ─── Pin Definitions ─────────────────────────────────────────────────────────
#define SOIL_1_PIN          ADC_CHANNEL_6    // GPIO34
#define SOIL_2_PIN          ADC_CHANNEL_7    // GPIO35
#define DHT_PIN             4
#define FLOW_PIN            18
#define RAIN_PIN            19

// ─── Calibration ─────────────────────────────────────────────────────────────
#define SOIL_DRY_VAL        2800    // ADC reading in dry air
#define SOIL_WET_VAL        1200    // ADC reading in water
#define FLOW_PULSES_PER_L   450.0f  // YF-S201: 450 pulses per litre
#define RAIN_MM_PER_TIP     0.2794f // tipping bucket: 0.2794mm per tip

// ─── Data Structure ──────────────────────────────────────────────────────────
typedef struct {
    float soil_moisture_1;  // % (0-100)
    float soil_moisture_2;  // % (0-100)
    float temperature;      // °C
    float humidity;         // % RH
    float flow_rate;        // L/min
    float rain_mm;          // mm since last reading
} sensor_data_t;

// ─── Function Prototypes ─────────────────────────────────────────────────────
void     sensors_init(void);
void     sensors_read(sensor_data_t *data);
float    soil_adc_to_percent(int raw);

#endif // SENSORS_H