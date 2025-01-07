from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap
import serial
import subprocess
import time

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
        self.setGeometry(300, 100, 1000, 800)  # 调整为更大的窗口

        # 使用 QPalette 设置背景图片
        self.setAutoFillBackground(True)
        palette = self.palette()
        background = QPixmap("bcg.jpg").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # 创建布局
        layout = QGridLayout()
        layout.setSpacing(100)  # 增大按钮之间的间距

        # 标题
        title = QLabel("请选择一个程序")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white; 
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2)  # 标题占据两列

        # 按钮
        self.buttons = []
        btn_names = ["Arduino mouse", "brickball.py", "drivecar", 
                    "shoot", "music_game", "退出"]
        self.actions = ['mouse.py', 'brick_ball.py', 'drive.py', 
                        'shoot_hide.py', 'music_game.py', None]

        btn_style = """
            QPushButton {
                font-size: 100px !important;;
                color: black;
                background-color: white;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
                background-clip: border-box;
            }
            QPushButton:hover {
                background-color: lightgray;
            }
        """

        for index, name in enumerate(btn_names):
            button = QPushButton(name)
            button.setStyleSheet(btn_style)
            button.setFixedSize(250, 150)  # 设置按钮为固定大小
            row = (index // 2) + 1  # 从第二行开始排列
            col = index % 2
            layout.addWidget(button, row, col)
            self.buttons.append(button)

        # 占位符调整按钮居中
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 6, 0, 1, 2)

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
            time.sleep(3)
            self.arduino.write(f"MainMenu\n".encode('utf-8'))
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
                self.moveSelection(-2)  # 上移两行
            elif y_value > 600:  # 向下移动
                self.moveSelection(2)  # 下移两行

            # 根据 X 轴值左右移动
            if x_value < 400:  # 向左移动
                self.moveSelection(-1)
            elif x_value > 600:  # 向右移动
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
                button.setStyleSheet("""
                    background-color: lightblue; 
                    color: white; 
                    font-weight: bold; 
                    border: 2px solid darkblue;
                """)
            else:
                button.setStyleSheet("""
                    background-color: white; 
                    color: black; 
                    border: 2px solid black;
                """)

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
            self.close()

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



