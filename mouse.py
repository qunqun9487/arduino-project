import serial
import pyautogui
import time
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from threading import Thread
import subprocess

# 初始化串口连接
try:
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)  # 修改为你的串口号
    arduino.write(f"mouse working\n".encode('utf-8'))

except serial.SerialException as e:
    print(f"无法连接到 Arduino: {e}")
    arduino = None




# 鼠标移动灵敏度
sensitivity = 50

class MouseControlApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.running = True

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("鼠标控制")
        self.setGeometry(100, 100, 200, 100)

        # 创建返回按钮
        layout = QVBoxLayout()
        self.return_button = QPushButton("返回主菜单")
        self.return_button.clicked.connect(self.return_to_menu)
        layout.addWidget(self.return_button)

        self.setLayout(layout)
        #wait for arduino start
        time.sleep(3)
        arduino.write(f"mouse working\n".encode('utf-8'))

    def return_to_menu(self):
        # 停止鼠标控制线程
        self.running = False
        if arduino and arduino.is_open:
            arduino.close()
            print("串口已关闭")
        print("返回主菜单")

        # 启动主菜单程序
        try:
            subprocess.Popen(['python', 'main_menu.py'])
        except Exception as e:
            print(f"启动主菜单时出错: {e}")

        # 关闭当前窗口
        self.close()

def mouse_control(app):
    if not arduino or not arduino.is_open:
        print("无法读取 Arduino 数据，因为串口未打开")
        return

    print("开始读取 Arduino 数据并控制鼠标...")
    try:
        while app.running:
            # 从串口读取数据
            data = arduino.readline().decode().strip()
            if not data:
                continue  # 跳过空行

            # 打印接收到的数据（用于调试）
            print(f"收到的数据: '{data}'")

            try:
                # 确保数据格式为 "X轴,Y轴,按键"
                if ',' in data and len(data.split(",")) == 3:
                    x_val, y_val, button = map(int, data.split(","))

                    # 映射摇杆值到鼠标移动
                    x_move = (x_val - 512) / sensitivity
                    y_move = -(y_val - 512) / sensitivity

                    # 移动鼠标
                    pyautogui.moveRel(x_move, -y_move)  # Y轴方向反转

                    # 按键模拟（左键点击）
                    if button == 0:  # 按键按下
                        pyautogui.click()

            except ValueError:
                print(f"数据解析错误: {data}")  # 打印错误数据以调试

    except serial.SerialException as e:
        print(f"串口读取错误: {e}")
    except KeyboardInterrupt:
        print("程序已终止")
    finally:
        if arduino and arduino.is_open:
            arduino.close()
            print("串口已关闭")

if __name__ == "__main__":
    if arduino:
        # 创建 PyQt 应用
        app = QApplication(sys.argv)
        main_window = MouseControlApp()

        # 创建并启动鼠标控制线程
        thread = Thread(target=mouse_control, args=(main_window,))
        thread.start()

        # 显示主窗口
        main_window.show()
        sys.exit(app.exec_())
    else:
        print("无法启动程序，因为未连接到 Arduino。")
