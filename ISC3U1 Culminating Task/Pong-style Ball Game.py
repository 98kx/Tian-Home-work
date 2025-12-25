# 导入所需库
import pygame
import random
import math

# 初始化Pygame库
pygame.init()

# 游戏常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
SCREEN_TITLE = "Pong-Style Ball Game"
FPS = 60
PADDLE_SPEED = 10
BALL_SPEED = 5

PADDLE_WIDTH, PADDLE_HEIGHT = 156, 18
BALL_RADIUS = 15

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 255, 100)
YELLOW = (255, 255, 0)

# 全局变量
screen = None
clock = None
running = True
top_paddle = None
bottom_paddle = None
ball = None
top_score = 0
bottom_score = 0
font = None
small_font = None
center_line_points = []

def init_game():
    """初始化游戏"""
    global screen, clock, top_paddle, bottom_paddle, ball, font, small_font, center_line_points
    
    # 创建游戏窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)
    
    # 初始化游戏时钟
    clock = pygame.time.Clock()
    
    # 创建paddle
    top_paddle = {
        'rect': pygame.Rect(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, 20, PADDLE_WIDTH, PADDLE_HEIGHT),
        'color': RED,
        'is_top': True,
        'speed': PADDLE_SPEED
    }
    
    bottom_paddle = {
        'rect': pygame.Rect(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT),
        'color': BLUE,
        'is_top': False,
        'speed': PADDLE_SPEED
    }
    
    # 创建球
    init_ball()
    
    # 初始化字体
    font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)
    
    # 创建中心虚线
    center_line_points = []
    for y in range(0, SCREEN_HEIGHT, 20):
        center_line_points.append((SCREEN_WIDTH / 2, y))
        center_line_points.append((SCREEN_WIDTH / 2, y + 10))

def init_ball():
    """初始化球的位置和速度"""
    global ball
    
    # 创建球
    ball = {
        'x': SCREEN_WIDTH / 2,
        'y': SCREEN_HEIGHT / 2,
        'radius': BALL_RADIUS,
        'color': YELLOW,
        'trail': [],
        'max_trail_length': 10
    }
    
    # 随机初始方向
    angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
    if random.random() > 0.5:
        angle += math.pi
    
    # 计算速度分量
    ball['dx'] = math.cos(angle) * BALL_SPEED
    ball['dy'] = math.sin(angle) * BALL_SPEED

def move_paddle(paddle, dx):
    """移动paddle"""
    paddle['rect'].x += dx
    
    # 确保paddle不会移出屏幕
    paddle['rect'].x = max(0, min(paddle['rect'].x, SCREEN_WIDTH - PADDLE_WIDTH))

def move_ball():
    """移动球"""
    # 添加轨迹点
    ball['trail'].append((ball['x'], ball['y']))
    if len(ball['trail']) > ball['max_trail_length']:
        ball['trail'].pop(0)
    
    # 更新球的位置
    ball['x'] += ball['dx']
    ball['y'] += ball['dy']
    
    # 处理上下墙壁碰撞
    if ball['y'] - ball['radius'] <= 0:
        ball['y'] = ball['radius']
        ball['dy'] = abs(ball['dy'])
    elif ball['y'] + ball['radius'] >= SCREEN_HEIGHT:
        ball['y'] = SCREEN_HEIGHT - ball['radius']
        ball['dy'] = -abs(ball['dy'])

def check_paddle_collision(paddle):
    """检查球是否与paddle碰撞"""
    # 创建球的矩形边界框
    ball_rect = pygame.Rect(
        ball['x'] - ball['radius'],
        ball['y'] - ball['radius'],
        ball['radius'] * 2,
        ball['radius'] * 2
    )
    
    # 检查碰撞
    if ball_rect.colliderect(paddle['rect']):
        # 计算击中位置
        hit_pos = (ball['x'] - paddle['rect'].centerx) / (paddle['rect'].width / 2)
        
        # 根据击中位置调整反弹角度
        angle = hit_pos * (math.pi / 3)
        
        # 根据paddle位置调整Y方向速度
        if paddle['is_top']:
            ball['dy'] = abs(math.sin(angle) * BALL_SPEED)
        else:
            ball['dy'] = -abs(math.sin(angle) * BALL_SPEED)
        
        # 设置X方向速度
        ball['dx'] = math.cos(angle) * BALL_SPEED * (1 if hit_pos > 0 else -1)
        
        # 每次碰撞后速度增加5%
        ball['dx'] *= 1.05
        ball['dy'] *= 1.05
        
        return True
    return False

