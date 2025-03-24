import pygame
import sys
from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque

@dataclass
class Node:
    xpos: int
    ypos: int
    color: tuple[int, int, int]
    disp_xpos: int
    disp_ypos: int
    left_domain: int
    right_domain:int
    children: List["Node"] = field(default_factory=list)
    is_start: bool = False
    is_end: bool = False

@dataclass
class Tile:
    xpos: int
    ypos: int
    color: tuple[int, int, int]

pygame.init()

# Constants
WINDOW_WIDTH = 1200  # Increased width to fit tree
WINDOW_HEIGHT = 600
GRID_SIZE = 15     # Number of rows and columns in the maze
CELL_SIZE = WINDOW_HEIGHT // GRID_SIZE  # Size of each cell
TREE_X_OFFSET = (WINDOW_HEIGHT+WINDOW_WIDTH)//2  # Offset for tree visualization
TREE_NODE_RADIUS = 10
TREE_NODE_OFFSET = 6  # this is a multiplier to space the tree out vertically.
TREE_CURSOR_MULTIPLIER = 2  # this is a multiplier to get the size of the red square in the tree

# Button constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_X_BFS = WINDOW_WIDTH - BUTTON_WIDTH - 20
BUTTON_Y_BFS = WINDOW_HEIGHT - BUTTON_HEIGHT - 20
BUTTON_X_DFS = WINDOW_WIDTH - BUTTON_WIDTH - 20
BUTTON_Y_DFS = WINDOW_HEIGHT - BUTTON_HEIGHT - 80  # Position above BFS button
BUTTON_X_RESET = WINDOW_WIDTH - 2*BUTTON_WIDTH - 40 #position next to the bfs button
BUTTON_Y_RESET = WINDOW_HEIGHT - BUTTON_HEIGHT - 20
BUTTON_X_PAUSE = WINDOW_WIDTH - 3*BUTTON_WIDTH - 60 #position next to the reset button
BUTTON_Y_PAUSE = WINDOW_HEIGHT - BUTTON_HEIGHT - 20
BUTTON_X_STEP = WINDOW_WIDTH - 2*BUTTON_WIDTH -40
BUTTON_Y_STEP = WINDOW_HEIGHT - BUTTON_HEIGHT - 80

BUTTON_COLOR = (100, 100, 200)
BUTTON_HOVER_COLOR = (120, 120, 220)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_TEXT_BFS = "Solve BFS"
BUTTON_TEXT_DFS = "Solve DFS"
BUTTON_TEXT_RESET = "Reset Maze"
BUTTON_TEXT_PAUSE = "Pause/Play Solve"
BUTTON_TEXT_STEP = "Step Solve"


WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Up move
GREEN = (0, 255, 0)  # Down move
YELLOW = (255, 255, 0)  # Left move
PURPLE = (128, 0, 128)  # Right move
ORANGE = (255, 165, 0)  # For visited cells during BFS/DFS
LIGHT_BLUE = (173, 216, 230)  # For frontier cells

COLORS = {
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (173, 255, 47),   # Green Yellow
    (255, 105, 180),  # Hot Pink
    (75, 0, 130),     # Indigo
    (0, 128, 128),    # Teal
    (255, 20, 147),   # Deep Pink
    (138, 43, 226),   # Blue Violet
    (34, 139, 34),    # Forest Green
    (255, 140, 0),    # Dark Orange
    (186, 85, 211),   # Medium Orchid
    (70, 130, 180),   # Steel Blue
    (240, 128, 128),  # Light Coral
    (154, 205, 50),   # Yellow Green
    (199, 21, 133),   # Medium Violet Red
    (218, 112, 214),  # Orchid
    (0, 206, 209),    # Dark Turquoise
    (205, 92, 92),    # Indian Red
    (30, 144, 255),   # Dodger Blue
    (127, 255, 0),    # Chartreuse
    (233, 150, 122),  # Dark Salmon
    (139, 69, 19),    # Saddle Brown
    (210, 105, 30),   # Chocolate
    (255, 99, 71)     # Tomato
}

