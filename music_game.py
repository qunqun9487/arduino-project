import pygame
import random
import sys
import subprocess
import serial
import time

# 初始化 Arduino 串口
try:
    arduino = serial.Serial(port='COM3', baudrate=115200, timeout=0.1)
    time.sleep(2)
    print("成功连接到 Arduino")
except Exception as e:
    print(f"连接 Arduino 失败: {e}")
    arduino = None

# 初始化 Pygame
pygame.init()

# 设置屏幕
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("音游")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 定义音符参数
note_width = 50
note_height = 50
note_speed = 10
notes = []

# 定义方向和颜色
directions = {
    "left": {"color": GREEN, "position": screen_width // 2 - 150},
    "up": {"color": BLUE, "position": screen_width // 2 - 50},
    "down": {"color": RED, "position": screen_width // 2 + 50},
    "right": {"color": YELLOW, "position": screen_width // 2 + 150},
}

# 定义接收区域
receptors = {
    "left": pygame.Rect(directions["left"]["position"], screen_height - 100, note_width, note_height),
    "up": pygame.Rect(directions["up"]["position"], screen_height - 100, note_width, note_height),
    "down": pygame.Rect(directions["down"]["position"], screen_height - 100, note_width, note_height),
    "right": pygame.Rect(directions["right"]["position"], screen_height - 100, note_width, note_height),
}

# 初始化分数和连击
score = 0
combo = 0
font = pygame.font.SysFont(None, 36)

# 初始化计时器
note_timer = 0
note_spawn_interval = 20  # 每隔 30 帧生成一个音符

# 加载背景音乐和按键音效
pygame.mixer.music.load("yingyou2.mp3")  # 替换为背景音乐路径
pygame.mixer.music.set_volume(0.1)  # 设置背景音乐音量
pygame.mixer.music.play()  # 播放一次，不循环

key_hit_sound = pygame.mixer.Sound("click3.wav")  # 替换为按键音效路径
key_hit_sound.set_volume(1.0)  # 设置按键音效音量

# 注册音乐结束事件
MUSIC_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_END)

# 定义按钮
button_width = 100
button_height = 40
terminate_button = pygame.Rect(screen_width - 120, 20, button_width, button_height)

# 初始化摇杆状态
joystick_keys = {"left": False, "up": False, "down": False, "right": False}

# 游戏主循环
clock = pygame.time.Clock()
running = True

background_image = pygame.image.load("music_bg.jpeg").convert_alpha()  # 替换为背景图片路径
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# 设置透明度
background_alpha = 128  # 透明度值 (0-255)
background_image.set_alpha(background_alpha)

while running:
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # 从 Arduino 读取数据
    if arduino:
        try:
            data = arduino.readline().decode().strip()  # 读取一行数据
            if data:
                parts = data.split(",")
                if len(parts) == 3:  # 确保数据格式正确
                    x_val, y_val, button = map(int, parts)

                    # 根据 X 和 Y 值判断按键状态
                    joystick_keys["left"] = x_val < 300
                    joystick_keys["right"] = x_val > 700
                    joystick_keys["up"] = y_val < 300
                    joystick_keys["down"] = y_val > 700
        except Exception as e:
            print(f"串口读取错误: {e}")

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MUSIC_END:  # 背景音乐结束
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if terminate_button.collidepoint(event.pos):  # 点击终止按钮
                running = False

    # 获取按键输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:  # 按下 ESC 键终止游戏
        running = False

    # 显示提示信息
    tips = [
        "green = left (←)",
        "blue = up (↑)",
        "red = down (↓)",
        "yellow = right (→)",
        "esc to quit"
    ]
    for i, tip in enumerate(tips):
        tip_text = font.render(tip, True, WHITE)
        screen.blit(tip_text, (10, 10 + i * 30))

    # 绘制终止按钮

    # 生成音符
    note_timer += 1
    if note_timer >= note_spawn_interval:
        note_timer = 0
        direction = random.choice(list(directions.keys()))
        notes.append({
            "rect": pygame.Rect(directions[direction]["position"], 0, note_width, note_height),
            "direction": direction,
            "color": directions[direction]["color"]
        })

    # 更新音符位置
    for note in notes[:]:
        note["rect"].y += note_speed
        if note["rect"].y > screen_height:
            notes.remove(note)
            combo = 0  # 连击中断

    # 检测按键与音符的碰撞
    for note in notes[:]:
        if note["rect"].colliderect(receptors[note["direction"]]):
            if (keys[pygame.K_LEFT] or joystick_keys["left"]) and note["direction"] == "left":
                notes.remove(note)
                score += 10 + combo
                arduino.write(f"score: {score}\n".encode('utf-8'))
                combo += 1
                key_hit_sound.play()
            elif (keys[pygame.K_UP] or joystick_keys["up"]) and note["direction"] == "up":
                notes.remove(note)
                score += 10 + combo
                arduino.write(f"score: {score}\n".encode('utf-8'))
                combo += 1
                key_hit_sound.play()
            elif (keys[pygame.K_DOWN] or joystick_keys["down"]) and note["direction"] == "down":
                notes.remove(note)
                score += 10 + combo
                arduino.write(f"score: {score}\n".encode('utf-8'))
                combo += 1
                key_hit_sound.play()
            elif (keys[pygame.K_RIGHT] or joystick_keys["right"]) and note["direction"] == "right":
                notes.remove(note)
                score += 10 + combo
                arduino.write(f"score: {score}\n".encode('utf-8'))
                combo += 1
                key_hit_sound.play()

    # 绘制接收区域
    for direction, rect in receptors.items():
        pygame.draw.rect(screen, directions[direction]["color"], rect)

    # 绘制音符
    for note in notes:
        pygame.draw.rect(screen, note["color"], note["rect"])

    # 显示分数和连击
    score_text = font.render(f"Score: {score}", True, WHITE)
    combo_text = font.render(f"Combo: {combo}", True, WHITE)
    screen.blit(score_text, (screen_width - 150, 10))
    screen.blit(combo_text, (screen_width - 150, 50))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(60)

# 停止音乐
pygame.mixer.music.stop()
def end_game():
    """结束游戏并跳转到游戏结束窗口"""
    if arduino and arduino.is_open:
        arduino.close()
        print("串口已关闭")
        print("返回主菜单")
# 游戏结束后启动 Game Over UI
    pygame.quit()
    subprocess.Popen(['python', 'game_over_ui.py', 'Music_Game', str(score)])
    sys.exit()
    sys.exit()
end_game()