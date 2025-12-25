# 导入所需库
import pygame  # 游戏开发库
import random  # 随机数生成
import math  # 数学函数
from typing import Tuple, Optional  # 类型注解支持

# 初始化Pygame库
pygame.init()

# 游戏常量定义
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720  # 游戏窗口尺寸
SCREEN_TITLE = "Pong-Style Ball Game"  # 窗口标题
FPS = 60  # 帧率（每秒更新次数）
PADDLE_SPEED = 10  #  paddle移动速度
BALL_SPEED = 8  # 球的初始速度
PADDLE_WIDTH, PADDLE_HEIGHT = 156, 18  # paddle尺寸
BALL_RADIUS = 15  # 球的半径

# 颜色定义（RGB格式）
BLACK = (0, 0, 0)  # 背景色
WHITE = (255, 255, 255)  # 边框和高亮色
RED = (255, 50, 50)  # 顶部paddle和玩家2颜色
BLUE = (50, 100, 255)  # 底部paddle和玩家1颜色
GREEN = (50, 255, 100)  # 说明文字颜色
YELLOW = (255, 0, 0)  # 球的颜色


class Paddle:
    """Paddle类用于管理玩家的paddle"""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], is_top: bool = False):
        """初始化paddle对象

        Args:
            x: 初始X坐标
            y: 初始Y坐标
            color: Paddle颜色（RGB元组）
            is_top: 是否为顶部paddle（影响碰撞检测的方向）
        """
        # 创建paddle的矩形对象，用于碰撞检测和绘制
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color  # 存储颜色
        self.is_top = is_top  # 标记是否为顶部paddle
        self.speed = PADDLE_SPEED  # 设置移动速度

    def move(self, dx: float) -> None:
        """水平移动paddle

        Args:
            dx: X轴移动距离（负值向左，正值向右）
        """
        self.rect.x += dx  # 更新X坐标
        self._enforce_boundaries()  # 确保paddle不会移出屏幕

    def _enforce_boundaries(self) -> None:
        """确保paddle始终保持在屏幕边界内"""
        # 使用max和min函数限制paddle的X坐标范围
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PADDLE_WIDTH))

    def draw(self, screen: pygame.Surface) -> None:
        """在屏幕上绘制paddle

        Args:
            screen: Pygame显示表面对象
        """
        # 绘制填充的圆角矩形作为paddle主体
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        # 添加白色边框增加视觉效果
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)


