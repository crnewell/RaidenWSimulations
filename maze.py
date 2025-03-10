import pygame
import sys
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Node:
    xpos: int
    ypos: int
    # dir_to: Optional[str]  # Direction moved to reach this node
    # parent: Optional["Node"] = None
    color: tuple[int, int, int]
    disp_xpos: int
    disp_ypos: int
    left_domain: int
    right_domain:int
    children: List["Node"] = field(default_factory=list)

@dataclass
class Tile:
    xpos: int
    ypos: int
    color: tuple[int, int, int]
    # tree_node: Node



pygame.init()

# Constants
WINDOW_WIDTH = 1200  # Increased width to fit tree
WINDOW_HEIGHT = 600
GRID_SIZE = 15     # Number of rows and columns in the maze
CELL_SIZE = WINDOW_HEIGHT // GRID_SIZE  # Size of each cell
TREE_X_OFFSET = (WINDOW_HEIGHT+WINDOW_WIDTH)//2  # Offset for tree visualization
TREE_NODE_RADIUS = 10;
TREE_NODE_OFFSET = 10; # this is a multiplier to space the tree out vertically.

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Up move
GREEN = (0, 255, 0)  # Down move
YELLOW = (255, 255, 0)  # Left move
PURPLE = (128, 0, 128)  # Right move

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

tile_map ={} #is a dictionary that goes from a location to a tile, with it's color and corresponding tree node
node_map = {} #is a dictionary that goes from a location to a node

# initiate preprocessing:
# create the tree according to the graph, 
#  have a matrix of pointers in the shape of the maze to the nodes corresponding to the tree
# color the maze with corresponding colors to the tree
# generate the tree using the maze, with a different type of node for branching and non-branching locations in the maze.


# count number of neighbors for each location in the maze
neighbor_count = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if maze[i][j] == 0:
            # we have a valid empty space we check its top neighbor
            if i > 0 and maze[i-1][ j] == 0:
                neighbor_count[i][ j] += 1
            # now left neighbor
            if j > 0 and maze[i][ j-1] == 0:
                neighbor_count[i][ j] +=1
            # now below neighbor
            if i < GRID_SIZE - 1 and maze[i+1][ j] == 0:
                neighbor_count[i][ j] += 1
            #now right neighbor
            if j < GRID_SIZE -1 and maze[i][ j+1] == 0:
                neighbor_count[i][ j] +=1


#printing neighbor_count out

for row in neighbor_count:
    print(row)


#starting position
player_pos = [0, 1]  
# root_pos = TREE_X_OFFSET
# root = Node(xpos=root_pos, ypos=TREE_NODE_RADIUS, dir_to=None, left_domain=WINDOW_HEIGHT + TREE_NODE_RADIUS, right_domain= WINDOW_WIDTH - TREE_NODE_RADIUS)
# current_node = root

def add_tile(xpos:int, ypos:int, new_Color: bool, color = None):
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
    # print("added tile with color", color, "at location ", xpos, ", ", ypos)
    
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
    #now right neighbor
    if ypos < GRID_SIZE -1 and maze[xpos][ypos+1] == 0:
        add_tile(xpos, ypos+1, new_color_child, color)

# starting preprocessing by making the first tile
# first empty tile is 0, 1
add_tile(0, 1, True)

def add_node(xpos:int, ypos:int, new_Node: bool, parent = None):
    global node_map
    #check that we haven't added this location yet
    if (xpos, ypos) in node_map:
        return
    #check that we are working with an open square
    if maze[xpos][ypos] != 0:
        raise ValueError("called add_node() on an nonvalid sqaure")
    
    # if we were told to make a new node at this location, we must add it, otherwise we use the parent node
    if new_Node:
        new_node = Node(xpos, ypos, tile_map[(xpos, ypos)].color, 0, 0, 0, 0)
        # add the child to the parent node (if it exists)
        if parent != None:
            parent.children.append(new_node)
        parent = new_node
    elif parent == None:
        raise ValueError("do not have a parent or permission to create a parent wihtin add_node")
    # add the correct node to the dictionary
    node_map[(xpos, ypos)] = parent
    print("added node with color", tile_map[(xpos, ypos)].color, "at location ", xpos, ", ", ypos)

    #if the current cell has more than 2 neighbors, then it's children will get new nodes in the tree
    new_node_child = neighbor_count[xpos][ypos] > 2

    #now we explore each of the children

    if xpos > 0 and maze[xpos-1][ypos] == 0:
        add_node(xpos-1, ypos, new_node_child, parent)
    # now left neighbor
    if ypos > 0 and maze[xpos][ypos-1] == 0:
        add_node(xpos, ypos-1, new_node_child, parent)
    # now below neighbor
    if xpos < GRID_SIZE - 1 and maze[xpos+1][ypos] == 0:
        add_node(xpos+1, ypos, new_node_child, parent)
    #now right neighbor
    if ypos < GRID_SIZE -1 and maze[xpos][ypos+1] == 0:
        add_node(xpos, ypos+1, new_node_child, parent)

