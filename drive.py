import pygame
import sys
import random
import serial
import time
import subprocess

# 初始化 Arduino 串口
try:
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)
    time.sleep(2)
    print("成功连接到 Arduino")
except serial.SerialException as e:
    print(f"无法连接到 Arduino: {e}")
    arduino = None

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
screen_width = 400
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("赛车游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)

# 定义玩家车辆参数
car_width = 50
car_height = 100
car_x = screen_width // 2 - car_width // 2
car_y = screen_height - car_height - 20
car_speed = 10

# 定义障碍物参数
obstacle_width = 50
obstacle_height = 100
obstacles = []
obstacle_speed = 7
obstacle_spawn_interval = 30  # 每隔 30 帧生成一个障碍物
obstacle_timer = 0

# 初始化分数
score = 0
font = pygame.font.SysFont(None, 36)

# 加载玩家车辆图像
car_image = pygame.Surface((car_width, car_height))
car_image.fill(BLUE)  # 用蓝色填充表示玩家车辆

# 加载障碍物图像
obstacle_image = pygame.Surface((obstacle_width, obstacle_height))
obstacle_image.fill(RED)  # 用红色填充表示障碍物

# 游戏主循环
clock = pygame.time.Clock()
running = True

# Arduino 数据初始化
joystick_x = 512  # 摇杆中间值
button_state = 1  # 按钮初始状态

def end_game():
    """结束游戏并跳转到游戏结束窗口"""
    if arduino and arduino.is_open:
        try:
            arduino.write("gameover\n".encode('utf-8'))
            print("发送到 Arduino: gameover")
        except Exception as e:
            print(f"发送 gameover 到 Arduino 出错: {e}")
        arduino.close()
        print("关闭 Arduino 串口")
    pygame.quit()
    subprocess.Popen(['python', 'game_over_ui.py', 'Drive_Car', str(score)])
    sys.exit()

while running:
    screen.fill(GRAY)  # 填充赛道背景颜色

    # 绘制赛道线
    pygame.draw.line(screen, WHITE, (screen_width // 2, 0), (screen_width // 2, screen_height), 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 从 Arduino 接收数据
    if arduino:
        try:
            data = arduino.readline().decode().strip()
            if data:
                parts = data.split(",")
                if len(parts) == 3:  # 确保数据格式正确
                    joystick_x, _, button_state = map(int, parts)  # 读取 X 值和按钮状态
        except Exception as e:
            print(f"读取 Arduino 数据错误: {e}")

    # 玩家车辆移动逻辑
    if joystick_x < 400 and car_x > 0:  # 左移
        car_x -= car_speed
    if joystick_x > 600 and car_x < screen_width - car_width:  # 右移
        car_x += car_speed

    # 玩家加速逻辑（按钮按下时增加障碍物速度）
    if button_state == 0:
        obstacle_speed = 10
    else:
        obstacle_speed = 7

    # 生成障碍物
    obstacle_timer += 1
    if obstacle_timer >= obstacle_spawn_interval:
        obstacle_timer = 0
        obstacle_x = random.randint(0, screen_width - obstacle_width)
        obstacles.append(pygame.Rect(obstacle_x, 0, obstacle_width, obstacle_height))

    # 更新障碍物位置
    for obstacle in obstacles[:]:
        obstacle.y += obstacle_speed
        if obstacle.y > screen_height:
            obstacles.remove(obstacle)
            score += 1  # 每避开一个障碍物得分
            # 回传分数到 Arduino
            if arduino:
                try:
                    arduino.write(f"score: {score}\n".encode('utf-8'))
                    print(f"发送到 Arduino: score: {score}")
                except Exception as e:
                    print(f"发送分数到 Arduino 出错: {e}")

    # 检测碰撞
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    for obstacle in obstacles:
        if car_rect.colliderect(obstacle):
            print("游戏结束！")
            running = False

    # 绘制玩家车辆
    screen.blit(car_image, (car_x, car_y))

    # 绘制障碍物
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle.x, obstacle.y))

    # 显示分数
    score_text = font.render(f"score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)

# 清理资源
end_game()
