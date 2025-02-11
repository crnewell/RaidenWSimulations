import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 500  # Window size (square)
GRID_SIZE = 15      # Number of rows and columns in the maze
CELL_SIZE = WINDOW_SIZE // GRID_SIZE  # Size of each cell

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Maze array (1s are walls, 0s are paths)
maze = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
]

# Player's starting position
player_pos = [0, 1]  # Row, Col

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("15x15 Maze")

# Function to draw the maze
def draw_maze():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = BLACK if maze[row][col] == 1 else WHITE
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Function to draw the player
def draw_player():
    pygame.draw.rect(
        screen, RED, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

# Main loop
running = True
clock = pygame.time.Clock()
move_direction = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_direction = "UP"
            elif event.key == pygame.K_DOWN:
                move_direction = "DOWN"
            elif event.key == pygame.K_LEFT:
                move_direction = "LEFT"
            elif event.key == pygame.K_RIGHT:
                move_direction = "RIGHT"
        elif event.type == pygame.KEYUP:
            move_direction = None

    # Move the player continuously in the held direction
    if move_direction == "UP":
        new_pos = [player_pos[0] - 1, player_pos[1]]
        if maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "DOWN":
        new_pos = [player_pos[0] + 1, player_pos[1]]
        if maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "LEFT":
        new_pos = [player_pos[0], player_pos[1] - 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "RIGHT":
        new_pos = [player_pos[0], player_pos[1] + 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos

    # Draw the maze and the player
    screen.fill(WHITE)
    draw_maze()
    draw_player()

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(10)

# Quit Pygame
pygame.quit()
sys.exit()
