from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import sys
import pygame
import numpy as np
from PyQt5.QtGui import QImage, QPainter
from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque
import subprocess

class PyGameQtWidget(QWidget):

    def __init__(self, parent=None, width=200, height=100):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
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

    def keyPressEvent(self, event):
        # TODO: add every key that you need to be pressed in pygame
        if event.key() == Qt.Key_Up:
            print("up key pressed")
            pygame_event = pygame.event.Event(
                pygame.KEYDOWN,
                {'key': pygame.K_UP}
            )
        elif event.key() == Qt.Key_Down:
            print("down key pressed")
            pygame_event = pygame.event.Event(
                pygame.KEYDOWN,
                {'key': pygame.K_DOWN}
            )
        elif event.key() == Qt.Key_Right:
            print("right key pressed")
            pygame_event = pygame.event.Event(
                pygame.KEYDOWN,
                {'key': pygame.K_RIGHT}
            )
        elif event.key() == Qt.Key_Left:
            print("left key pressed")
            pygame_event = pygame.event.Event(
                pygame.KEYDOWN,
                {'key': pygame.K_LEFT}
            )
        self.pygame_events.append(pygame_event)


    def get_button_state(self):
        return (0, 0, 0)


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
            {"name": "MazeRunner", "class": None, "external": "maze.py"},
            {"name": "Graph Manipulation", "class": None, "external": "adjlist.py"},
            {"name": "Sorting/Searching", "class": None, "external": "sort.py"},
            {"name": "Probability", "class": None, "external": "probability.py"},
            {"name": "Set Theory", "class": None, "external": "setTheory.py"}
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
        sim_index = visualization_number - 1

        # Check if this is an external visualization
        if sim_index < len(self.simulations) and self.simulations[sim_index].get("external"):
            # Hide main window
            self.hide()

            # Run the external Python file
            external_file = self.simulations[sim_index]["external"]
            try:
                subprocess.run([sys.executable, external_file])
            except Exception as e:
                print(f"Error running external visualization: {e}")

            # Show main window again after external program closes
            self.show()
            return

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