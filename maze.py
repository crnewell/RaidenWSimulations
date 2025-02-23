import pygame
import sys
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Node:
    xpos: int
    ypos: int
    left_domain: int
    right_domain: int
    dir_to: Optional[str]  # Direction moved to reach this node
    children: List["Node"] = field(default_factory=list)



pygame.init()

# Constants
WINDOW_WIDTH = 1200  # Increased width to fit tree
WINDOW_HEIGHT = 600
GRID_SIZE = 15     # Number of rows and columns in the maze
CELL_SIZE = WINDOW_HEIGHT // GRID_SIZE  # Size of each cell
TREE_X_OFFSET = (WINDOW_HEIGHT+WINDOW_WIDTH)//2  # Offset for tree visualization
TREE_NODE_RADIUS = 10;

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Up move
GREEN = (0, 255, 0)  # Down move
YELLOW = (255, 255, 0)  # Left move
PURPLE = (128, 0, 128)  # Right move

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

#starting position
player_pos = [0, 1]  
root_pos = TREE_X_OFFSET
root = Node(xpos=root_pos, ypos=TREE_NODE_RADIUS, dir_to=None, left_domain=WINDOW_HEIGHT + TREE_NODE_RADIUS, right_domain= WINDOW_WIDTH - TREE_NODE_RADIUS)
current_node = root



screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("15x15 Maze")

def draw_maze():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = BLACK if maze[row][col] == 1 else WHITE
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_player():
    pygame.draw.rect(
        screen, RED, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )


def add_node(new_direction):
    global current_node
    # TODO: change the domain so that if a node has one child then it has full domain
    new_node = Node(
        xpos=(current_node.left_domain + current_node.xpos) // 2,
        ypos=current_node.ypos + TREE_NODE_RADIUS * 3, 
        dir_to= new_direction,  # Example for moving up
        left_domain= current_node.left_domain,
        right_domain=current_node.xpos)
    current_node.children.append(new_node)
    current_node = new_node




def draw_subtree(subtreeroot):
    # TODO CHANGE COLOR TO BE BASED ON DIRECTION TO
    # TODO: change color to show current node highlighted
    if subtreeroot.dir_to == "UP":
        color = BLUE
    elif subtreeroot.dir_to == "DOWN":
        color = GREEN
    elif subtreeroot.dir_to == "LEFT":
        color = YELLOW
    elif subtreeroot.dir_to == "RIGHT":
        color = PURPLE
    else:
        color = BLACK
    pygame.draw.circle(screen, color, (subtreeroot.xpos,subtreeroot.ypos), TREE_NODE_RADIUS)
    for node in  subtreeroot.children:
        draw_subtree(node)


def draw_tree():
    draw_subtree(root)




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
    # TODO: update to include going reverse in the tree
    if move_direction == "UP":
        new_pos = [player_pos[0] - 1, player_pos[1]]
        if maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
            add_node(move_direction)
    elif move_direction == "DOWN":
        new_pos = [player_pos[0] + 1, player_pos[1]]
        if maze[new_pos[0]][new_pos[1]] == 0:
            add_node(move_direction)
            player_pos = new_pos
    elif move_direction == "LEFT":
        new_pos = [player_pos[0], player_pos[1] - 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            add_node(move_direction)
            player_pos = new_pos
    elif move_direction == "RIGHT":
        new_pos = [player_pos[0], player_pos[1] + 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            add_node(move_direction)
            player_pos = new_pos

    # Drawing maze
    screen.fill(WHITE)
    draw_maze()
    draw_player()
    draw_tree();

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(10)

# end
pygame.quit()
sys.exit()
