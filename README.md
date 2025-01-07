# arduino-project


need to import

sys

time	

random	

subprocess	

threading	

pygame	

serial	

pyautogui	

PyQt5


## Features
- **Joystick Input**: Reads real-time X and Y axis values and button states.
- **Serial Communication**: Sends joystick data via serial.
- **LCD Display**: Displays messages received from the serial input.

## Hardware Requirements
1. Arduino board (e.g., Uno, Mega, Nano, etc.)
2. Joystick module
3. I2C LCD display
4. Jumper wires and a breadboard

## Software Requirements
1. **Arduino IDE**
2. Required Libraries:
   - `Wire` (built-in)
   - `LiquidCrystal_I2C`

## Circuit Diagram
1. **Joystick Module Connections**:
   - `VRX` -> `A0` (X-axis)
   - `VRY` -> `A1` (Y-axis)
   - `SW`  -> `D2` (button)
   - `VCC` -> `5V`
   - `GND` -> `GND`
2. **I2C LCD Connections**:
   - `VCC` -> `5V`
   - `GND` -> `GND`
   - `SDA` -> `A4` (Uno) or `D20` (Mega)
   - `SCL` -> `A5` (Uno) or `D21` (Mega)
