import pygame
from typing import Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
SCREEN_TITLE = "Dual Player Control Game"
FPS = 60
SPEED = 10

# Color definitions
BLACK = (0, 0, 0)

# Boundary limits (assuming image size is 156x18 pixels)
IMAGE_WIDTH, IMAGE_HEIGHT = 156, 18
MAX_X = SCREEN_WIDTH - IMAGE_WIDTH
MAX_Y = SCREEN_HEIGHT - IMAGE_HEIGHT


class Player:
    """Player class to manage individual player's position, image, and movement"""

    def __init__(self, image_path: str, start_x: float, start_y: float):
        """Initialize a player

        Args:
            image_path: Path to the image file
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
        """
        self.image = pygame.image.load(image_path)
        self.image.convert()  # Optimize image format for faster drawing
        self.x = start_x
        self.y = start_y
        self.speed = SPEED

    def move(self, dx: float, dy: float) -> None:
        """Move the player

        Args:
            dx: Distance to move on X axis
            dy: Distance to move on Y axis
        """
        self.x += dx
        self.y += dy
        self._enforce_boundaries()

    def _enforce_boundaries(self) -> None:
        """Ensure player stays within screen boundaries"""
        self.x = max(0, min(self.x, MAX_X))
        self.y = max(0, min(self.y, MAX_Y))

    def get_position(self) -> Tuple[float, float]:
        """Get current player position"""
        return (self.x, self.y)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw player on the screen"""
        screen.blit(self.image, (self.x, self.y))


def handle_player1_input(player: Player) -> None:
    """Handle input for Player 1 (arrow keys)"""
    keys = pygame.key.get_pressed()

    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx -= player.speed
    if keys[pygame.K_RIGHT]:
        dx += player.speed
    if keys[pygame.K_UP]:
        dy -= player.speed
    if keys[pygame.K_DOWN]:
        dy += player.speed

    if dx != 0 or dy != 0:
        player.move(dx, dy)


def handle_player2_input(player: Player) -> None:
    """Handle input for Player 2 (WASD keys)"""
    keys = pygame.key.get_pressed()

    dx, dy = 0, 0
    if keys[pygame.K_a]:
        dx -= player.speed
    if keys[pygame.K_d]:
        dx += player.speed
    if keys[pygame.K_w]:
        dy -= player.speed
    if keys[pygame.K_s]:
        dy += player.speed

    if dx != 0 or dy != 0:
        player.move(dx, dy)


def main() -> None:
    """Main game function"""
    # Initialize the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    # Load resources
    # Note: Uncomment the next line if you have a background image
    # background = pygame.image.load("space.webp")

    # Create player objects
    player1 = Player("Board(2).png", 461.5, 75)  # Player 1 (arrow keys)
    player2 = Player("Board(2).png", 461.5, 627)  # Player 2 (WASD keys)

    # Game clock for controlling frame rate
    clock = pygame.time.Clock()
    running = True

    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Process player input
        handle_player1_input(player1)
        handle_player2_input(player2)

        # Rendering
        screen.fill(BLACK)  # Clear the screen
        # Uncomment to draw background: screen.blit(background, (0, 0))
        player1.draw(screen)
        player2.draw(screen)

        # Update the display
        pygame.display.flip()

        # Control frame rate
        clock.tick(FPS)

    # Quit the game properly
    pygame.quit()


if __name__ == "__main__":
    main()