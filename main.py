from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import sys
import pygame
import numpy as np
from PyQt5.QtGui import QImage, QPainter
from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque



class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        pygame.init()
        self.surface = pygame.Surface((200, 100))
        self.circle_x = 100
        self.circle_speed = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(16)

    def update_pygame(self):
        self.surface.fill((0, 0, 0))
        pygame.draw.circle(self.surface, (255, 0, 0), (self.circle_x, 50), 10)
        self.circle_x += self.circle_speed
        if self.circle_x >= 200 or self.circle_x <= 0:
            self.circle_speed *= -1

        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        image = pygame.surfarray.array3d(self.surface)
        image = np.rot90(image, k=3)
        image = np.flip(image, axis=1)
        height, width, _ = image.shape
        bytes_per_line = 3 * width
        qimage = QImage(image.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)

        qp.drawImage(0, 0, qimage)

class PyGameQtWidget(QWidget):

    def __init__(self, parent=None, width=200, height=100):
        super().__init__(parent)
        self.setFixedSize(width, height)
        if not pygame.get_init():
            pygame.init()

        self.surface = pygame.Surface((width, height))
        self.pygame_events = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)  # ~60 FPS

    def update_simulation(self):
        self.process_pygame_events()
        self.surface.fill((0, 0, 0))
        self.update()

    def process_pygame_events(self):
        for event in self.pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                pass
            elif event.type == pygame.MOUSEMOTION:
                pass

        self.pygame_events = []

    def paintEvent(self, event):
        qp = QPainter(self)
        image = pygame.surfarray.array3d(self.surface)
        image = np.rot90(image, k=3)
        image = np.flip(image, axis=1)
        height, width, _ = image.shape
        bytes_per_line = 3 * width
        qimage = QImage(image.tobytes(), width, height, bytes_per_line, QImage.Format_RGB888)
        qp.drawImage(0, 0, qimage)

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        pygame_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': (x, y), 'button': event.button()}
        )
        self.pygame_events.append(pygame_event)

    def mouseReleaseEvent(self, event):
        x, y = event.x(), event.y()
        pygame_event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {'pos': (x, y), 'button': event.button()}
        )
        self.pygame_events.append(pygame_event)

    def mouseMoveEvent(self, event):
        x, y = event.x(), event.y()
        pygame_event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {'pos': (x, y), 'buttons': self.get_button_state()}
        )
        self.pygame_events.append(pygame_event)

    def get_button_state(self):
        return (0, 0, 0)


class ClickableSimulation(PyGameQtWidget):

    def __init__(self, parent=None, width=200, height=100):
        super().__init__(parent, width, height)

        self.buttons = [
            {
                'rect': pygame.Rect(20, 20, 70, 30),
                'color': (255, 0, 0),
                'text': 'Red',
                'action': self.set_background_red
            },
            {
                'rect': pygame.Rect(110, 20, 70, 30),
                'color': (0, 0, 255),
                'text': 'Blue',
                'action': self.set_background_blue
            },
            {
                'rect': pygame.Rect(65, 60, 70, 30),
                'color': (0, 255, 0),
                'text': 'Green',
                'action': self.set_background_green
            }
        ]

        self.font = pygame.font.SysFont('Arial', 20)
        self.bg_color = (50, 50, 50)

    def update_simulation(self):
        self.process_pygame_events()
        self.surface.fill(self.bg_color)

        for button in self.buttons:
            pygame.draw.rect(self.surface, button['color'], button['rect'])
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.surface.blit(text, text_rect)

        self.update()

    def process_pygame_events(self):
        for event in self.pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for button clicks
                for button in self.buttons:
                    if button['rect'].collidepoint(event.pos):
                        button['action']()
        self.pygame_events = []

    def set_background_red(self):
        self.bg_color = (100, 30, 30)

    def set_background_blue(self):
        self.bg_color = (30, 30, 100)

    def set_background_green(self):
        self.bg_color = (30, 100, 30)

