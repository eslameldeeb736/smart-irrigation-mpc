# Smart Irrigation System with Model Predictive Control (MPC)

An automated irrigation system that optimizes crop water usage using real-time sensor data and a Model Predictive Control (MPC) algorithm.

## Overview
Traditional irrigation wastes water by operating on fixed schedules. This system uses sensor feedback and predictive control to irrigate only when needed and in the right amount.

## Hardware
- ESP32 — sensor interfacing and data acquisition
- Raspberry Pi — main controller running Embedded Linux
- Soil moisture sensor
- Temperature/humidity sensor (DHT)

## Software & Algorithms
- Embedded C for ESP32 peripheral drivers
- Python on Raspberry Pi for MPC implementation
- ARX (AutoRegressive with eXogenous input) model for system identification
- Model Predictive Control (MPC) for optimal irrigation scheduling

## System Architecture
1. ESP32 reads soil moisture and environmental sensors
2. Data is sent to Raspberry Pi via UART/Wi-Fi
3. Raspberry Pi runs the ARX+MPC algorithm
4. Control signal is sent back to activate the irrigation pump

## Repository Structure

/esp32          → ESP32 firmware (C)
/raspberry_pi   → MPC controller (Python)
/docs           → Wiring diagrams and documentation

## Built With
- ESP32 (Espressif)
- Raspberry Pi 4
- Embedded Linux
- C / Python