used_colors = set()

def get_unique_color():
    global COLORS
    if not COLORS:
        raise ValueError("No more unique colors available!")
    color = COLORS.pop()  # Remove and return a random color
    used_colors.add(color)
    return color

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
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1]
]

tile_map = {}  # is a dictionary that goes from a location to a tile, with it's color and corresponding tree node
node_map = {}  # is a dictionary that goes from a location to a node

# Define start and end positions
start_pos = [0, 1]
end_pos = [GRID_SIZE - 1, GRID_SIZE - 2]  # Based on the maze layout

# count number of neighbors for each location in the maze
neighbor_count = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if maze[i][j] == 0:
            # we have a valid empty space we check its top neighbor
            if i > 0 and maze[i-1][j] == 0:
                neighbor_count[i][j] += 1
            # now left neighbor
            if j > 0 and maze[i][j-1] == 0:
                neighbor_count[i][j] += 1
            # now below neighbor
            if i < GRID_SIZE - 1 and maze[i+1][j] == 0:
                neighbor_count[i][j] += 1
            # now right neighbor
            if j < GRID_SIZE - 1 and maze[i][j+1] == 0:
                neighbor_count[i][j] += 1

# printing neighbor_count out
for row in neighbor_count:
    print(row)

# starting position
player_pos = [0, 1]
original_player_pos = [0, 1]  # Store the original position for reset

def add_tile(xpos: int, ypos: int, new_Color: bool, color=None):
    global tile_map
    # check that we have not already added the tile
    if (xpos, ypos) in tile_map:
        return
    
    # check that are working with an open square
    if maze[xpos][ypos] != 0:
        raise ValueError("called add tile on nonvalid square")
    # we have a new tile, so we must add it
    # we get a new color if the previous node told us to
    if new_Color:
        color = get_unique_color()
    elif color == None:
        raise ValueError("did not recieve a color, or permission to create a new color")

    tile_map[(xpos, ypos)] = Tile(xpos, ypos, color)
    
    # now we check the neighbors and call each of them
    # if this current cell has more than 2 neighbors, then it's children will all get new colors
    new_color_child = (neighbor_count[xpos][ypos] > 2)

    # we have a valid empty space we check its top neighbor
    if xpos > 0 and maze[xpos-1][ypos] == 0:
        add_tile(xpos-1, ypos, new_color_child, color)
    # now left neighbor
    if ypos > 0 and maze[xpos][ypos-1] == 0:
        add_tile(xpos, ypos-1, new_color_child, color)
    # now below neighbor
    if xpos < GRID_SIZE - 1 and maze[xpos+1][ypos] == 0:
        add_tile(xpos+1, ypos, new_color_child, color)
    # now right neighbor
    if ypos < GRID_SIZE - 1 and maze[xpos][ypos+1] == 0:
        add_tile(xpos, ypos+1, new_color_child, color)

# starting preprocessing by making the first tile
# first empty tile is 0, 1
add_tile(0, 1, True)

