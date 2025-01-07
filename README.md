# arduino-project


### need to import
sys
time	
random	
subprocess	
threading	
pygame	
serial	
pyautogui	
PyQt5


arduino libary
need
LiquidCrystal_I2C

Hardware Requirements
Arduino board (e.g., Uno, Mega, Nano, etc.)
Joystick module
I2C LCD display
Jumper wires and a breadboard
Software Requirements
Arduino IDE
Required Libraries:
Wire (built-in)
LiquidCrystal_I2C
Circuit Diagram
Joystick Module Connections:
VRX -> A0 (X-axis)
VRY -> A1 (Y-axis)
SW -> D2 (button)
VCC -> 5V
GND -> GND
I2C LCD Connections:
VCC -> 5V
GND -> GND
SDA -> A4 (Uno) or D20 (Mega)
SCL -> A5 (Uno) or D21 (Mega)
