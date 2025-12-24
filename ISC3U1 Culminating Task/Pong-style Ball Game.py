import pygame
import random
import math
from typing import Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
SCREEN_TITLE = "Pong-Style Ball Game"
FPS = 60
PADDLE_SPEED = 10
BALL_SPEED = 8
PADDLE_WIDTH, PADDLE_HEIGHT = 156, 18
BALL_RADIUS = 15

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 255, 100)
YELLOW = (255, 255, 50)


class Paddle:
    """Paddle class to manage player's paddle"""

    def __init__(self, x: float, y: float, color: Tuple[int, int, int], is_top: bool = False):
        """Initialize a paddle

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            color: Paddle color
            is_top: Whether this is the top paddle (for collision detection)
        """
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.is_top = is_top
        self.speed = PADDLE_SPEED

    def move(self, dx: float) -> None:
        """Move the paddle horizontally

        Args:
            dx: Distance to move on X axis
        """
        self.rect.x += dx
        self._enforce_boundaries()

    def _enforce_boundaries(self) -> None:
        """Ensure paddle stays within screen boundaries"""
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PADDLE_WIDTH))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw paddle on the screen"""
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        # Add a subtle outline
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)


class Ball:
    """Ball class to manage the game ball"""

    def __init__(self, x: float, y: float):
        """Initialize the ball

        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.color = YELLOW

        # Start with a random direction
        angle = random.uniform(math.pi / 4, 3 * math.pi / 4)  # 45 to 135 degrees
        if random.random() > 0.5:
            angle += math.pi  # Reverse direction

        self.dx = math.cos(angle) * BALL_SPEED
        self.dy = math.sin(angle) * BALL_SPEED

        # Trail effect
        self.trail = []
        self.max_trail_length = 10

    def move(self) -> None:
        """Move the ball and handle wall collisions"""
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Move the ball
        self.x += self.dx
        self.y += self.dy

        # Bounce off top and bottom walls
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy = abs(self.dy)
        elif self.y + self.radius >= SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.dy = -abs(self.dy)

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Check if the ball collides with a paddle

        Args:
            paddle: The paddle to check collision with

        Returns:
            True if collision occurred, False otherwise
        """
        # Simple AABB collision
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

        if ball_rect.colliderect(paddle.rect):
            # Calculate hit position (from -1 to 1, where -1 is left edge, 1 is right edge)
            hit_pos = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)

            # Adjust angle based on where the ball hit the paddle
            angle = hit_pos * (math.pi / 3)  # Max 60 degrees from center

            # Reverse Y direction
            if paddle.is_top:
                self.dy = abs(math.sin(angle) * BALL_SPEED)
            else:
                self.dy = -abs(math.sin(angle) * BALL_SPEED)

            # Set X direction based on hit position
            self.dx = math.cos(angle) * BALL_SPEED * (1 if hit_pos > 0 else -1)

            # Add a small speed increase on each hit
            self.dx *= 1.05
            self.dy *= 1.05

            return True
        return False

    def is_out_of_bounds(self) -> Optional[str]:
        """Check if ball is out of bounds (scored)

        Returns:
            "top" if top player scored, "bottom" if bottom player scored, None otherwise
        """
        if self.x < 0 or self.x > SCREEN_WIDTH:
            # Reset position if ball goes out sideways
            self.x = SCREEN_WIDTH / 2
            self.y = SCREEN_HEIGHT / 2
            # Start with a random direction
            angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
            self.dx = math.cos(angle) * BALL_SPEED
            self.dy = math.sin(angle) * BALL_SPEED

        # Check for scoring
        if self.y - self.radius <= 0:
            return "top"
        elif self.y + self.radius >= SCREEN_HEIGHT:
            return "bottom"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw ball on the screen with trail effect"""
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            radius = int(self.radius * (i / len(self.trail)))
            trail_color = (YELLOW[0], YELLOW[1], YELLOW[2], alpha)

            # Create a surface for the trail circle with alpha
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*trail_color[:3], alpha), (radius, radius), radius)
            screen.blit(trail_surface, (trail_x - radius, trail_y - radius))

        # Draw the ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Add a highlight to the ball
        highlight_pos = (int(self.x) - 5, int(self.y) - 5)
        pygame.draw.circle(screen, (255, 255, 200, 100), highlight_pos, 5)


