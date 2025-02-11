from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
import sys


class PygameQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COT3100 Visualizer")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.title_label = QLabel("Discrete Structures Visualizer")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
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

        layout.addLayout(button_layout)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.visualization_label = QLabel("")
        self.visualization_label.setAlignment(Qt.AlignCenter)  # Center the label
        layout.addWidget(self.visualization_label)
        central_widget.setLayout(layout)

    def update_content(self, visualization_number):
        self.visualization_label.setText(f"This is visualization {visualization_number}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PygameQtApp()
    window.show()
    sys.exit(app.exec_())