class Ball:
    """Ball类用于管理游戏中的球"""

    def __init__(self, x: float, y: float):
        """初始化球对象

        Args:
            x: 初始X坐标
            y: 初始Y坐标
        """
        self.x = x  # 球的X坐标（使用浮点数提高精度）
        self.y = y  # 球的Y坐标
        self.radius = BALL_RADIUS  # 球的半径
        self.color = YELLOW  # 球的颜色

        # 随机初始方向：45到135度之间（确保球不会直接水平或垂直移动）
        angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
        # 50%概率反转方向
        rd = random.random()
        print(rd )
        if rd > 0.5:
            angle += math.pi  # 反转180度

        # 计算X和Y方向的速度分量
        self.dx = math.cos(angle) * BALL_SPEED
        self.dy = math.sin(angle) * BALL_SPEED

        # 轨迹效果相关变量
        self.trail = []  # 存储轨迹点的列表
        self.max_trail_length = 10  # 最大轨迹长度

    def move(self) -> None:
        """移动球并处理墙壁碰撞"""
        # 添加当前位置到轨迹列表
        self.trail.append((self.x, self.y))
        # 如果轨迹过长，移除最旧的点
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # 更新球的位置
        self.x += self.dx
        self.y += self.dy

        # 处理上下墙壁碰撞
        if self.y - self.radius <= 0:  # 碰撞顶部墙壁
            self.y = self.radius  # 重置位置以避免球卡在墙内
            self.dy = abs(self.dy)  # Y方向速度变为正值（向下）
        elif self.y + self.radius >= SCREEN_HEIGHT:  # 碰撞底部墙壁
            self.y = SCREEN_HEIGHT - self.radius  # 重置位置
            self.dy = -abs(self.dy)  # Y方向速度变为负值（向上）

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """检查球是否与paddle碰撞

        Args:
            paddle: 要检查的paddle对象

        Returns:
            如果发生碰撞返回True，否则返回False
        """
        # 创建球的矩形边界框用于AABB碰撞检测
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

        # 检查球的矩形是否与paddle的矩形重叠
        if ball_rect.colliderect(paddle.rect):
            # 计算球在paddle上的击中位置（-1到1之间，-1为左边缘，1为右边缘）
            hit_pos = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)

            # 根据击中位置调整反弹角度（最大偏离中心60度）
            angle = hit_pos * (math.pi / 3)  # 弧度制的60度

            # 根据paddle位置调整Y方向速度
            if paddle.is_top:  # 顶部paddle，球应向下反弹
                self.dy = abs(math.sin(angle) * BALL_SPEED)
            else:  # 底部paddle，球应向上反弹
                self.dy = -abs(math.sin(angle) * BALL_SPEED)

            # 根据击中位置设置X方向速度
            self.dx = math.cos(angle) * BALL_SPEED * (1 if hit_pos > 0 else -1)

            # 每次碰撞后速度增加5%，增加游戏难度
            self.dx *= 1.05
            self.dy *= 1.05

            return True
        return False

    def is_out_of_bounds(self) -> Optional[str]:
        """检查球是否出界（得分情况）

        Returns:
            - "top": 如果球越过顶部边界（底部玩家得分）
            - "bottom": 如果球越过底部边界（顶部玩家得分）
            - None: 如果球没有出界
        """
        # 如果球左右出界，重置到屏幕中心并随机方向
        if self.x < 0 or self.x > SCREEN_WIDTH:
            # 重置位置到屏幕中心
            self.x = SCREEN_WIDTH / 2
            self.y = SCREEN_HEIGHT / 2
            # 随机初始方向
            angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
            self.dx = math.cos(angle) * BALL_SPEED
            self.dy = math.sin(angle) * BALL_SPEED

        # 检查得分情况
        if self.y - self.radius <= 0:  # 球越过顶部边界
            return "top"
        elif self.y + self.radius >= SCREEN_HEIGHT:  # 球越过底部边界
            return "bottom"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """在屏幕上绘制球及其轨迹效果

        Args:
            screen: Pygame显示表面对象
        """
        # 绘制轨迹效果
        for i, (trail_x, trail_y) in enumerate(self.trail):
            # 计算轨迹点的透明度（从透明到不透明）
            alpha = 200 #int(1 * (i / len(self.trail)))
            # 计算轨迹点的半径（从大到小）
            radius = 10 +int(self.radius * (i / len(self.trail)))
            # 轨迹颜色（与球同色但带透明度）
            trail_color = (YELLOW[0], YELLOW[1], YELLOW[2], alpha)

            # 创建带透明度的表面用于绘制轨迹
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            # 在透明表面上绘制轨迹点
            pygame.draw.circle(trail_surface, (*trail_color[:3], alpha), (radius, radius), radius)
            # 将轨迹点绘制到主屏幕
            screen.blit(trail_surface, (trail_x - radius, trail_y - radius))

        # 绘制主球
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # 为球添加高光效果，增加立体感
        highlight_pos = (int(self.x) - 5, int(self.y) - 5)
        pygame.draw.circle(screen, (255, 255, 200, 100), highlight_pos, 5)


