# Weatherproof Ultrasonic Sensor Real-Time Monitoring with Python
    
## Introduction

This project demonstrates how to interface a Weatherproof Ultrasonic Sensor (SKU SEN0208) with a Python application to display real-time distance measurements. The sensor is set to work in Mode 1 (UART automatic output) and is connected to a computer via a USB-Serial converter. The Python application uses Tkinter for the GUI and Matplotlib for plotting the real-time graph.

---
#### Features
- Real-time graph updates: The graph updates in real-time to reflect incoming sensor data.
- Serial device selection: Users can select the serial device and baud rate from a dropdown menu.
- Data logging: Sensor data can be logged to a CSV file with an option to enable or disable logging.
- Dynamic graph scaling: The graph scales automatically to fit the latest data points.
- Error handling: The application handles errors gracefully, including issues with serial communication.
- User-friendly interface: The application features a simple and intuitive interface, making it easy to use even for those without technical expertise.

---
## Setup

### Hardware

- Weatherproof Ultrasonic Sensor (SKU SEN0208)
- USB-Serial Converter
- Jumper Wires
- Soldering supplies

### Software

- Python 3.x
- Tkinter
- Matplotlib
- Scipy
- Pyserial

### Steps

1. Solder a jumper on the sensor board for Mode 1
2. Connect the sensor to the USB-Serial converter.
    #### Connecting the Sensor

    - Connect the sensor's `TX` pin to the `RX` pin on the USB-Serial converter.
    - Connect the sensor's `RX` pin to the `TX` pin on the USB-Serial converter.
    - Connect the `GND` to `GND`.
    - Connect the `VCC` to `5V` on the USB-Serial converter.

3. Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Python script:
    ```bash
    python main.py
    ```
4. Select the serial device and baud rate.

5. Click 'Start' to begin graphing. Click 'Stop' to stop graphing.

6. Enable the logging option to log data to a CSV file.

### Control Panel

- **Serial Device**: Select the COM port.
- **Baud Rate**: Set the baud rate (usually 9600).
- **Start/Stop**: Start or stop monitoring.
- **Clear**: Clear the graph.
- **Update Interval**: Set graph update frequency.
- **Logging**: Enable/Disable data logging.
- **Exit**: Close the app.

### Graph Area

Displays real-time distance data.

## Use Cases

- **Monitoring**: Start the app, select COM port and baud rate, and click "Start".
- **Logging**: Check "Enable Logging" to save data to a CSV file.
- **Clear Graph**: Click "Clear" to remove data points.
- **Change Interval**: Select a new update interval from the dropdown.
- **Exit**: Click "Exit" to close the app.

## Troubleshooting

- If the graph is empty, check the COM port and baud rate.
- If the graph isn't updating, try stopping and restarting monitoring.

## Contributing

Open issues or PRs for improvements.

## Reference

https://wiki.dfrobot.com/Weatherproof_Ultrasonic_Sensor_With_Separate_Probe_SKU_SEN0208

https://www.youtube.com/watch?v=h6321UBATps


## License

MIT License.