#ifndef ACTUATORS_H
#define ACTUATORS_H

#include <stdint.h>
#include "driver/gpio.h"

// ─── Pin Definitions ─────────────────────────────────────────────────────────
#define RELAY_1_PIN     26      // Valve 1
#define RELAY_2_PIN     27      // Valve 2

// ─── Relay Logic ─────────────────────────────────────────────────────────────
// Relay modules are typically active-LOW (0 = ON, 1 = OFF)
#define RELAY_ON        0
#define RELAY_OFF       1

// ─── Function Prototypes ─────────────────────────────────────────────────────
void actuators_init(void);
void valve_open(uint8_t valve_num, uint32_t duration_sec);
void valve_close(uint8_t valve_num);
void valve_close_all(void);

#endif // ACTUATORS_H