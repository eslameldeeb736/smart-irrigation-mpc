idf_component_register(SRCS "app_mqtt.c" "actuators.c" "sensors.c" "zone1.c"
                    INCLUDE_DIRS "."
                    REQUIRES esp_driver_gpio esp_adc dht mqtt esp_wifi nvs_flash esp_event esp_netif)