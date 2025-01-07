import sys
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QBrush, QPixmap
import time
import subprocess

class GameOverUI(QWidget):
    def __init__(self, game_name, score):
        super().__init__()
        self.game_name = game_name
        self.score = score
        self.current_index = 0  # 初始化当前选中的按钮索引
        self.prev_button_state = 1  # 上一次的按钮状态
        self.arduino_connected = False  # Arduino 是否已连接
        self.initUI()
        self.initArduino()

    def initUI(self):
        self.setWindowTitle("游戏结束")
        self.setGeometry(200, 50, 1000, 800)

        # 设置背景图片
        self.setAutoFillBackground(True)
        palette = QPalette()
        background = QPixmap("g_over.jpeg").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # 创建布局
        layout = QGridLayout()
        layout.setSpacing(40)  # 按钮之间的间距

        # 游戏结束标题
        title = QLabel(f"游戏结束：{self.game_name}")
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: white; 
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 2)  # 标题占据两列

        # 显示得分
        score_label = QLabel(f"得分：{self.score}")
        score_label.setStyleSheet("""
            font-size: 24px; 
            color: white; 
            background-color: rgba(0, 0, 0, 0.5);
            padding: 5px;
            border-radius: 5px;
        """)
        score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(score_label, 1, 0, 1, 2)  # 得分占据两列

        # 按钮
        self.buttons = []
        btn_labels = ["返回主菜单", "再来一次"]
        for index, label in enumerate(btn_labels):
            button = QPushButton(label)
            button.setStyleSheet("""
                font-size: 20px;
                color: black;
                background-color: white;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
            """)
            button.setFixedSize(250, 100)  # 按钮固定大小
            row = 2 + index  # 从第 2 行开始排列
            layout.addWidget(button, row, 0, 1, 2, Qt.AlignCenter)
            self.buttons.append(button)

        # 设置布局
        self.setLayout(layout)

        # 初始化按钮高亮
        self.updateButtonHighlight()
        
        
        

    def initArduino(self):
        """初始化 Arduino 串口连接和定时器"""
        try:
            self.arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)
            self.arduino_connected = True
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.readArduino)
            time.sleep(3)
            self.arduino.write(f"gameover\n".encode('utf-8'))
            self.timer.start(100)  # 每 100ms 读取一次 Arduino 数据
        except serial.SerialException as e:
            print(f"无法连接到 Arduino: {e}")
            self.arduino_connected = False

    def readArduino(self):
        """从 Arduino 读取数据并处理按钮选择"""
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

            # 根据 Y 值上下移动选中按钮
            if y_value < 400:  # 向上移动
                self.moveSelection(-1)
            elif y_value > 600:  # 向下移动
                self.moveSelection(1)

            # 按下按钮确认选择
            if button_state == 0 and self.prev_button_state == 1:  # 检测按钮按下
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
        if self.current_index == 0:  # 返回主菜单
            self.returnToMainMenu()
        elif self.current_index == 1:  # 再来一次
            self.restartGame()

    def restartGame(self):
        """根据游戏名称重新启动游戏"""
        if self.game_name == "Brick_Ball":
            subprocess.Popen(['python', 'brick_ball.py'])
        elif self.game_name == "Music_Game":
            subprocess.Popen(['python', 'music_game.py'])
        elif self.game_name == "Drive_Car":
            subprocess.Popen(['python', 'drive.py'])
        elif self.game_name == "Shoot_Hide":
            subprocess.Popen(['python', 'shoot_hide.py'])
        else:
            print(f"未知游戏名称: {self.game_name}")
        self.close()

    def returnToMainMenu(self):
        """返回主菜单"""
        subprocess.Popen(['python', 'main_menu.py'])
        self.close()
    def returnToBrickBall(self):
        """返回主菜单"""
        subprocess.Popen(['python', 'brick_ball.py'])
        self.close()

    def closeEvent(self, event):
        """释放资源"""
        if self.arduino_connected and self.arduino.is_open:
            self.arduino.close()
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_name = sys.argv[1]
    score = sys.argv[2]
    game_over_ui = GameOverUI(game_name, score)
    game_over_ui.show()
    sys.exit(app.exec_())




