idf_component_register(SRCS "app_core.c"
                       INCLUDE_DIRS "include"
                       REQUIRES nvs_flash ble jarvis_common
                                camera audio wake_word imu power wifi_stream)
