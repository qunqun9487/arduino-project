import pygame
import sys
import random
import serial
import time
import subprocess

# 初始化串口
try:
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)
    time.sleep(2)
    print("成功连接到 Arduino")
except serial.SerialException as e:
    print(f"无法连接到 Arduino: {e}")
    arduino = None

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸和标题
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("弹幕射击游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 182, 193)  # Light Pink


# 定义玩家参数
player_width = 50
player_height = 50
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 5

# 定义子弹参数
bullet_width = 5
bullet_height = 10
bullet_speed = -7
bullets = []

# 定义敌人参数
enemy_width = 50
enemy_height = 50
enemies = []
enemy_spawn_timer = 0
enemy_spawn_interval = 60  # 每 60 帧生成一个敌人

# 定义弹幕参数
enemy_bullets = []
enemy_bullet_width = 5
enemy_bullet_height = 10
enemy_bullet_speed = 5

# 初始化分数
score = 0
font = pygame.font.SysFont(None, 36)

# 游戏主循环
clock = pygame.time.Clock()
running = True

# Arduino 数据初始化
joystick_x = 512  # 默认摇杆在中间位置
button_state = 1  # 按钮未按下

def end_game():
    """结束游戏并跳转到游戏结束窗口"""
    if arduino and arduino.is_open:
        arduino.close()
        print("串口已关闭")
    pygame.quit()
    subprocess.Popen(['python', 'game_over_ui.py', 'Shoot_Hide', str(score)])
    sys.exit()

background_image = pygame.image.load("music_bg.jpeg").convert_alpha()  # 替换为背景图片路径
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# 设置透明度
background_alpha = 128  # 透明度值 (0-255)
background_image.set_alpha(background_alpha)

while running:
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # 从 Arduino 接收数据
    if arduino:
        try:
            data = arduino.readline().decode().strip()
            if data:
                parts = data.split(",")
                if len(parts) == 3:
                    joystick_x, _, button_state = map(int, parts)  # 只需要 X 和按钮状态
        except Exception as e:
            print(f"读取 Arduino 数据错误: {e}")

    # 玩家移动逻辑
    if joystick_x < 400 and player_x > 0:  # 左移
        player_x -= player_speed
    if joystick_x > 600 and player_x < screen_width - player_width:  # 右移
        player_x += player_speed

    # 玩家射击逻辑
    if button_state == 0:  # 检测按钮按下
        if len(bullets) < 5:  # 限制屏幕上的子弹数量
            bullets.append(pygame.Rect(player_x + player_width // 2, player_y, bullet_width, bullet_height))

    # 更新子弹位置
    for bullet in bullets[:]:
        bullet.y += bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)

    # 生成敌人
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_interval:
        enemy_spawn_timer = 0
        enemy_x = random.randint(0, screen_width - enemy_width)
        enemies.append(pygame.Rect(enemy_x, 0, enemy_width, enemy_height))

    # 更新敌人位置
    for enemy in enemies[:]:
        enemy.y += 2
        if enemy.y > screen_height:
            enemies.remove(enemy)
        else:
            # 敌人发射弹幕
            if random.randint(1, 1000) > 990:
                enemy_bullets.append(pygame.Rect(enemy.x + enemy_width // 2, enemy.y + enemy_height, enemy_bullet_width, enemy_bullet_height))

    # 更新敌人弹幕位置
    for enemy_bullet in enemy_bullets[:]:
        enemy_bullet.y += enemy_bullet_speed
        if enemy_bullet.y > screen_height:
            enemy_bullets.remove(enemy_bullet)

    # 检测子弹与敌人的碰撞
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                if arduino:
                    arduino.write(f"score: {score}\n".encode('utf-8'))
                break

    # 检测玩家与敌人弹幕的碰撞
    for enemy_bullet in enemy_bullets[:]:
        if pygame.Rect(player_x, player_y, player_width, player_height).colliderect(enemy_bullet):
            print("游戏结束！")
            running = False

    # 绘制屏幕内容
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))  # 绘制玩家

    for bullet in bullets:
        pygame.draw.rect(screen, GREEN, bullet)  # 绘制玩家子弹

    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)  # 绘制敌人

    for enemy_bullet in enemy_bullets:
        pygame.draw.rect(screen, PINK, enemy_bullet)  # 绘制敌人子弹

    # 显示分数
    score_text = font.render(f"分数: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)

# 游戏结束，跳转到游戏结束窗口
end_game()