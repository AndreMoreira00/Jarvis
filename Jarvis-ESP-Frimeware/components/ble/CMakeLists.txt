idf_component_register(SRCS "jarvis_ble.c" "gatt_svc.c"
                       INCLUDE_DIRS "include"
                       PRIV_INCLUDE_DIRS "."
                       REQUIRES bt nvs_flash jarvis_common)
