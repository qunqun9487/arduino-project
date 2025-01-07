from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
import serial
import subprocess

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.current_index = 0  # 初始化当前选中的按钮索引
        self.prev_button_state = 1  # 上一次的按钮状态
        self.arduino_connected = False  # Arduino 是否已连接
        self.initUI()
        self.initArduino()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle("主菜单")
        self.setGeometry(300, 300, 400, 300)

        # 设置背景图片
        self.setStyleSheet("background-image: url('bcg.jpg'); background-repeat: no-repeat; background-position: center;")

        # 垂直布局
        layout = QVBoxLayout()

        # 标题
        title = QLabel("请选择一个程序")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background-color: rgba(0, 0, 0, 0.5);")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 按钮
        self.buttons = []
        btn_names = ["Arduino 鼠标控制", "打砖块游戏", "接物小游戏", "退出"]
        self.actions = ['mousetest.py', 'brick_breaker.py', 'catch_game.py', None]

        btn_style = """
            QPushButton {
                font-size: 16px;
                color: black;
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: lightgray;
            }
        """

        for name in btn_names:
            button = QPushButton(name)
            button.setStyleSheet(btn_style)
            layout.addWidget(button)
            self.buttons.append(button)

        # 设置布局
        self.setLayout(layout)

        # 初始化选中的按钮
        self.updateButtonHighlight()

    def initArduino(self):
        """初始化 Arduino 串口连接和定时器"""
        try:
            self.arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)  # 修改为你的串口号
            self.arduino_connected = True
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.readArduino)
            self.timer.start(100)  # 每 100ms 读取一次 Arduino 数据
        except serial.SerialException as e:
            print(f"无法连接到 Arduino: {e}")
            self.arduino_connected = False

    def readArduino(self):
        """读取 Arduino 数据并根据方向操作按钮"""
        if not self.arduino_connected:
            return

        try:
            data = self.arduino.readline().decode().strip()
            if not data:
                return

            # 解析 Arduino 数据
            try:
                x_str, y_str, button_str = data.split(",")
                x_value = int(x_str)
                y_value = int(y_str)
                button_state = int(button_str)
            except ValueError:
                print(f"数据解析错误: {data}")
                return

            # 根据 Y 轴值移动选中按钮
            if y_value < 400:  # 向上移动
                self.moveSelection(-1)
            elif y_value > 600:  # 向下移动
                self.moveSelection(1)

            # 按钮按下触发确认选择
            if button_state == 0 and self.prev_button_state == 1:  # 检测按下事件
                self.handleSelection()

            # 更新按钮状态
            self.prev_button_state = button_state

        except Exception as e:
            print(f"读取 Arduino 数据出错: {e}")

    def moveSelection(self, direction):
        """移动按钮选中状态"""
        self.current_index = (self.current_index + direction) % len(self.buttons)
        self.updateButtonHighlight()

    def updateButtonHighlight(self):
        """更新按钮的高亮显示"""
        for i, button in enumerate(self.buttons):
            if i == self.current_index:
                button.setStyleSheet("background-color: lightblue; color: white; font-weight: bold;")
            else:
                button.setStyleSheet("background-color: white; color: black;")

    def handleSelection(self):
        """处理确认选择的操作"""
        if self.current_index < len(self.actions) and self.actions[self.current_index]:
            self.run_program(self.actions[self.current_index])
        elif self.current_index == len(self.actions) - 1:  # 退出
            self.close()

    def run_program(self, file_name):
        """运行子程序"""
        if self.arduino_connected and self.arduino.is_open:
            self.arduino.close()
            self.arduino_connected = False
            print("主程序关闭 Arduino 连接以启动子程序")

        try:
            subprocess.Popen(['python', file_name])
        except Exception as e:
            print(f"运行 {file_name} 时出错: {e}")

    def closeEvent(self, event):
        """清理资源"""
        if self.arduino_connected and self.arduino.is_open:
            self.arduino.close()
            print("主程序释放 Arduino 连接")
        self.timer.stop()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication([])
    menu = MainMenu()
    menu.show()
    app.exec_()



