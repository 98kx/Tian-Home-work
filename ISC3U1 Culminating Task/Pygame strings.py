import pygame  # Import the Pygame library

# Initialize all Pygame modules
pygame.init()

# Set up display dimensions
WIDTH, HEIGHT = 1080, 720  # Window size in pixels
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create the game window
pygame.display.set_caption("Adding an Image to the Surface")  # Set the window title

# Define colors using RGB values
BLACK = (0, 0, 0)  # Each value is Red, Green, Blue (0-255)(gray is 128 for all)

# -----------------------------
# Load an image and prepare it for display
# -----------------------------
# IMPORTANT: Replace 'bird.png' with the actual image file in your project folder.
# pygame.image.load() loads the image into memory.
player_background = pygame.image.load("space.webp")
player_image = pygame.image.load("Board(2).png")  # Load the image file
player_image.convert() #optimizes the image format and makes drawing faster
player_image1 = pygame.image.load("Board(2).png")
player_image1.convert()
# Set initial position for the image
image_x = 461.5  # X-coordinate where the image will be drawn
image_y = 75  # Y-coordinate where the image will be drawn
image1_y = 627
image1_x = 461.5
speed = 10# Movement speed in pixels per frame

# -----------------------------
# Create a clock object to control frame rate
# -----------------------------
clock = pygame.time.Clock()  # This helps keep the game running at a steady speed (e.g., 60 FPS)


# Game loop control variable
running = True  # When True, the game keeps running


# Start the game loop
while running:
    # -------------------------
    # Check which keys are currently pressed
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # If the user clicks the close button
            running = False  # Stop the loop and exit the game

        
    # Check keys for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        image_x -= speed  # Move left
    if keys[pygame.K_RIGHT]:
        image_x += speed  # Move right
    if keys[pygame.K_UP]:
        image_y -= speed  # Move up
    if keys[pygame.K_DOWN]:
        image_y += speed  # Move down
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
         image1_x -= speed  # Move left
    if keys[pygame.K_d]:
        image1_x += speed  # Move right
    if keys[pygame.K_w]:
        image1_y -= speed  # Move up
    if keys[pygame.K_s]:
        image1_y += speed  # Move down

    # Boundary collision: keep inside the screen
    if image1_x < 0:
        image1_x = 0
    if image1_x > 923:
        image1_x = 923
    if image1_y < 0:
        image1_y = 0
    if image1_y > 702:
        image1_y =702 

    if image_x < 0:
        image_x = 0
    if image_x > 923:
        image_x = 923
    if image_y < 0:
        image_y = 0
    if image_y > 702:
        image_y = 702



    # Drawing commands go here
    screen.fill(BLACK)  # Fill the screen with white color every frame

    # Draw the image on the screen at the specified position
    # screen.blit() is used to draw images onto the surface.
    screen.blit(player_image1, (image1_x, image1_y))
    screen.blit(player_image, (image_x, image_y))

    # Update the display so changes appear on the screen
    pygame.display.flip()
    # -------------------------
    # Control the frame rate (60 frames per second)
    # -------------------------
    clock.tick(60)  # This makes sure the game runs smoothly and doesn't use too much CPU


# Quit Pygame properly after the loop ends
pygame.quit()
