# snake_game.py

import pygame
import random
import json
import os

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20  # Ensure that WIDTH and HEIGHT are multiples of CELL_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Game variables
clock = pygame.time.Clock()
FPS = 15

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# High score file
HIGH_SCORE_FILE = "high_scores.json"


# Load high scores from file
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            return json.load(file)
    return []


# Save high scores to file
def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, "w") as file:
        json.dump(scores, file)


# Get the highest score from all high scores
def get_high_score():
    high_scores = load_high_scores()
    if high_scores:
        return max(score['score'] for score in high_scores)
    return 0


# Display the main menu
def main_menu():
    screen.fill(BLACK)
    title_text = large_font.render("Welcome to Snake Game", True, WHITE)
    play_text = font.render("Press ENTER to Play", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False


# Prompt the player to enter their name
def get_player_name():
    name = ""
    prompt = "Enter your name: "
    active = True
    while active:
        screen.fill(BLACK)
        prompt_text = font.render(prompt + name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "":
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isprintable():
                        name += event.unicode
    return name


# Show game over screen with the player's score and high scores
def game_over_screen(score):
    player_name = get_player_name()
    high_scores = load_high_scores()

    # Add the new score and sort high scores
    high_scores.append({"name": player_name, "score": score})
    high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:5]  # Keep top 5 scores
    save_high_scores(high_scores)

    screen.fill(BLACK)
    game_over_text = large_font.render("Game Over", True, RED)
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    high_scores_text = font.render("High Scores:", True, BLUE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3))
    screen.blit(high_scores_text, (WIDTH // 2 - high_scores_text.get_width() // 2, HEIGHT // 2))

    # Display high scores
    y_offset = HEIGHT // 2 + 40
    for entry in high_scores:
        score_entry = font.render(f"{entry['name']}: {entry['score']}", True, WHITE)
        screen.blit(score_entry, (WIDTH // 2 - score_entry.get_width() // 2, y_offset))
        y_offset += 30

    pygame.display.flip()
    pygame.time.delay(3000)  # Wait a few seconds before returning to the main menu


# Main game function
def play_game():
    snake_pos = [[WIDTH // 2, HEIGHT // 2]]  # Start from the center of the screen
    snake_direction = pygame.K_RIGHT
    snake_length = 1
    score = 0
    paused = False

    # Place food on a grid position
    food_pos = get_random_food_position(snake_pos)
    food_spawned = True
    running = True

    # Retrieve the current high score
    high_score = get_high_score()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT] and not paused:
                    if (event.key == pygame.K_UP and snake_direction != pygame.K_DOWN) or \
                            (event.key == pygame.K_DOWN and snake_direction != pygame.K_UP) or \
                            (event.key == pygame.K_LEFT and snake_direction != pygame.K_RIGHT) or \
                            (event.key == pygame.K_RIGHT and snake_direction != pygame.K_LEFT):
                        snake_direction = event.key
                elif event.key == pygame.K_p:
                    paused = not paused  # Toggle pause
                elif event.key == pygame.K_ESCAPE:
                    return  # Exit to main menu

        if paused:
            continue  # Skip the rest of the loop if the game is paused

        # Move snake
        new_head = move_snake(snake_direction, snake_pos)

        # Check for food collision
        if new_head == food_pos:  # Exact match with food position
            score += 1  # Increase score
            snake_length += 1  # Increase snake length
            food_spawned = False  # Mark food as "eaten" so it will respawn
        else:
            if len(snake_pos) > snake_length:
                snake_pos.pop()  # Remove the last segment to keep the length

        # Respawn food in a new random position if needed
        if not food_spawned:
            food_pos = get_random_food_position(snake_pos)
            food_spawned = True

        # Check for self-collision (game over)
        if check_self_collision(snake_pos):
            running = False

        # Draw everything
        screen.fill(BLACK)
        for segment in snake_pos:
            pygame.draw.rect(screen, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE))

        # Display score and high score
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {max(score, high_score)}", True, WHITE)
        screen.blit(score_text, [10, 10])
        screen.blit(high_score_text, [10, 40])

        pygame.display.flip()
        clock.tick(FPS)

    # Show game over screen with high scores after the game ends
    game_over_screen(score)


# Helper function to get a random food position not occupied by the snake
def get_random_food_position(snake_pos):
    while True:
        position = [random.randrange(0, WIDTH // CELL_SIZE) * CELL_SIZE,
                    random.randrange(0, HEIGHT // CELL_SIZE) * CELL_SIZE]
        if position not in snake_pos:
            return position


# Helper function to move the snake
def move_snake(direction, snake_pos):
    x, y = snake_pos[0]
    if direction == pygame.K_UP:
        y -= CELL_SIZE
    elif direction == pygame.K_DOWN:
        y += CELL_SIZE
    elif direction == pygame.K_LEFT:
        x -= CELL_SIZE
    elif direction == pygame.K_RIGHT:
        x += CELL_SIZE

    # Wrap around the screen if the snake crosses the border
    x %= WIDTH
    y %= HEIGHT

    new_head = [x, y]
    snake_pos.insert(0, new_head)
    return new_head


# Checks if the snake collides with itself
def check_self_collision(snake_pos):
    return snake_pos[0] in snake_pos[1:]


# Main program execution
while True:
    main_menu()
    play_game()
