from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import sys
import pygame
import numpy as np
from PyQt5.QtGui import QImage, QPainter


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
    # Constants
    WINDOW_WIDTH = 1200  # Increased width to fit tree
    WINDOW_HEIGHT = 400
    GRID_SIZE = 15     # Number of rows and columns in the maze
    CELL_SIZE = WINDOW_HEIGHT // GRID_SIZE  # Size of each cell
    TREE_X_OFFSET = (WINDOW_HEIGHT+WINDOW_WIDTH)//2  # Offset for tree visualization
    TREE_NODE_RADIUS = 10
    TREE_NODE_OFFSET = 6  # this is a multiplier to space the tree out vertically.
    TREE_CURSOR_MULTIPLIER = 2  # this is a multiplier to get the size of the red square in the tree



    def __init__(self, parent=None, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        super().__init__(parent, width, height)
        WINDOW_WIDTH = width
        WINDOW_HEIGHT = height

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
                'action': self.set_background_red
            },
            {
                'rect': pygame.Rect(BUTTON_X_DFS, BUTTON_Y_DFS, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_DFS,
                'action': self.set_background_blue
            },
            {
                'rect': pygame.Rect(BUTTON_X_RESET, BUTTON_Y_RESET, BUTTON_WIDTH, BUTTON_HEIGHT),
                'color': BUTTON_COLOR,
                'text': BUTTON_TEXT_RESET,
                'action': self.set_background_green
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
