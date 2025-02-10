import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 500  # Window size (square)
GRID_SIZE = 5      # Number of rows and columns in the maze
CELL_SIZE = WINDOW_SIZE // GRID_SIZE  # Size of each cell

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Maze array (1s are walls, 0s are paths)
maze = [
    [1, 0, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1]
]

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("5x5 Maze")

# Function to draw the maze
def draw_maze():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = BLACK if maze[row][col] == 1 else WHITE
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the maze
    screen.fill(WHITE)
    draw_maze()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