def add_node(xpos: int, ypos: int, new_Node: bool, parent=None):
    global node_map
    # check that we haven't added this location yet
    if (xpos, ypos) in node_map:
        return
    # check that we are working with an open square
    if maze[xpos][ypos] != 0:
        raise ValueError("called add_node() on an nonvalid sqaure")
    
    # if we were told to make a new node at this location, we must add it, otherwise we use the parent node
    if new_Node:
        is_start = (xpos == start_pos[0] and ypos == start_pos[1])
        is_end = (xpos == end_pos[0] and ypos == end_pos[1])
        new_node = Node(xpos, ypos, tile_map[(xpos, ypos)].color, 0, 0, 0, 0, is_start=is_start, is_end=is_end)
        # add the child to the parent node (if it exists)
        if parent != None:
            parent.children.append(new_node)
        parent = new_node
    elif parent == None:
        raise ValueError("do not have a parent or permission to create a parent wihtin add_node")
    # add the correct node to the dictionary
    node_map[(xpos, ypos)] = parent
    print("added node with color", tile_map[(xpos, ypos)].color, "at location ", xpos, ", ", ypos)

    # if the current cell has more than 2 neighbors, then it's children will get new nodes in the tree
    new_node_child = neighbor_count[xpos][ypos] > 2

    # now we explore each of the children
    if xpos > 0 and maze[xpos-1][ypos] == 0:
        add_node(xpos-1, ypos, new_node_child, parent)
    # now left neighbor
    if ypos > 0 and maze[xpos][ypos-1] == 0:
        add_node(xpos, ypos-1, new_node_child, parent)
    # now below neighbor
    if xpos < GRID_SIZE - 1 and maze[xpos+1][ypos] == 0:
        add_node(xpos+1, ypos, new_node_child, parent)
    # now right neighbor
    if ypos < GRID_SIZE - 1 and maze[xpos][ypos+1] == 0:
        add_node(xpos, ypos+1, new_node_child, parent)

# now start preprocessing the first location for the tree
add_node(0, 1, True)