class Game:
    """Main game class to manage game state"""

    def __init__(self):
        """Initialize the game"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)

        # Create paddles
        self.top_paddle = Paddle(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, 20, RED, is_top=True)
        self.bottom_paddle = Paddle(SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, SCREEN_HEIGHT - 40, BLUE, is_top=False)

        # Create ball
        self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Scores
        self.top_score = 0
        self.bottom_score = 0

        # Font for score display
        self.font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 36)

        # Game clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Center line
        self.center_line_points = []
        for y in range(0, SCREEN_HEIGHT, 20):
            self.center_line_points.append((SCREEN_WIDTH / 2, y))
            self.center_line_points.append((SCREEN_WIDTH / 2, y + 10))

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Reset game
                    self.top_score = 0
                    self.bottom_score = 0
                    self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def handle_input(self) -> None:
        """Handle player input"""
        keys = pygame.key.get_pressed()

        # Top paddle (Player 2) controls: A/D
        if keys[pygame.K_a]:
            self.top_paddle.move(-self.top_paddle.speed)
        if keys[pygame.K_d]:
            self.top_paddle.move(self.top_paddle.speed)

        # Bottom paddle (Player 1) controls: Left/Right arrows
        if keys[pygame.K_LEFT]:
            self.bottom_paddle.move(-self.bottom_paddle.speed)
        if keys[pygame.K_RIGHT]:
            self.bottom_paddle.move(self.bottom_paddle.speed)

    def update(self) -> None:
        """Update game state"""
        # Move the ball
        self.ball.move()

        # Check paddle collisions
        if self.ball.check_paddle_collision(self.top_paddle) or \
                self.ball.check_paddle_collision(self.bottom_paddle):
            # Play sound effect would go here
            pass

        # Check if ball is out of bounds (scored)
        score_result = self.ball.is_out_of_bounds()
        if score_result == "top":
            self.bottom_score += 1
            # Reset ball
            self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        elif score_result == "bottom":
            self.top_score += 1
            # Reset ball
            self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def draw(self) -> None:
        """Draw everything on the screen"""
        # Clear the screen
        self.screen.fill(BLACK)

        # Draw center line
        pygame.draw.lines(self.screen, (50, 50, 50), False, self.center_line_points, 2)

        # Draw paddles
        self.top_paddle.draw(self.screen)
        self.bottom_paddle.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw scores
        top_score_text = self.font.render(str(self.top_score), True, RED)
        bottom_score_text = self.font.render(str(self.bottom_score), True, BLUE)

        self.screen.blit(top_score_text, (SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 4))
        self.screen.blit(bottom_score_text, (SCREEN_WIDTH / 2 - 50, 3 * SCREEN_HEIGHT / 4 - 50))

        # Draw player labels
        top_label = self.small_font.render("Player 2 (WASD: A/D)", True, RED)
        bottom_label = self.small_font.render("Player 1 (Arrow Keys)", True, BLUE)

        self.screen.blit(top_label, (20, 20))
        self.screen.blit(bottom_label, (20, SCREEN_HEIGHT - 40))

        # Draw instructions
        instructions = [
            "Controls:",
            "Player 1 (Bottom): Left/Right Arrow Keys",
            "Player 2 (Top): A/D Keys",
            "R: Reset Game  |  ESC: Quit"
        ]

        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, GREEN)
            self.screen.blit(text, (SCREEN_WIDTH - 400, 20 + i * 30))

        # Update display
        pygame.display.flip()

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()