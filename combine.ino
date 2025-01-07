#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// I2C LCD 初始化
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 定义摇杆引脚
const int VRX_PIN = A0; // X轴
const int VRY_PIN = A1; // Y轴
const int SW_PIN = 2;   // 按键

// 保存上一次状态
int prevX = 512, prevY = 512, prevButton = 1;
String receivedMessage = ""; // 用于存储串口接收到的消息

void setup() {
  // 初始化串口
  Serial.begin(115200);

  // 初始化摇杆引脚
  pinMode(SW_PIN, INPUT_PULLUP);

  // 初始化 I2C LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Waiting for data...");
}

void loop() {
  int xValue = analogRead(VRX_PIN);
  int yValue = analogRead(VRY_PIN);
  int buttonState = digitalRead(SW_PIN);

  // 只有当数据变化时才发送
  if (abs(xValue - prevX) > 20 || abs(yValue - prevY) > 20 || buttonState != prevButton) {
    Serial.print(xValue);
    Serial.print(",");
    Serial.print(yValue);
    Serial.print(",");
    Serial.println(buttonState);

    prevButton = buttonState;
  }

  delay(100);
  handleSerialInput();
}


void handleSerialInput() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { // 如果接收到换行符，认为消息接收完成
      updateDisplay(receivedMessage); // 更新 I2C LCD 显示
      receivedMessage = ""; // 清空消息缓存
    } else {
      receivedMessage += c; // 拼接消息
    }
  }
}

void updateDisplay(const String &message) {
  lcd.clear(); // 清空 LCD
  lcd.setCursor(0, 0); // 设置光标到第一行
  lcd.print(message); // 显示消息
}