class MazeRunner(PyGameQtWidget):
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

    # Constants
    WINDOW_WIDTH = 1200  # Increased width to fit tree
    WINDOW_HEIGHT = 400
    GRID_SIZE = 15     # Number of rows and columns in the maze





    def __init__(self, parent=None, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):    
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
        
        super().__init__(parent, width, height)
        WINDOW_WIDTH = width
        WINDOW_HEIGHT = height
        self.GRID_SIZE = 15     # Number of rows and columns in the maze
        self.CELL_SIZE = WINDOW_HEIGHT // self.GRID_SIZE  # Size of each cell
        TREE_X_OFFSET = (WINDOW_HEIGHT+WINDOW_WIDTH)//2  # Offset for tree visualization
        self.TREE_NODE_RADIUS = 10
        TREE_NODE_OFFSET = 6  # this is a multiplier to space the tree out vertically.
        self.TREE_CURSOR_MULTIPLIER = 2  # this is a multiplier to get the size of the red square in the tree
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
        BUTTON_TEXT_BFS = 'Solve BFS'
        BUTTON_TEXT_DFS = 'Solve DFS'
        BUTTON_TEXT_RESET = 'Reset Maze'
        BUTTON_TEXT_PAUSE = 'Pause/Play Solve'
        BUTTON_TEXT_STEP = 'Step Solve'
        self.buttons = [
            {
                'rect': pygame.Rect(BUTTON_X_BFS, BUTTON_Y_BFS, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_BFS,
                'action': self.start_bfs
            },
            {
                'rect': pygame.Rect(BUTTON_X_DFS, BUTTON_Y_DFS, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_DFS,
                'action': self.start_dfs
            },
            {
                'rect': pygame.Rect(BUTTON_X_RESET, BUTTON_Y_RESET, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_RESET,
                'action': self.reset
            },
            {
                'rect': pygame.Rect(BUTTON_X_PAUSE, BUTTON_Y_PAUSE, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_PAUSE,
                'action': self.set_background_green
            },
            {
                'rect': pygame.Rect(BUTTON_X_STEP, BUTTON_Y_STEP, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_STEP,
                'action': self.set_background_green
            }
        ]

        self.font = pygame.font.SysFont('Arial', 20)
        self.bg_color = (50, 50, 50)
        # This is where all the information goes that the simulation will need
        self.WHITE = (255, 255, 255)
        self.GREY = (128, 128, 128)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)  # Up move
        self.GREEN = (0, 255, 0)  # Down move
        self.YELLOW = (255, 255, 0)  # Left move
        self.PURPLE = (128, 0, 128)  # Right move
        self.ORANGE = (255, 165, 0)  # For visited cells during BFS/DFS
        self.LIGHT_BLUE = (173, 216, 230)  # For frontier cells

        self.COLORS = {
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

        self.used_colors = set()

        def get_unique_color():
            if not self.COLORS:
                raise ValueError("No more unique colors available!")
            color = self.COLORS.pop()  # Remove and return a random color
            self.used_colors.add(color)
            return color
        
        # Maze array (1s are walls, 0s are paths)
        self.maze = [
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
        
        self.tile_map = {}  # is a dictionary that goes from a location to a tile, with it's color and corresponding tree node
        self.node_map = {}  # is a dictionary that goes from a location to a node

        # Define start and end positions
        self.start_pos = [0, 1]
        self.end_pos = [self.GRID_SIZE - 1, self.GRID_SIZE - 2]  # Based on the maze layout

        # count number of neighbors for each location in the maze
        self.neighbor_count = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.maze[i][j] == 0:
                    # we have a valid empty space we check its top neighbor
                    if i > 0 and self.maze[i-1][j] == 0:
                        self.neighbor_count[i][j] += 1
                    # now left neighbor
                    if j > 0 and self.maze[i][j-1] == 0:
                        self.neighbor_count[i][j] += 1
                    # now below neighbor
                    if i < self.GRID_SIZE - 1 and self.maze[i+1][j] == 0:
                        self.neighbor_count[i][j] += 1
                    # now right neighbor
                    if j < self.GRID_SIZE - 1 and self.maze[i][j+1] == 0:
                        self.neighbor_count[i][j] += 1

        # starting position
        self.player_pos = [0, 1]
        self.original_player_pos = [0, 1]  # Store the original position for reset
        
        def add_tile(xpos: int, ypos: int, new_Color: bool, color=None):
            # check that we have not already added the tile
            if (xpos, ypos) in self.tile_map:
                return
            
            # check that are working with an open square
            if self.maze[xpos][ypos] != 0:
                raise ValueError("called add tile on nonvalid square")
            # we have a new tile, so we must add it
            # we get a new color if the previous node told us to
            if new_Color:
                color = get_unique_color()
            elif color == None:
                raise ValueError("did not recieve a color, or permission to create a new color")

            self.tile_map[(xpos, ypos)] = Tile(xpos, ypos, color)
            
            # now we check the neighbors and call each of them
            # if this current cell has more than 2 neighbors, then it's children will all get new colors
            new_color_child = (self.neighbor_count[xpos][ypos] > 2)

            # we have a valid empty space we check its top neighbor
            if xpos > 0 and self.maze[xpos-1][ypos] == 0:
                add_tile(xpos-1, ypos, new_color_child, color)
            # now left neighbor
            if ypos > 0 and self.maze[xpos][ypos-1] == 0:
                add_tile(xpos, ypos-1, new_color_child, color)
            # now below neighbor
            if xpos < self.GRID_SIZE - 1 and self.maze[xpos+1][ypos] == 0:
                add_tile(xpos+1, ypos, new_color_child, color)
            # now right neighbor
            if ypos < self.GRID_SIZE - 1 and self.maze[xpos][ypos+1] == 0:
                add_tile(xpos, ypos+1, new_color_child, color)

        # starting preprocessing by making the first tile
        # first empty tile is 0, 1
        add_tile(0, 1, True)


        def add_node(xpos: int, ypos: int, new_Node: bool, parent=None):
            # check that we haven't added this location yet
            if (xpos, ypos) in self.node_map:
                return
            # check that we are working with an open square
            if self.maze[xpos][ypos] != 0:
                raise ValueError("called add_node() on an nonvalid sqaure")
            
            # if we were told to make a new node at this location, we must add it, otherwise we use the parent node
            if new_Node:
                is_start = (xpos == self.start_pos[0] and ypos == self.start_pos[1])
                is_end = (xpos == self.end_pos[0] and ypos == self.end_pos[1])
                new_node = Node(xpos, ypos, self.tile_map[(xpos, ypos)].color, 0, 0, 0, 0, is_start=is_start, is_end=is_end)
                # add the child to the parent node (if it exists)
                if parent != None:
                    parent.children.append(new_node)
                parent = new_node
            elif parent == None:
                raise ValueError("do not have a parent or permission to create a parent wihtin add_node")
            # add the correct node to the dictionary
            self.node_map[(xpos, ypos)] = parent
            print("added node with color", self.tile_map[(xpos, ypos)].color, "at location ", xpos, ", ", ypos)

            # if the current cell has more than 2 neighbors, then it's children will get new nodes in the tree
            new_node_child = self.neighbor_count[xpos][ypos] > 2

            # now we explore each of the children
            if xpos > 0 and self.maze[xpos-1][ypos] == 0:
                add_node(xpos-1, ypos, new_node_child, parent)
            # now left neighbor
            if ypos > 0 and self.maze[xpos][ypos-1] == 0:
                add_node(xpos, ypos-1, new_node_child, parent)
            # now below neighbor
            if xpos < self.GRID_SIZE - 1 and self.maze[xpos+1][ypos] == 0:
                add_node(xpos+1, ypos, new_node_child, parent)
            # now right neighbor
            if ypos < self.GRID_SIZE - 1 and self.maze[xpos][ypos+1] == 0:
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
                    update_pos(child, (disp_x + new_domain_left)//2, disp_y + self.TREE_NODE_RADIUS * TREE_NODE_OFFSET, new_domain_left, disp_x)
                else:
                    # we are populating a right child
                    update_pos(child, (disp_x + new_domain_right)//2, disp_y + self.TREE_NODE_RADIUS * TREE_NODE_OFFSET, disp_x, new_domain_right)
                left = False

        # setting all of the locations of the tree
        update_pos(self.node_map[(0, 1)], TREE_X_OFFSET, self.TREE_NODE_RADIUS * self.TREE_CURSOR_MULTIPLIER, WINDOW_HEIGHT + self.TREE_NODE_RADIUS, WINDOW_WIDTH - self.TREE_NODE_RADIUS)

        # For BFS/DFS exploration visualization
        self.visited_cells = set()  # Cells that have been explored
        self.frontier_cells = set()  # Cells that are in the queue to be explored
        self.path_cells = set()  # Cells that are part of the final solution

        # Global variables for auto-solving
        self.solution_path = []
        self.solving_active = False
        self.current_step = 0
        self.exploration_history = []
        self.exploration_step = 0
        self.final_path_set = set()
        self.in_exploration_phase = False
        self.current_algorithm = None  # To track whether we're using BFS or DFS

        # Main loop
        self.running = True
        self.clock = pygame.time.Clock()
        self.move_direction = None
        self.solution_paused = False
        self.solution_step = False


    def draw_maze(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if self.maze[row][col] == 1:
                    color = self.BLACK
                elif (row, col) in self.path_cells:
                    # Part of the final solution path
                    color = self.GREEN
                elif (row, col) in self.visited_cells:
                    # Visited during BFS/DFS exploration
                    color = self.GREY
                elif (row, col) in self.frontier_cells:
                    # In the frontier (queue)
                    color = self.LIGHT_BLUE
                elif (row, col) == (self.start_pos[0], self.start_pos[1]):
                    # Start position
                    color = self.BLUE
                elif (row, col) == (self.end_pos[0], self.end_pos[1]):
                    # End position
                    color = self.GREEN
                else:
                    # Normal open cell
                    color = self.tile_map[(row, col)].color
                pygame.draw.rect(self.surface, color, (col * self.CELL_SIZE, row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE))

    def draw_player(self):
        pygame.draw.rect(
            self.surface, self.RED, (self.player_pos[1] * self.CELL_SIZE, self.player_pos[0] * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
        )


    def draw_tree(self):
        def draw_subtree(subtreeroot):
            for node in subtreeroot.children:
                # Draw line connecting parent to child
                pygame.draw.line(self.surface, self.BLACK, 
                                (subtreeroot.disp_xpos, subtreeroot.disp_ypos), 
                                (node.disp_xpos, node.disp_ypos), 2)
                draw_subtree(node)

            # Draw the node as a circle or triangle depending on if it's a start or end node
            if subtreeroot.is_start or subtreeroot.is_end:
                # Draw a triangle for start/end nodes
                triangle_size = self.TREE_NODE_RADIUS * 1.5
                if subtreeroot.is_start:
                    # Draw an upward-pointing triangle for start
                    points = [
                        (subtreeroot.disp_xpos, subtreeroot.disp_ypos - triangle_size),
                        (subtreeroot.disp_xpos - triangle_size, subtreeroot.disp_ypos + triangle_size/2),
                        (subtreeroot.disp_xpos + triangle_size, subtreeroot.disp_ypos + triangle_size/2)
                    ]
                    pygame.draw.polygon(self.surface, self.BLUE, points)
                else:
                    # Draw a downward-pointing triangle for end
                    points = [
                        (subtreeroot.disp_xpos, subtreeroot.disp_ypos + triangle_size),
                        (subtreeroot.disp_xpos - triangle_size, subtreeroot.disp_ypos - triangle_size/2),
                        (subtreeroot.disp_xpos + triangle_size, subtreeroot.disp_ypos - triangle_size/2)
                    ]
                    pygame.draw.polygon(self.surface, self.GREEN, points)
            else:
                # Draw regular nodes as circles
                pygame.draw.circle(self.surface, subtreeroot.color, (subtreeroot.disp_xpos, subtreeroot.disp_ypos), self.TREE_NODE_RADIUS)

        
        # draw a square for the current node
        if (self.player_pos[0], self.player_pos[1]) in self.node_map:
            tree_loc_x = self.node_map[(self.player_pos[0], self.player_pos[1])].disp_xpos
            tree_loc_y = self.node_map[(self.player_pos[0], self.player_pos[1])].disp_ypos
            pygame.draw.rect(self.surface, self.RED, (tree_loc_x - self.TREE_NODE_RADIUS * self.TREE_CURSOR_MULTIPLIER, 
                                        tree_loc_y - self.TREE_NODE_RADIUS * self.TREE_CURSOR_MULTIPLIER, 
                                        self.TREE_NODE_RADIUS * 2 * self.TREE_CURSOR_MULTIPLIER, 
                                        self.TREE_NODE_RADIUS * 2 * self.TREE_CURSOR_MULTIPLIER))
        draw_subtree(self.node_map[(0, 1)])

    # Function for BFS - Modified to return exploration history
    def find_path_bfs(self):
        queue = deque([(self.start_pos[0], self.start_pos[1], [])]) 
        visited = set([(self.start_pos[0], self.start_pos[1])])
        
        exploration_history = []  
        
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        dir_names = ["UP", "RIGHT", "DOWN", "LEFT"]
        
        # Add initial state
        exploration_history.append((set(visited), set(), (self.start_pos[0], self.start_pos[1])))
        
        while queue:
            row, col, path = queue.popleft()
            
            # Check if we reached the exit
            if row == self.end_pos[0] and col == self.end_pos[1]:
                # Add the final path to the history
                path_set = set()
                current_pos = (self.start_pos[0], self.start_pos[1])
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
                if (0 <= new_row < self.GRID_SIZE and 0 <= new_col < self.GRID_SIZE and 
                    self.maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
                    frontier.add((new_row, new_col))
            
            # Record current state
            if frontier:
                exploration_history.append((set(visited), frontier, (row, col)))
            
            # Try all four directions
            for i, (dr, dc) in enumerate(directions):
                new_row, new_col = row + dr, col + dc
                
                # Check if the new position is valid and not visited
                if (0 <= new_row < self.GRID_SIZE and 0 <= new_col < self.GRID_SIZE and 
                    self.maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
                    queue.append((new_row, new_col, path + [dir_names[i]]))
                    visited.add((new_row, new_col))
        
        return [], exploration_history, set()  # No path found

    # Function for DFS - Modified to return exploration history
    def find_path_dfs(self):
        stack = [(self.start_pos[0], self.start_pos[1], [])]
        visited = set([(self.start_pos[0], self.start_pos[1])])
        
        exploration_history = []
        
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        dir_names = ["UP", "RIGHT", "DOWN", "LEFT"]
        
        # Add initial state
        exploration_history.append((set(visited), set(), (self.start_pos[0], self.start_pos[1])))
        
        while stack:
            row, col, path = stack.pop()  # DFS uses a stack (pop from end)
            
            # Check if we reached the exit
            if row == self.end_pos[0] and col == self.end_pos[1]:
                # Add the final path to the history
                path_set = set()
                current_pos = (self.start_pos[0], self.start_pos[1])
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
                if (0 <= new_row < self.GRID_SIZE and 0 <= new_col < self.GRID_SIZE and 
                    self.maze[new_row][new_col] == 0 and (new_row, new_col) not in visited):
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



    def update_simulation(self):
        self.process_pygame_events()
        self.surface.fill(self.bg_color)

            # Handle exploration visualization
        if self.solving_active:
            if not self.solution_paused and self.in_exploration_phase and self.exploration_step < len(self.exploration_history):
                # Update visualization states
                visited_set_temp, frontier_set_temp, current_pos_temp = self.exploration_history[self.exploration_step]
                self.visited_cells = visited_set_temp
                self.frontier_cells = frontier_set_temp
                self.player_pos = [current_pos_temp[0], current_pos_temp[1]]
                self.exploration_step += 1
                pygame.time.delay(200)  # Slow down the visualization
                
                # Check if exploration is complete
                if self.exploration_step >= len(self.exploration_history):
                    self.in_exploration_phase = False
                    # Reset player position to start for the solution path
                    self.player_pos = self.original_player_pos.copy()
                    # Mark the final path cells
                    self.path_cells = self.final_path_set
                    pygame.time.delay(500)  # Pause before starting the solution path
            
            elif not self.solution_paused and not self.in_exploration_phase and self.current_step < len(self.solution_path):
                # Now follow the solution path
                self.move_direction = self.solution_path[self.current_step]
                self.current_step += 1
                pygame.time.delay(200)  # Slow down the automatic moves
                
                if self.current_step >= len(self.solution_path):
                    solving_active = False
            if self.solution_step:
                # return the solve to paused
                self.solution_step = False
                self.solution_paused = True



        for button in self.buttons:
            pygame.draw.rect(self.surface, button['color'], button['rect'])
            text = self.font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.surface.blit(text, text_rect)
        self.draw_maze()
        self.draw_player()
        self.draw_tree()

        self.update()





    def process_pygame_events(self):
        for event in self.pygame_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for button clicks
                for button in self.buttons:
                    if button['rect'].collidepoint(event.pos):
                        button['action']()
        self.pygame_events = []

    def start_bfs(self):
                # Reset and start BFS exploration
        self.player_pos = self.original_player_pos.copy()
        self.solution_path, self.exploration_history, self.final_path_set = self.find_path_bfs()
        self.solving_active = True
        self.current_step = 0
        self.exploration_step = 0
        self.visited_cells.clear()
        self.frontier_cells.clear()
        self.path_cells.clear()
        self.in_exploration_phase = True
        self.current_algorithm = "BFS"
        self.move_direction = None
        print("BFS Solution path:", self.solution_path)
        print(f"BFS exploration: {len(self.exploration_history)} steps")
    
    def start_dfs(self):
        self.player_pos = self.original_player_pos.copy()
        self.solution_path, self.exploration_history, self.final_path_set = self.find_path_dfs()
        self.solving_active = True
        self.current_step = 0
        self.exploration_step = 0
        self.visited_cells.clear()
        self.frontier_cells.clear()
        self.path_cells.clear()
        self.in_exploration_phase = True
        self.current_algorithm = "DFS"
        self.move_direction = None
        print("DFS Solution path:", self.solution_path)
        print(f"DFS exploration: {len(self.exploration_history)} steps")

    def reset(self):
        print("MAZE RESET PRESSED")
        # Reset 
        self.player_pos = self.original_player_pos.copy()
        self.solving_active = False
        self.current_step = 0
        self.exploration_step = 0
        self.visited_cells.clear()
        self.frontier_cells.clear()
        self.path_cells.clear()
        self.move_direction = None
        self.solution_paused = False



    def set_background_red(self):
        self.bg_color = (100, 30, 30)

    def set_background_blue(self):
        self.bg_color = (30, 30, 100)

    def set_background_green(self):
        self.bg_color = (30, 100, 30)







class PygameQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COT3100 Visualizer")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()

        self.title_label = QLabel("Discrete Structures Visualizer")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        self.layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_style = "min-width: 150px; max-width: 150px; min-height: 50px; max-height: 50px;"

        self.buttons = []
        self.simulations = [
            {"name": "Moving Circle", "class": PygameWidget},
            {"name": "Button Demo", "class": ClickableSimulation},
            {"name": "MazeRunner", "class": MazeRunner},
            {"name": "Visualization 4", "class": None},
            {"name": "Visualization 5", "class": None},
            {"name": "Visualization 6", "class": None},
            {"name": "Visualization 7", "class": None}
        ]

        for i, sim in enumerate(self.simulations, 1):
            button = QPushButton(sim["name"])
            button.setStyleSheet(button_style)
            button.setFixedHeight(50)
            button.clicked.connect(lambda _, num=i: self.update_content(num))
            self.buttons.append(button)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        for button in self.buttons:
            button_layout.addWidget(button)

        self.layout.addLayout(button_layout)
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.visualization_container = QWidget()
        self.visualization_layout = QVBoxLayout(self.visualization_container)
        self.visualization_layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.visualization_container)

        self.visualization_widget = QLabel("Select a visualization")
        self.visualization_widget.setAlignment(Qt.AlignCenter)
        self.visualization_layout.addWidget(self.visualization_widget)

        central_widget.setLayout(self.layout)

    def update_content(self, visualization_number):
        if hasattr(self, 'visualization_widget') and self.visualization_widget is not None:
            self.visualization_layout.removeWidget(self.visualization_widget)
            self.visualization_widget.hide()

        sim_index = visualization_number - 1
        if sim_index < len(self.simulations) and self.simulations[sim_index]["class"]:
            sim_class = self.simulations[sim_index]["class"]
            self.visualization_widget = sim_class(self.visualization_container)
        else:
            self.visualization_widget = QLabel(f"Visualization {visualization_number} not implemented")
            self.visualization_widget.setAlignment(Qt.AlignCenter)

        self.visualization_layout.addWidget(self.visualization_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PygameQtApp()
    window.show()
    sys.exit(app.exec_())
