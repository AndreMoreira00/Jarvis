// imu.h — IMU (MPU-6050/BNO055) por I2C: classifica gestos de CABECA localmente e
// emite UM evento (poucos bytes) -> app_core -> ble (Events 0x02). Banda ~zero.
// NUNCA envia accel/gyro cru continuo por BLE. STUB de bring-up. Folha.
#pragma once

void imu_init(void);  // bring-up: sinal de vida. Real: configura sensor + thresholds + callback.