#now start preprocessing the first location for the tree
add_node(0,1, True)

#now determine the display positions of the nodes in the tree
def update_pos(node, disp_x, disp_y, new_domain_left, new_domain_right):
    # update the current node with the correct values
    node.disp_xpos = disp_x
    node.disp_ypos = disp_y
    node.left_domain = new_domain_left
    node.right_domain = new_domain_right

    #update the children with the correct values (each node has 0 or 2 children)
    left = True
    for child in node.children:
        if left:
            # we are populating a left child
            update_pos(child, (disp_x + new_domain_left)//2, disp_y + TREE_NODE_RADIUS * TREE_NODE_OFFSET, new_domain_left, disp_x)
        else:
            #we are populating a right child
            update_pos(child, (disp_x +new_domain_right)//2, disp_y + TREE_NODE_RADIUS *TREE_NODE_OFFSET, disp_x, new_domain_right)
        left = False


# setting all of the locations of the tree
update_pos(node_map[(0,1)], TREE_X_OFFSET, TREE_NODE_RADIUS, WINDOW_HEIGHT + TREE_NODE_RADIUS, WINDOW_WIDTH - TREE_NODE_RADIUS)
















# printing the tree post order (node, left, right)
def print_node(root):
    print("Node with color " , root.color, " has " , len(root.children), " many children")
    for child in root.children:
        print_node(child)

print_node(node_map[(0, 1)])

















screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("15x15 Maze")

def draw_maze():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = BLACK if maze[row][col] == 1 else tile_map[(row, col)].color
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_player():
    pygame.draw.rect(
        screen, RED, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )


# def add_node(new_direction):
#     global current_node
#     # check that a node does need to be added
#     if (new_direction == "RIGHT" and current_node.dir_to == "LEFT") or (new_direction == "LEFT" and current_node.dir_to == "RIGHT") or (new_direction == "DOWN" and current_node.dir_to == "UP") or (new_direction == "UP" and current_node.dir_to == "DOWN"):
#         current_node = current_node.parent
#     else:
#         # TODO: change the domain so that if a node has one child then it has full domain
#         # adding a child on the left
#         if len(current_node.children)== 0:
#             new_node = Node(
#                 xpos=(current_node.left_domain + current_node.xpos) // 2,
#                 ypos=current_node.ypos + TREE_NODE_RADIUS * 3, 
#                 dir_to= new_direction,
#                 left_domain= current_node.left_domain,
#                 right_domain=current_node.xpos,
#                 parent= current_node)
#         #adding a child on the right
#         else:
#             new_node = Node(
#                 xpos=(current_node.right_domain + current_node.xpos) // 2,
#                 ypos=current_node.ypos + TREE_NODE_RADIUS * 3, 
#                 dir_to= new_direction,
#                 left_domain= current_node.xpos,
#                 right_domain=current_node.right_domain,
#                 parent= current_node)
#         current_node.children.append(new_node)
#         current_node = new_node


def draw_subtree(subtreeroot):
    # TODO: change color to show current node highlighted
    pygame.draw.circle(screen, subtreeroot.color, (subtreeroot.disp_xpos, subtreeroot.disp_ypos), TREE_NODE_RADIUS)

    
    # pygame.draw.circle(screen, color, (subtreeroot.xpos,subtreeroot.ypos), TREE_NODE_RADIUS)
    for node in  subtreeroot.children:
        draw_subtree(node)


def draw_tree():
    draw_subtree(node_map[(0, 1)])




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
            # add_node(move_direction)
    elif move_direction == "DOWN":
        new_pos = [player_pos[0] + 1, player_pos[1]]
        if maze[new_pos[0]][new_pos[1]] == 0:
            # add_node(move_direction)
            player_pos = new_pos
    elif move_direction == "LEFT":
        new_pos = [player_pos[0], player_pos[1] - 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            # add_node(move_direction)
            player_pos = new_pos
    elif move_direction == "RIGHT":
        new_pos = [player_pos[0], player_pos[1] + 1]
        if maze[new_pos[0]][new_pos[1]] == 0:
            # add_node(move_direction)
            player_pos = new_pos
    print("player at tile: ", player_pos[0], player_pos[1], "tile color of ", tile_map[(player_pos[0], player_pos[1])].color, " and tree color of ", tile_map[(player_pos[0], player_pos[1])].color)
    # Drawing maze
    screen.fill(WHITE)
    draw_maze()
    draw_player()
    draw_tree()

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(10)

# end
pygame.quit()
sys.exit()
