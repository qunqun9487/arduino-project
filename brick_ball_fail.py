import pygame
import sys
import random
import serial
import time
import subprocess

# 初始化串口
try:
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)  # 修改为你的串口号
    time.sleep(2)
except serial.SerialException as e:
    print(f"无法连接到 Arduino: {e}")
    arduino = None

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸和标题
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("打砖块游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)  # 分裂道具颜色

# 定义玩家板子参数
paddle_width = 100
paddle_height = 10
paddle_x = screen_width // 2 - paddle_width // 2
paddle_y = screen_height - 20
paddle_speed = 14

# 定义球参数
ball_size = 10
balls = [{'x': screen_width // 2, 'y': screen_height // 2, 'speed_x': 8, 'speed_y': -8}]

# 定义砖块参数
brick_rows = 5
brick_columns = 10
brick_width = 70
brick_height = 20
brick_padding = 10
brick_offset_top = 50
brick_offset_left = 35

# 定义分裂道具参数
powerups = []  # 存储当前掉落的分裂道具
powerup_size = 20
powerup_speed = 5
powerup_chance = 0.3  # 分裂道具掉落的概率（30%）

# 创建砖块
bricks = []
for row in range(brick_rows):
    for col in range(brick_columns):
        brick_x = brick_offset_left + col * (brick_width + brick_padding)
        brick_y = brick_offset_top + row * (brick_height + brick_padding)
        bricks.append(pygame.Rect(brick_x, brick_y, brick_width, brick_height))

# 初始化分数
score = 0
font = pygame.font.SysFont(None, 36)

# 游戏主循环
clock = pygame.time.Clock()
running = True


def end_game():
    """结束游戏并跳转到游戏结束窗口"""
    if arduino and arduino.is_open:
            arduino.close()
            print("串口已关闭")
            print("返回主菜单")
    pygame.quit()
    subprocess.Popen(['python', 'game_over_ui.py', 'Brick_Ball', str(score)])
    sys.exit()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 从 Arduino 接收数据
    try:
        data = arduino.readline().decode().strip()
        if data and ',' in data:
            parts = data.split(",")
            if len(parts) == 3:  # 确保数据格式正确
                x_val, y_val, button = map(int, parts)

                # 根据 X 值控制板子移动
                if x_val < 400:  # 偏左
                    paddle_x -= paddle_speed
                elif x_val > 600:  # 偏右
                    paddle_x += paddle_speed

    except Exception as e:
        print(f"读取数据错误: {e}")
        pass

    # 限制板子移动范围
    paddle_x = max(0, min(screen_width - paddle_width, paddle_x))

    # 更新所有小球的位置
    for ball in balls[:]:  # 遍历当前所有小球
        ball['x'] += ball['speed_x']
        ball['y'] += ball['speed_y']

        # 球碰到墙壁反弹
        if ball['x'] <= 0 or ball['x'] >= screen_width - ball_size:
            ball['speed_x'] = -ball['speed_x']
        if ball['y'] <= 0:
            ball['speed_y'] = -ball['speed_y']

        # 球碰到板子反弹
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        if paddle_rect.colliderect(pygame.Rect(ball['x'], ball['y'], ball_size, ball_size)):
            ball['speed_y'] = -ball['speed_y']

        # 球碰到砖块
        for brick in bricks[:]:
            if brick.colliderect(pygame.Rect(ball['x'], ball['y'], ball_size, ball_size)):
                bricks.remove(brick)
                ball['speed_y'] = -ball['speed_y']
                score += 1
                arduino.write(f"score: {score}\n".encode('utf-8'))
                # 掉落分裂道具的概率
                if random.random() < powerup_chance:
                    powerups.append({'x': brick.x + brick_width // 2 - powerup_size // 2,
                                    'y': brick.y + brick_height // 2,
                                    'speed_y': powerup_speed})

        # 检查球是否掉出屏幕
        if ball['y'] > screen_height:
            balls.remove(ball)
            if len(balls) == 0:  # 如果所有球都掉出屏幕
                print("游戏结束！")
                running = False

    # 更新分裂道具的位置
    for powerup in powerups[:]:
        powerup['y'] += powerup['speed_y']

        # 检查是否被玩家接住
        if paddle_rect.colliderect(pygame.Rect(powerup['x'], powerup['y'], powerup_size, powerup_size)):
            powerups.remove(powerup)
            # 分裂出两个新球
            for ball in balls[:]:
                balls.append({'x': ball['x'], 'y': ball['y'], 'speed_x': -ball['speed_x'], 'speed_y': ball['speed_y']})
                balls.append({'x': ball['x'], 'y': ball['y'], 'speed_x': ball['speed_x'], 'speed_y': -ball['speed_y']})

        # 如果道具掉到屏幕下方，移除它
        elif powerup['y'] > screen_height:
            powerups.remove(powerup)

    # 如果所有砖块被清除，结束游戏
    if not bricks:
        print("游戏胜利！")
        running = False

    # 绘制屏幕内容
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, paddle_rect)  # 绘制板子
    for ball in balls:
        pygame.draw.ellipse(screen, RED, (ball['x'], ball['y'], ball_size, ball_size))  # 绘制所有小球

    # 绘制砖块
    for brick in bricks:
        pygame.draw.rect(screen, BLACK, brick)

    # 绘制分裂道具
    for powerup in powerups:
        pygame.draw.rect(screen, YELLOW, (powerup['x'], powerup['y'], powerup_size, powerup_size))

    # 显示分数
    score_text = font.render(f"score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)

# 游戏结束，跳转到游戏结束窗口
end_game()