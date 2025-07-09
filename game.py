import pygame

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Dodgeball!")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255) # New color for Luke's beam
GREEN = (0, 255, 0) # For win message
GRAY = (150, 150, 150) # For game over message

# Beam properties
BEAM_WIDTH = 5
BEAM_HEIGHT = 20

# Luke's beam properties
PLAYER_BEAM_COLOR = BLUE
PLAYER_BEAM_SPEED = -10  # Negative y = up (moves upwards)

# Vader's beam properties
DODGER_BEAM_COLOR = RED
DODGER_BEAM_SPEED = 7 # Positive y = down (moves downwards)
VADER_SHOT_INTERVAL = 60 # Frames between Vader's shots (e.g., 60 frames = 1 second at 60 FPS)

# Player (Luke) properties
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 7 # Speed at which Luke moves horizontally
# Initial position (centered horizontally)
initial_luke_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
initial_luke_y = 500
luke_rect = pygame.Rect(initial_luke_x, initial_luke_y, PLAYER_WIDTH, PLAYER_HEIGHT)

# Dodger (Vader) properties
DODGER_WIDTH = 100
DODGER_HEIGHT = 100
DODGER_SPEED = 4 # Speed at which Vader moves horizontally
# Initial position (centered horizontally, at the top)
initial_vader_x = (SCREEN_WIDTH - DODGER_WIDTH) // 2
initial_vader_y = 40
vader_rect = pygame.Rect(initial_vader_x, initial_vader_y, DODGER_WIDTH, DODGER_HEIGHT)

# Game state variables (will be reset by restart_game)
player_beams = [] # Luke's beams
vader_beams = [] # Vader's beams
vader_alive = True
game_over = False
vader_direction = 1 # 1 for right, -1 for left
vader_shot_timer = 0 # Timer for Vader's shooting

# Load images
# Make sure 'luke.png' and 'vader.png' are in the same directory as your script
try:
    # It's good practice to use .convert_alpha() for images with transparency
    luke_img = pygame.image.load("luke.png").convert_alpha()
    luke_img = pygame.transform.scale(luke_img, (PLAYER_WIDTH, PLAYER_HEIGHT)) # Scale image to match rect size
    vader_img = pygame.image.load("vader.png").convert_alpha()
    vader_img = pygame.transform.scale(vader_img, (DODGER_WIDTH, DODGER_HEIGHT)) # Scale image to match rect size
except pygame.error as e:
    print(f"Error loading images: {e}")
    print("Please ensure 'luke.png' and 'vader.png' are in the same directory.")
    # Create placeholder surfaces if images fail to load
    luke_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
    luke_img.fill(GREEN) # Placeholder color for Luke
    vader_img = pygame.Surface((DODGER_WIDTH, DODGER_HEIGHT))
    vader_img.fill(RED) # Placeholder color for Vader

# Fonts for messages
font_win = pygame.font.Font(None, 74) # Font for "You Win!"
font_game_over = pygame.font.Font(None, 74) # Font for "Game Over!"
font_restart = pygame.font.Font(None, 40) # Font for "Press R to Restart"

