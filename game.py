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
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0) # For menu selection highlight
DARK_GRAY = (50, 50, 50) # For menu button background
LIGHT_GRAY = (200, 200, 200) # For description text

# Beam properties
BEAM_WIDTH = 5
BEAM_HEIGHT = 20

# Luke's beam properties
PLAYER_BEAM_COLOR = BLUE
PLAYER_BEAM_SPEED = -10

# Vader's beam properties
DODGER_BEAM_COLOR = RED
DODGER_BEAM_SPEED = 7
VADER_SHOT_INTERVAL = 60 # Frames between Vader's shots

# Player (Luke) properties
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 7
initial_luke_x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2
initial_luke_y = 500
luke_rect = pygame.Rect(initial_luke_x, initial_luke_y, PLAYER_WIDTH, PLAYER_HEIGHT)

# Dodger (Vader) properties
DODGER_WIDTH = 100
DODGER_HEIGHT = 100
DODGER_SPEED = 4
initial_vader_x = (SCREEN_WIDTH - DODGER_WIDTH) // 2
initial_vader_y = 40
vader_rect = pygame.Rect(initial_vader_x, initial_vader_y, DODGER_WIDTH, DODGER_HEIGHT)

# Game state variables (will be reset by restart_game)
player_beams = []
vader_beams = []
vader_alive = True
game_over = False
vader_direction = 1 # 1 for right, -1 for left
vader_shot_timer = 0
selected_ml_type = None # Stores the chosen ML type from the menu

