# ESP32 Fan Controller

This project provides a web interface and API for controlling a fan using an ESP32. Monitor and adjust RPM settings in real-time.

## Tested Hardware
- **Fan:** be quiet! Pure Wings 2 | 140mm PWM High Speed Case Fan BL083
- **Microcontroller:** ESP32 DEVKIT v1

## Pin Configuration
- **GND** —> FAN Ground (Black)
- **VIN** —> Fan 12V (Yellow)
- **26** —> RPM (Green)
- **25** —> PWM (Blue)

![image](https://github.com/user-attachments/assets/ae7b7d66-23d1-4986-90a8-c4bea7650693)

### Note
Due to the ESP32's VIN only outputting 5V instead of the required 12V, the fan will not reach its full speed potential of 1600 RPM. Additionally, current configurations do not fully stop the fan. The minimum operating speed is approximately 90-120 RPM, even when set to the lowest RPM (1 RPM setting).

### Get Current RPM

```bash
curl -X GET http://<ESP32_IP_ADDRESS>/rpm
```

### Set Desired RPM

```bash
curl -X POST -d "1000" http://<ESP32_IP_ADDRESS>/rpm
```

Replace `<ESP32_IP_ADDRESS>` with the IP address assigned to your ESP32 on your network.