def check_ball_out_of_bounds():
    """检查球是否出界"""
    global top_score, bottom_score
    
    # 如果球左右出界，重置到屏幕中心
    if ball['x'] < 0 or ball['x'] > SCREEN_WIDTH:
        init_ball()
        return None
    
    # 检查得分情况
    if ball['y'] - ball['radius'] <= 0:
        bottom_score += 1
        init_ball()
        return "top"
    elif ball['y'] + ball['radius'] >= SCREEN_HEIGHT:
        top_score += 1
        init_ball()
        return "bottom"
    
    return None

def handle_events():
    """处理Pygame事件"""
    global running
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_game()

def reset_game():
    """重置游戏"""
    global top_score, bottom_score
    top_score = 0
    bottom_score = 0
    init_ball()

def handle_input():
    """处理玩家输入"""
    keys = pygame.key.get_pressed()
    
    # 顶部paddle控制：A/D键（忽略大小写）
    if keys[pygame.K_a] or keys[pygame.K_q]:  # 支持A和Q键（Q是某些键盘布局的A键位置）
        move_paddle(top_paddle, -top_paddle['speed'])
    if keys[pygame.K_d]:
        move_paddle(top_paddle, top_paddle['speed'])
    
    # 底部paddle控制：左右方向键
    if keys[pygame.K_LEFT]:
        move_paddle(bottom_paddle, -bottom_paddle['speed'])
    if keys[pygame.K_RIGHT]:
        move_paddle(bottom_paddle, bottom_paddle['speed'])

def update():
    """更新游戏状态"""
    # 移动球
    move_ball()
    
    # 检查球与paddle的碰撞
    if check_paddle_collision(top_paddle) or check_paddle_collision(bottom_paddle):
        # 这里可以添加碰撞音效
        pass
    
    # 检查球是否出界
    check_ball_out_of_bounds()

def draw_paddle(paddle):
    """绘制paddle"""
    pygame.draw.rect(screen, paddle['color'], paddle['rect'], border_radius=8)
    pygame.draw.rect(screen, WHITE, paddle['rect'], 2, border_radius=8)

def draw_ball():
    """绘制球"""
    # 绘制轨迹效果
    for i, (trail_x, trail_y) in enumerate(ball['trail']):
        
        alpha = int(255 * (i / len(ball['trail'])))
        radius = int(ball['radius'] * (i / len(ball['trail'])))
        
        # 创建带透明度的表面
        trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(trail_surface, (*YELLOW, alpha), (radius, radius), radius)
        screen.blit(trail_surface, (trail_x - radius, trail_y - radius))
    
    # 绘制主球
    pygame.draw.circle(screen, ball['color'], (int(ball['x']), int(ball['y'])), ball['radius'])
    
    # 为球添加高光效果
    highlight_pos = (int(ball['x']) - 5, int(ball['y']) - 5)
    highlight_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(highlight_surface, (255, 255, 200, 100), (5, 5), 5)
    screen.blit(highlight_surface, highlight_pos)

def draw():
    """在屏幕上绘制所有游戏元素"""
    # 清空屏幕
    screen.fill(BLACK)
    
    # 绘制中心虚线
    pygame.draw.lines(screen, (50, 50, 50), False, center_line_points, 2)
    
    # 绘制paddle
    draw_paddle(top_paddle)
    draw_paddle(bottom_paddle)
    
    # 绘制球
    draw_ball()
    
    # 绘制分数
    top_score_text = font.render(str(top_score), True, RED)
    bottom_score_text = font.render(str(bottom_score), True, BLUE)
    screen.blit(top_score_text, (SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 4))
    screen.blit(bottom_score_text, (SCREEN_WIDTH / 2 - 50, 3 * SCREEN_HEIGHT / 4 - 50))
    
    # 绘制玩家标签
    top_label = small_font.render("Player 2 (WASD: A/D)", True, RED)
    bottom_label = small_font.render("Player 1 (Arrow Keys)", True, BLUE)
    screen.blit(top_label, (20, 20))
    screen.blit(bottom_label, (20, SCREEN_HEIGHT - 40))
    
    # 绘制游戏说明
    instructions = [
        "Controls:",
        "Player 1 (Bottom): Left/Right Arrow Keys",
        "Player 2 (Top): A/D Keys",
        "R: Reset Game  |  ESC: Quit"
    ]
    
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, GREEN)
        screen.blit(text, (SCREEN_WIDTH - 400, 20 + i * 30))
    
    # 更新屏幕显示
    pygame.display.flip()

def main():
    """主函数"""
    # 初始化游戏
    init_game()
    
    # 主游戏循环
    while running:
        handle_events()
        handle_input()
        update()
        draw()
        clock.tick(FPS)
    
    # 退出Pygame
    pygame.quit()

# 启动游戏
if __name__ == "__main__":
    main()