class Game:
    """主游戏类，管理游戏状态和游戏循环"""

    def __init__(self):
        """初始化游戏对象"""
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 设置窗口标题
        pygame.display.set_caption(SCREEN_TITLE)

        # 创建paddle对象
        self.top_paddle = Paddle(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, 20, RED, is_top=True)
        self.bottom_paddle = Paddle(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, BLUE, is_top=False)

        # 创建球对象
        self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # 分数初始化
        self.top_score = 0  # 顶部玩家分数
        self.bottom_score = 0  # 底部玩家分数

        # 字体设置
        self.font = pygame.font.SysFont(None, 72)  # 大字体用于显示分数
        self.small_font = pygame.font.SysFont(None, 36)  # 小字体用于显示说明

        # 游戏时钟（控制帧率）
        self.clock = pygame.time.Clock()
        self.running = True  # 游戏运行状态标志

        # 创建中心虚线
        self.center_line_points = []
        for y in range(0, SCREEN_HEIGHT, 20):
            # 添加虚线的每个线段的起点和终点
            self.center_line_points.append((SCREEN_WIDTH / 2, y))
            self.center_line_points.append((SCREEN_WIDTH / 2, y + 10))

    def handle_events(self) -> None:
        """处理Pygame事件（如窗口关闭、按键按下等）"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 窗口关闭事件
                self.running = False  # 停止游戏循环
            elif event.type == pygame.KEYDOWN:  # 按键按下事件
                if event.key == pygame.K_ESCAPE:  # ESC键退出游戏
                    self.running = False
                elif event.key == pygame.K_r:  # R键重置游戏
                    self.top_score = 0  # 重置分数
                    self.bottom_score = 0
                    self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)  # 创建新球

    def handle_input(self) -> None:
        """处理玩家输入（键盘控制）"""
        keys = pygame.key.get_pressed()  # 获取当前所有按下的键

        # 顶部paddle（玩家2）控制：A/D键
        if keys[pygame.K_a]:  # A键向左移动
            self.top_paddle.move(-self.top_paddle.speed)
        if keys[pygame.K_d]:  # D键向右移动
            self.top_paddle.move(self.top_paddle.speed)

        # 底部paddle（玩家1）控制：左右方向键
        if keys[pygame.K_LEFT]:  # 左方向键向左移动
            self.bottom_paddle.move(-self.bottom_paddle.speed)
        if keys[pygame.K_RIGHT]:  # 右方向键向右移动
            self.bottom_paddle.move(self.bottom_paddle.speed)

    def update(self) -> None:
        """更新游戏状态"""
        # 移动球
        self.ball.move()

        # 检查球与paddle的碰撞
        if self.ball.check_paddle_collision(self.top_paddle) or \
                self.ball.check_paddle_collision(self.bottom_paddle):
            # 这里可以添加碰撞音效
            pass

        # 检查球是否出界（得分）
        score_result = self.ball.is_out_of_bounds()
        if score_result == "top":  # 球越过顶部边界，底部玩家得分
            self.bottom_score += 1
            # 重置球到中心
            self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        elif score_result == "bottom":  # 球越过底部边界，顶部玩家得分
            self.top_score += 1
            # 重置球到中心
            self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def draw(self) -> None:
        """在屏幕上绘制所有游戏元素"""
        # 清空屏幕（黑色背景）
        self.screen.fill(BLACK)

        # 绘制中心虚线
        pygame.draw.lines(self.screen, (50, 50, 50), False, self.center_line_points, 2)

        # 绘制paddle
        self.top_paddle.draw(self.screen)
        self.bottom_paddle.draw(self.screen)

        # 绘制球
        self.ball.draw(self.screen)

        # 绘制分数
        top_score_text = self.font.render(str(self.top_score), True, RED)  # 创建分数文本
        bottom_score_text = self.font.render(str(self.bottom_score), True, BLUE)
        # 绘制分数到屏幕
        self.screen.blit(top_score_text, (SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 4))
        self.screen.blit(bottom_score_text, (SCREEN_WIDTH / 2 - 50, 3 * SCREEN_HEIGHT / 4 - 50))

        # 绘制玩家标签
        top_label = self.small_font.render("Player 2 (WASD: A/D)", True, RED)
        bottom_label = self.small_font.render("Player 1 (Arrow Keys)", True, BLUE)
        self.screen.blit(top_label, (20, 20))
        self.screen.blit(bottom_label, (20, SCREEN_HEIGHT - 40))

        # 绘制游戏说明
        instructions = [
            "Controls:",
            "Player 1 (Bottom): Left/Right Arrow Keys",
            "Player 2 (Top): A/D Keys",
            "R: Reset Game  |  ESC: Quit"
        ]

        # 绘制每条说明文字
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, GREEN)
            self.screen.blit(text, (SCREEN_WIDTH - 400, 20 + i * 30))

        # 更新屏幕显示
        pygame.display.flip()

    def run(self) -> None:
        """主游戏循环"""
        while self.running:
            self.handle_events()  # 处理事件
            self.handle_input()  # 处理输入
            self.update()  # 更新游戏状态
            self.draw()  # 绘制游戏元素
            self.clock.tick(FPS)  # 控制帧率

        pygame.quit()  # 退出Pygame


# 如果直接运行此文件，启动游戏
if __name__ == "__main__":
    game = Game()  # 创建游戏对象
    game.run()  # 运行游戏