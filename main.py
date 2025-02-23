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
        for i in range(1, 8):
            button = QPushButton(f"Visualization {i}")
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

        self.visualization_widget = QLabel("")
        self.visualization_widget.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.visualization_widget)
        central_widget.setLayout(self.layout)

    def update_content(self, visualization_number):

        if visualization_number == 1:
            self.visualization_widget = PygameWidget(self)
        else:
            self.visualization_widget = QLabel(f"This is visualization {visualization_number}")
            self.visualization_widget.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.visualization_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PygameQtApp()
    window.show()
    sys.exit(app.exec_())