# Function to reset game state
def restart_game():
    global player_beams, vader_beams, vader_alive, game_over, luke_rect, vader_rect, vader_direction, vader_shot_timer
    player_beams = []
    vader_beams = []
    vader_alive = True
    game_over = False
    luke_rect.x = initial_luke_x # Reset Luke's position
    vader_rect.x = initial_vader_x # Reset Vader's position
    vader_direction = 1 # Reset Vader's direction to move right initially
    vader_shot_timer = 0 # Reset Vader's shot timer

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over: # Only allow shooting if game is not over
                if event.key == pygame.K_SPACE:
                    # Beam starts from Luke's center top
                    beam_rect = pygame.Rect(luke_rect.centerx - BEAM_WIDTH // 2, luke_rect.top, BEAM_WIDTH, BEAM_HEIGHT)
                    player_beams.append(beam_rect)
            
            # Check for restart key even if game is over
            if event.key == pygame.K_r and game_over:
                restart_game()
            
            if event.key == pygame.K_q:
                running = False

    # Game logic update (only if game is not over)
    if not game_over:
        # Luke's horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            luke_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            luke_rect.x += PLAYER_SPEED
        
        # Keep Luke within screen bounds
        if luke_rect.left < 0:
            luke_rect.left = 0
        if luke_rect.right > SCREEN_WIDTH:
            luke_rect.right = SCREEN_WIDTH

        # Vader's horizontal movement
        if vader_alive: # Only move Vader if he is alive
            vader_rect.x += DODGER_SPEED * vader_direction

            # Reverse direction if Vader hits screen edges
            if vader_rect.left < 0:
                vader_rect.left = 0 # Snap to edge
                vader_direction = 1 # Change direction to right
            elif vader_rect.right > SCREEN_WIDTH:
                vader_rect.right = SCREEN_WIDTH # Snap to edge
                vader_direction = -1 # Change direction to left

            # Vader's shooting logic
            vader_shot_timer += 1
            if vader_shot_timer >= VADER_SHOT_INTERVAL:
                vader_shot_timer = 0 # Reset timer
                # Beam starts from Vader's center bottom
                vader_beam_rect = pygame.Rect(vader_rect.centerx - BEAM_WIDTH // 2, vader_rect.bottom, BEAM_WIDTH, BEAM_HEIGHT)
                vader_beams.append(vader_beam_rect)

        # Update Luke's beam positions and check for off-screen beams
        for beam in player_beams[:]: # Iterate over a copy to allow modification during iteration
            beam.y += PLAYER_BEAM_SPEED
            if beam.y < 0:
                player_beams.remove(beam)
            
            # Collision detection with Vader
            if vader_alive and beam.colliderect(vader_rect):
                vader_alive = False
                game_over = True # Game ends when Vader is hit
                player_beams.remove(beam) # Remove the beam that hit Vader
                print("Vader hit! You Win!")
        
        # Update Vader's beam positions and check for off-screen beams
        for beam in vader_beams[:]: # Iterate over a copy
            beam.y += DODGER_BEAM_SPEED
            if beam.y > SCREEN_HEIGHT: # If beam goes off bottom of screen
                vader_beams.remove(beam)
            
            # Collision detection with Luke
            if beam.colliderect(luke_rect):
                game_over = True # Game ends when Luke is hit
                vader_beams.remove(beam) # Remove the beam that hit Luke
                print("Luke hit! Game Over!")

    # Drawing
    screen.fill(BLACK)

    # Draw Luke
    screen.blit(luke_img, (luke_rect.x, luke_rect.y))

    # Draw Vader only if alive
    if vader_alive:
        screen.blit(vader_img, (vader_rect.x, vader_rect.y))
    else:
        # Display "You Win!" message
        win_text = font_win.render("You Win!", True, GREEN)
        text_rect_win = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(win_text, text_rect_win)

        # Display "Press R to Restart" message
        restart_text = font_restart.render("Press R to Restart", True, WHITE)
        text_rect_restart = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(restart_text, text_rect_restart)
    
    # Display "Game Over!" message if Luke is hit
    if game_over and not vader_alive: # If Vader is dead, it's "You Win!"
        pass # Already handled above
    elif game_over and not vader_alive: # If Vader is dead, it's "You Win!"
        pass # Already handled above
    elif game_over and vader_alive: # If Luke is hit and Vader is still alive, it's "Game Over!"
        game_over_text = font_game_over.render("Game Over!", True, GRAY)
        text_rect_game_over = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(game_over_text, text_rect_game_over)

        restart_text = font_restart.render("Press R to Restart", True, WHITE)
        text_rect_restart = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(restart_text, text_rect_restart)


    # Draw Luke's beams
    for beam in player_beams:
        pygame.draw.rect(screen, PLAYER_BEAM_COLOR, beam)
    
    # Draw Vader's beams
    for beam in vader_beams:
        pygame.draw.rect(screen, DODGER_BEAM_COLOR, beam)

    pygame.display.flip() # Use flip instead of update for full screen update
    clock.tick(60) # Cap the frame rate at 60 FPS

pygame.quit()