# now determine the display positions of the nodes in the tree
def update_pos(node, disp_x, disp_y, new_domain_left, new_domain_right):
    # update the current node with the correct values
    node.disp_xpos = disp_x
    node.disp_ypos = disp_y
    node.left_domain = new_domain_left
    node.right_domain = new_domain_right

    # update the children with the correct values (each node has 0 or 2 children)
    left = True
    for child in node.children:
        if left:
            # we are populating a left child
            update_pos(child, (disp_x + new_domain_left)//2, disp_y + TREE_NODE_RADIUS * TREE_NODE_OFFSET, new_domain_left, disp_x)
        else:
            # we are populating a right child
            update_pos(child, (disp_x + new_domain_right)//2, disp_y + TREE_NODE_RADIUS * TREE_NODE_OFFSET, disp_x, new_domain_right)
        left = False

# setting all of the locations of the tree
update_pos(node_map[(0, 1)], TREE_X_OFFSET, TREE_NODE_RADIUS * TREE_CURSOR_MULTIPLIER, WINDOW_HEIGHT + TREE_NODE_RADIUS, WINDOW_WIDTH - TREE_NODE_RADIUS)

# START DISPLAY
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("15x15 Maze Solver - BFS/DFS")
font = pygame.font.SysFont('Arial', 20)

# For BFS/DFS exploration visualization
visited_cells = set()  # Cells that have been explored
frontier_cells = set()  # Cells that are in the queue to be explored
path_cells = set()  # Cells that are part of the final solution

def draw_maze():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if maze[row][col] == 1:
                color = BLACK
            elif (row, col) in path_cells:
                # Part of the final solution path
                color = GREEN
            elif (row, col) in visited_cells:
                # Visited during BFS/DFS exploration
                color = GREY
            elif (row, col) in frontier_cells:
                # In the frontier (queue)
                color = LIGHT_BLUE
            elif (row, col) == (start_pos[0], start_pos[1]):
                # Start position
                color = BLUE
            elif (row, col) == (end_pos[0], end_pos[1]):
                # End position
                color = GREEN
            else:
                # Normal open cell
                color = tile_map[(row, col)].color
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_player():
    pygame.draw.rect(
        screen, RED, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )

def draw_subtree(subtreeroot):
    for node in subtreeroot.children:
        # Draw line connecting parent to child
        pygame.draw.line(screen, BLACK, 
                          (subtreeroot.disp_xpos, subtreeroot.disp_ypos), 
                          (node.disp_xpos, node.disp_ypos), 2)
        draw_subtree(node)

    # Draw the node as a circle or triangle depending on if it's a start or end node
    if subtreeroot.is_start or subtreeroot.is_end:
        # Draw a triangle for start/end nodes
        triangle_size = TREE_NODE_RADIUS * 1.5
        if subtreeroot.is_start:
            # Draw an upward-pointing triangle for start
            points = [
                (subtreeroot.disp_xpos, subtreeroot.disp_ypos - triangle_size),
                (subtreeroot.disp_xpos - triangle_size, subtreeroot.disp_ypos + triangle_size/2),
                (subtreeroot.disp_xpos + triangle_size, subtreeroot.disp_ypos + triangle_size/2)
            ]
            pygame.draw.polygon(screen, BLUE, points)
        else:
            # Draw a downward-pointing triangle for end
            points = [
                (subtreeroot.disp_xpos, subtreeroot.disp_ypos + triangle_size),
                (subtreeroot.disp_xpos - triangle_size, subtreeroot.disp_ypos - triangle_size/2),
                (subtreeroot.disp_xpos + triangle_size, subtreeroot.disp_ypos - triangle_size/2)
            ]
            pygame.draw.polygon(screen, GREEN, points)
    else:
        # Draw regular nodes as circles
        pygame.draw.circle(screen, subtreeroot.color, (subtreeroot.disp_xpos, subtreeroot.disp_ypos), TREE_NODE_RADIUS)

def draw_tree():
    # draw a square for the current node
    if (player_pos[0], player_pos[1]) in node_map:
        tree_loc_x = node_map[(player_pos[0], player_pos[1])].disp_xpos
        tree_loc_y = node_map[(player_pos[0], player_pos[1])].disp_ypos
        pygame.draw.rect(screen, RED, (tree_loc_x - TREE_NODE_RADIUS * TREE_CURSOR_MULTIPLIER, 
                                      tree_loc_y - TREE_NODE_RADIUS * TREE_CURSOR_MULTIPLIER, 
                                      TREE_NODE_RADIUS * 2 * TREE_CURSOR_MULTIPLIER, 
                                      TREE_NODE_RADIUS * 2 * TREE_CURSOR_MULTIPLIER))
    draw_subtree(node_map[(0, 1)])

def draw_button(button_x, button_y, button_text, hover=False):
    color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, (button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT), border_radius=5)
    
    text_surface = font.render(button_text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(button_x + BUTTON_WIDTH // 2, button_y + BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def is_button_hovered(pos, button_x, button_y):
    x, y = pos
    return button_x <= x <= button_x + BUTTON_WIDTH and button_y <= y <= button_y + BUTTON_HEIGHT

# Function for BFS - Modified to return exploration history
def find_path_bfs():
    queue = deque([(start_pos[0], start_pos[1], [])]) 
    visited = set([(start_pos[0], start_pos[1])])
    
    exploration_history = []  
    
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    dir_names = ["UP", "RIGHT", "DOWN", "LEFT"]
    
    # Add initial state
    exploration_history.append((set(visited), set(), (start_pos[0], start_pos[1])))
    
    while queue:
        row, col, path = queue.popleft()
        
        # Check if we reached the exit
        if row == end_pos[0] and col == end_pos[1]:
            # Add the final path to the history
            path_set = set()
            current_pos = (start_pos[0], start_pos[1])
            path_set.add(current_pos)
            
            for move in path:
                if move == "UP":
                    current_pos = (current_pos[0] - 1, current_pos[1])
                elif move == "RIGHT":
                    current_pos = (current_pos[0], current_pos[1] + 1)
                elif move == "DOWN":
                    current_pos = (current_pos[0] + 1, current_pos[1])
                elif move == "LEFT":
                    current_pos = (current_pos[0], current_pos[1] - 1)
                path_set.add(current_pos)
            
            return path, exploration_history, path_set
        
        # Add neighbors to the frontier
        frontier = set()
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE and 
                maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
                frontier.add((new_row, new_col))
        
        # Record current state
        if frontier:
            exploration_history.append((set(visited), frontier, (row, col)))
        
        # Try all four directions
        for i, (dr, dc) in enumerate(directions):
            new_row, new_col = row + dr, col + dc
            
            # Check if the new position is valid and not visited
            if (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE and 
                maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
                queue.append((new_row, new_col, path + [dir_names[i]]))
                visited.add((new_row, new_col))
    
    return [], exploration_history, set()  # No path found

# Function for DFS - Modified to return exploration history
def find_path_dfs():
    stack = [(start_pos[0], start_pos[1], [])]
    visited = set([(start_pos[0], start_pos[1])])
    
    exploration_history = []
    
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    dir_names = ["UP", "RIGHT", "DOWN", "LEFT"]
    
    # Add initial state
    exploration_history.append((set(visited), set(), (start_pos[0], start_pos[1])))
    
    while stack:
        row, col, path = stack.pop()  # DFS uses a stack (pop from end)
        
        # Check if we reached the exit
        if row == end_pos[0] and col == end_pos[1]:
            # Add the final path to the history
            path_set = set()
            current_pos = (start_pos[0], start_pos[1])
            path_set.add(current_pos)
            
            for move in path:
                if move == "UP":
                    current_pos = (current_pos[0] - 1, current_pos[1])
                elif move == "RIGHT":
                    current_pos = (current_pos[0], current_pos[1] + 1)
                elif move == "DOWN":
                    current_pos = (current_pos[0] + 1, current_pos[1])
                elif move == "LEFT":
                    current_pos = (current_pos[0], current_pos[1] - 1)
                path_set.add(current_pos)
            
            return path, exploration_history, path_set
        
        # Add neighbors to the frontier
        frontier = set()
        valid_moves = []
        
        # Check all four directions
        for i, (dr, dc) in enumerate(directions):
            new_row, new_col = row + dr, col + dc
            
            # Check if the new position is valid and not visited
            if (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE and 
                maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
                frontier.add((new_row, new_col))
                valid_moves.append((new_row, new_col, path + [dir_names[i]]))
        
        # Record current state
        if frontier:
            exploration_history.append((set(visited), frontier, (row, col)))
        
        # Add valid moves to the stack (in reverse order to prioritize UP, RIGHT, DOWN, LEFT)
        for move in reversed(valid_moves):
            new_row, new_col, new_path = move
            stack.append((new_row, new_col, new_path))
            visited.add((new_row, new_col))
    
    return [], exploration_history, set()  # No path found

# Global variables for auto-solving
solution_path = []
solving_active = False
current_step = 0
exploration_history = []
exploration_step = 0
final_path_set = set()
in_exploration_phase = False
current_algorithm = None  # To track whether we're using BFS or DFS

# Main loop
running = True
clock = pygame.time.Clock()
move_direction = None
button_hover_bfs = False
button_hover_dfs = False
button_hover_reset = False
button_hover_pause = False
solution_paused = False
button_hover_step = False

while running:
    mouse_pos = pygame.mouse.get_pos()
    button_hover_bfs = is_button_hovered(mouse_pos, BUTTON_X_BFS, BUTTON_Y_BFS)
    button_hover_dfs = is_button_hovered(mouse_pos, BUTTON_X_DFS, BUTTON_Y_DFS)
    button_hover_reset = is_button_hovered(mouse_pos, BUTTON_X_RESET, BUTTON_Y_RESET)
    button_hover_pause = is_button_hovered(mouse_pos, BUTTON_X_PAUSE, BUTTON_Y_PAUSE)
    button_hover_step = is_button_hovered(mouse_pos, BUTTON_X_STEP, BUTTON_Y_STEP)
    
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_hover_bfs:
                # Reset and start BFS exploration
                player_pos = original_player_pos.copy()
                solution_path, exploration_history, final_path_set = find_path_bfs()
                solving_active = True
                current_step = 0
                exploration_step = 0
                visited_cells.clear()
                frontier_cells.clear()
                path_cells.clear()
                in_exploration_phase = True
                current_algorithm = "BFS"
                print("BFS Solution path:", solution_path)
                print(f"BFS exploration: {len(exploration_history)} steps")
            elif button_hover_dfs:
                # Reset and start DFS exploration
                player_pos = original_player_pos.copy()
                solution_path, exploration_history, final_path_set = find_path_dfs()
                solving_active = True
                current_step = 0
                exploration_step = 0
                visited_cells.clear()
                frontier_cells.clear()
                path_cells.clear()
                in_exploration_phase = True
                current_algorithm = "DFS"
                print("DFS Solution path:", solution_path)
                print(f"DFS exploration: {len(exploration_history)} steps")
            elif button_hover_reset:
                print("MAZE RESET PRESSED")
                # Reset 
                player_pos = original_player_pos.copy()
                solving_active = False
                current_step = 0
                exploration_step = 0
                visited_cells.clear()
                frontier_cells.clear()
                path_cells.clear()
                move_direction = None
                solution_paused = False
            elif button_hover_pause:
                #pause the exploration
                print("SOLUTION PAUSE PRESSED")
                solution_paused = not solution_paused
            elif button_hover_step:
                print("SOLUTION STEP PRESSED")
                #TODO: step the solution by one.



    
    # Handle exploration visualization
    if solving_active:
        if not solution_paused and in_exploration_phase and exploration_step < len(exploration_history):
            # Update visualization states
            visited_set, frontier_set, current_pos = exploration_history[exploration_step]
            visited_cells = visited_set
            frontier_cells = frontier_set
            player_pos = [current_pos[0], current_pos[1]]
            exploration_step += 1
            pygame.time.delay(200)  # Slow down the visualization
            
            # Check if exploration is complete
            if exploration_step >= len(exploration_history):
                in_exploration_phase = False
                # Reset player position to start for the solution path
                player_pos = original_player_pos.copy()
                # Mark the final path cells
                path_cells = final_path_set
                pygame.time.delay(500)  # Pause before starting the solution path
        
        elif not solution_paused and not in_exploration_phase and current_step < len(solution_path):
            # Now follow the solution path
            move_direction = solution_path[current_step]
            current_step += 1
            pygame.time.delay(200)  # Slow down the automatic moves
            
            if current_step >= len(solution_path):
                solving_active = False
    
    # Handle player movement
    if move_direction == "UP":
        new_pos = [player_pos[0] - 1, player_pos[1]]
        if 0 <= new_pos[0] < GRID_SIZE and maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "DOWN":
        new_pos = [player_pos[0] + 1, player_pos[1]]
        if 0 <= new_pos[0] < GRID_SIZE and maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "LEFT":
        new_pos = [player_pos[0], player_pos[1] - 1]
        if 0 <= new_pos[1] < GRID_SIZE and maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    elif move_direction == "RIGHT":
        new_pos = [player_pos[0], player_pos[1] + 1]
        if 0 <= new_pos[1] < GRID_SIZE and maze[new_pos[0]][new_pos[1]] == 0:
            player_pos = new_pos
    
    # Drawing everything 
    # Drawing everything
    screen.fill(WHITE)
    draw_maze()
    draw_player()
    draw_tree()
    # draw_button(WINDOW_WIDTH-200, WINDOW_HEIGHT-100, "SOLVE BFS", button_hover_bfs )
    draw_button(BUTTON_X_BFS, BUTTON_Y_BFS, BUTTON_TEXT_BFS, button_hover_bfs)
    draw_button(BUTTON_X_DFS, BUTTON_Y_DFS, BUTTON_TEXT_DFS, button_hover_dfs)
    draw_button(BUTTON_X_RESET, BUTTON_Y_RESET, BUTTON_TEXT_RESET, button_hover_reset)
    draw_button(BUTTON_X_PAUSE, BUTTON_Y_PAUSE, BUTTON_TEXT_PAUSE, button_hover_pause)
    draw_button(BUTTON_X_STEP, BUTTON_Y_STEP, BUTTON_TEXT_STEP, button_hover_step)

    # draw_button(button_hover_dfs)

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(10)

# end
pygame.quit()
sys.exit()