# Load images
try:
    luke_img = pygame.image.load("luke.png").convert_alpha()
    luke_img = pygame.transform.scale(luke_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
    vader_img = pygame.image.load("vader.png").convert_alpha()
    vader_img = pygame.transform.scale(vader_img, (DODGER_WIDTH, DODGER_HEIGHT))
except pygame.error as e:
    print(f"Error loading images: {e}")
    print("Please ensure 'luke.png' and 'vader.png' are in the same directory.")
    luke_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
    luke_img.fill(GREEN)
    vader_img = pygame.Surface((DODGER_WIDTH, DODGER_HEIGHT))
    vader_img.fill(RED)

# Fonts for messages
font_title = pygame.font.Font(None, 90)
font_menu = pygame.font.Font(None, 50)
font_description = pygame.font.Font(None, 28) # Smaller font for descriptions
font_win = pygame.font.Font(None, 74)
font_game_over = pygame.font.Font(None, 74)
font_restart = pygame.font.Font(None, 40)

# Function to reset game state
def restart_game():
    global player_beams, vader_beams, vader_alive, game_over, luke_rect, vader_rect, vader_direction, vader_shot_timer
    player_beams = []
    vader_beams = []
    vader_alive = True
    game_over = False
    luke_rect.x = initial_luke_x
    vader_rect.x = initial_vader_x
    vader_direction = 1
    vader_shot_timer = 0

# Machine Learning options and their descriptions
ml_options_data = {
    "Rule-Based (Constant Movement)": {
        "description": (
            "Vader's movement is entirely predictable, following a simple, pre-programmed pattern. "
            "He will move back and forth at a constant speed, bouncing off the screen edges. "
            "This mode demonstrates a non-adaptive AI, making it easier to predict and defeat once you learn his pattern."
        )
    },
    "Reinforcement Learning (Q-Learning)": {
        "description": (
            "Vader learns to dodge by trial and error. He will explore different movements and "
            "receive 'rewards' for dodging your beams and 'penalties' for being hit. "
            "Over time, he aims to optimize his dodging strategy based on past experiences, becoming more challenging as he 'learns'."
        )
    },
    "Genetic Algorithm": {
        "description": (
            "Vader's dodging strategy evolves over generations, much like natural selection. "
            "Multiple 'Vaders' with slightly different dodging behaviors will compete. "
            "The most successful dodgers 'survive' and 'reproduce', passing on their best traits. "
            "This process aims to create an increasingly resilient dodging AI over many game rounds."
        )
    },
    "Neural Network (Pre-Trained)": {
        "description": (
            "Vader's dodging is controlled by a pre-trained artificial neural network. "
            "This network has already learned complex dodging patterns from extensive simulated gameplay. "
            "While not learning in real-time during your game, it demonstrates the power of deep learning "
            "to create highly effective and intelligent AI behaviors."
        )
    },
    "Simple Heuristic (Predictive)": {
        "description": (
            "Vader uses a simple predictive heuristic to anticipate where your beams will land. "
            "He calculates the beam's trajectory and attempts to move to a safe spot. "
            "This AI is more intelligent than a purely rule-based one, reacting to threats "
            "by making calculated movements rather than just following a fixed path."
        )
    }
}
ml_option_names = list(ml_options_data.keys())

# Function to wrap text for display
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

def main_menu():
    global selected_ml_type
    menu_running = True
    selected_option_index = 0 # Index of the currently highlighted option
    
    # Menu states: 0 = selecting option, 1 = displaying description
    menu_state = 0 

    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if menu_state == 0: # Selecting option
                    if event.key == pygame.K_UP:
                        selected_option_index = (selected_option_index - 1) % len(ml_option_names)
                    elif event.key == pygame.K_DOWN:
                        selected_option_index = (selected_option_index + 1) % len(ml_option_names)
                    elif event.key == pygame.K_RETURN: # Select option, move to description state
                        menu_state = 1
                elif menu_state == 1: # Displaying description
                    if event.key == pygame.K_RETURN: # Confirm selection and exit menu
                        selected_ml_type = ml_option_names[selected_option_index]
                        menu_running = False
                
                if event.key == pygame.K_q: # Quit from any menu state
                    pygame.quit()
                    exit()

        screen.fill(BLACK)

        if menu_state == 0: # Displaying options
            # Title
            title_text = font_title.render("Star Wars Dodgeball", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            screen.blit(title_text, title_rect)

            # Instructions
            instruction_text = font_menu.render("Choose Vader's AI:", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
            screen.blit(instruction_text, instruction_rect)

            # Menu options
            for i, option_name in enumerate(ml_option_names):
                text_color = YELLOW if i == selected_option_index else WHITE
                option_text = font_menu.render(option_name, True, text_color)
                
                # Calculate position for each option
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60 + i * 60))
                
                # Draw a background rectangle for the selected option
                if i == selected_option_index:
                    padding = 20
                    bg_rect = pygame.Rect(option_rect.left - padding, option_rect.top - padding,
                                          option_rect.width + 2 * padding, option_rect.height + 2 * padding)
                    pygame.draw.rect(screen, DARK_GRAY, bg_rect, border_radius=10) # Rounded corners
                
                screen.blit(option_text, option_rect)
            
            # Instruction to press ENTER to view description
            select_instruction = font_restart.render("Press ENTER to View Description", True, WHITE)
            select_instruction_rect = select_instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(select_instruction, select_instruction_rect)

        elif menu_state == 1: # Displaying description
            current_option_name = ml_option_names[selected_option_index]
            description = ml_options_data[current_option_name]["description"]
            
            # Display selected option name
            selected_title = font_menu.render(current_option_name, True, YELLOW)
            selected_title_rect = selected_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            screen.blit(selected_title, selected_title_rect)

            # Wrap and display description
            wrapped_lines = wrap_text(description, font_description, SCREEN_WIDTH - 100) # 100px padding
            
            y_offset = SCREEN_HEIGHT // 2 - (len(wrapped_lines) * font_description.get_linesize()) // 2 # Center vertically
            
            for line in wrapped_lines:
                line_surface = font_description.render(line, True, LIGHT_GRAY)
                line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                screen.blit(line_surface, line_rect)
                y_offset += font_description.get_linesize() + 5 # Move down for next line
            
            # Add instruction to press ENTER to start
            start_instruction = font_restart.render("Press ENTER to Start Game", True, WHITE)
            start_instruction_rect = start_instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(start_instruction, start_instruction_rect)

        pygame.display.flip()
        clock.tick(60)

# --- Game Start ---
# Call the main menu function before starting the game loop
main_menu()
print(f"Selected ML type for Vader: {selected_ml_type}")

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

        # Vader's horizontal movement (currently constant, will be replaced by ML)
        if vader_alive: # Only move Vader if he is alive
            vader_rect.x += DODGER_SPEED * vader_direction

            # Reverse direction if Vader hits screen edges
            if vader_rect.left < 0:
                vader_rect.left = 0
                vader_direction = 1
            elif vader_rect.right > SCREEN_WIDTH:
                vader_rect.right = SCREEN_WIDTH
                vader_direction = -1

            # Vader's shooting logic
            vader_shot_timer += 1
            if vader_shot_timer >= VADER_SHOT_INTERVAL:
                vader_shot_timer = 0
                vader_beam_rect = pygame.Rect(vader_rect.centerx - BEAM_WIDTH // 2, vader_rect.bottom, BEAM_WIDTH, BEAM_HEIGHT)
                vader_beams.append(vader_beam_rect)

        # Update Luke's beam positions and check for off-screen beams
        for beam in player_beams[:]:
            beam.y += PLAYER_BEAM_SPEED
            if beam.y < 0:
                player_beams.remove(beam)
            
            # Collision detection with Vader
            if vader_alive and beam.colliderect(vader_rect):
                vader_alive = False
                game_over = True
                player_beams.remove(beam)
                print("Vader hit! You Win!")
        
        # Update Vader's beam positions and check for off-screen beams
        for beam in vader_beams[:]:
            beam.y += DODGER_BEAM_SPEED
            if beam.y > SCREEN_HEIGHT:
                vader_beams.remove(beam)
            
            # Collision detection with Luke
            if beam.colliderect(luke_rect):
                game_over = True
                vader_beams.remove(beam)
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
    if game_over and not vader_alive:
        pass # Already handled above (You Win!)
    elif game_over and vader_alive:
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
