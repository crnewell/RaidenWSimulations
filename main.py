from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpacerItem, QSizePolicy, QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPixmap, QLinearGradient, QGradient
import sys
import pygame
import numpy as np
import subprocess
import os


class VisualizationCard(QFrame):
    # Custom widget for each visualization option

    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setObjectName("visualizationCard")
        self.setStyleSheet("""
            #visualizationCard {
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
            #visualizationCard:hover {
                background-color: #f5f5f5;
                border: 1px solid #c0c0c0;
            }
        """)

        # Add shadow effect
        self.setGraphicsEffect(self.create_shadow_effect())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #333; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; font-size: 14px; margin-top: 10px;")
        layout.addWidget(desc_label)

        # Spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Learn More button
        self.learn_button = QPushButton("Learn More")
        self.learn_button.setStyleSheet("""
            QPushButton {
                background-color: #5e72e4;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #324cdd;
            }
        """)
        self.learn_button.setFixedWidth(150)
        layout.addWidget(self.learn_button, 0, Qt.AlignRight)

    def create_shadow_effect(self):
        # Create a shadow effect for the card
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        from PyQt5.QtGui import QColor

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        return shadow


class PygameQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COT3100 Visualizer")
        self.setGeometry(100, 100, 1024, 768)  # Larger window size
        self.current_visualization = None

        self.set_application_style()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_home_screen()
        self.create_detail_screen()

        self.detail_widget.hide()

        self.simulations = [
            {
                "name": "MazeRunner",
                "external": "maze.py",
                "description": "A visualization that demonstrates pathfinding algorithms in a maze environment. Explore how algorithms like Breadth-First Search, and Depth-First Search navigate through complex mazes, and how this might be thought of as searching a tree.",
                "color": "#4CAF50"  # Green
            },
            {
                "name": "Graph Manipulation",
                "external": "adjlist.py",
                "description": "Interactive graph manipulation tools to understand graph theory concepts. Create, modify, and analyze graphs to learn about connectivity, cycles, and traversal algorithms.",
                "color": "#2196F3"  # Blue
            },
            {
                "name": "Sorting/Searching",
                "external": "sort.py",
                "description": "Visualize different sorting and searching algorithms in action. Compare the efficiency and behavior of  insertion sort, selection sort, bubble sort, quick sort, and linear and binary search.",
                "color": "#9C27B0"  # Purple
            },
            {
                "name": "Probability",
                "external": "probability.py",
                "description": "Explore probability concepts through interactive simulations. Understand distributions, random variables, and statistical concepts through visual demonstrations.",
                "color": "#FF9800"  # Orange
            },
            {
                "name": "Set Theory",
                "external": "setTheory.py",
                "description": "Visual representations of set operations and relationships. Learn about unions, intersections, complements, and other set operations through interactive diagrams.",
                "color": "#E91E63"  # Pink
            }
        ]

        self.create_visualization_cards()

    def set_application_style(self):
        # Set global application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                font-weight: bold;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

    def create_home_screen(self):
        # Create the home screen with header and content area
        self.home_widget = QWidget()
        home_layout = QVBoxLayout(self.home_widget)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(200)
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                       stop:0 #6B48FF, stop:1 #5E72E4);
            border-bottom: 1px solid #e0e0e0;
        """)

        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Discrete Structures Visualizer")
        title.setStyleSheet("color: white; font-size: 36px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Interactive tools to explore discrete mathematics concepts")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 18px;")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        home_layout.addWidget(header)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_scroll.setStyleSheet("background-color: transparent;")

        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)

        self.content_scroll.setWidget(self.content_widget)
        home_layout.addWidget(self.content_scroll)

        self.main_layout.addWidget(self.home_widget)

    def create_detail_screen(self):
        # Create the detail screen for visualization description
        self.detail_widget = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_widget)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_layout.setSpacing(0)

        detail_header = QWidget()
        detail_header.setFixedHeight(100)
        detail_header.setStyleSheet("""
            background-color: #f0f0f0;
            border-bottom: 1px solid #e0e0e0;
        """)

        header_layout = QHBoxLayout(detail_header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        back_button = QPushButton("← Back to Menu")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5e72e4;
                font-size: 16px;
                border: none;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                color: #324cdd;
            }
        """)
        back_button.clicked.connect(self.show_home_screen)
        header_layout.addWidget(back_button, 0, Qt.AlignLeft)

        self.detail_layout.addWidget(detail_header)

        self.detail_content = QWidget()
        self.detail_content_layout = QVBoxLayout(self.detail_content)
        self.detail_content_layout.setContentsMargins(60, 40, 60, 40)
        self.detail_content_layout.setAlignment(Qt.AlignCenter)

        self.detail_title = QLabel()
        self.detail_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #333; margin-bottom: 20px;")
        self.detail_title.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.addWidget(self.detail_title)

        self.detail_description = QLabel()
        self.detail_description.setWordWrap(True)
        self.detail_description.setStyleSheet("font-size: 18px; color: #555; line-height: 150%;")
        self.detail_description.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.addWidget(self.detail_description)

        self.detail_content_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.launch_button = QPushButton("Open Visualization")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #5e72e4;
                color: white;
                font-size: 18px;
                padding: 15px 32px;
                border-radius: 10px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #324cdd;
            }
        """)
        self.launch_button.clicked.connect(self.launch_visualization)
        self.detail_content_layout.addWidget(self.launch_button, 0, Qt.AlignCenter)

        self.detail_content_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        note = QLabel("You will return to this screen after closing the visualization")
        note.setStyleSheet("font-size: 14px; color: #888;")
        note.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.addWidget(note)

        self.detail_layout.addWidget(self.detail_content)
        self.main_layout.addWidget(self.detail_widget)

    def create_visualization_cards(self):
        # Create visualization cards in a grid layout
        num_simulations = len(self.simulations)
        cols = 2  # 2 columns
        rows = (num_simulations + 1) // 2  # Ceiling division

        for i, sim in enumerate(self.simulations):
            row = i // cols
            col = i % cols

            # Create card
            card = VisualizationCard(sim["name"], sim["description"])

            # Add colored indicator
            color_indicator = QFrame(card)
            color_indicator.setStyleSheet(f"background-color: {sim['color']}; border-radius: 5px;")
            color_indicator.setFixedSize(50, 5)
            card.layout().insertWidget(0, color_indicator)

            # Connect card button
            card.learn_button.clicked.connect(lambda _, idx=i: self.show_detail_screen(idx))

            # Add to grid
            self.content_layout.addWidget(card, row, col)

    def show_detail_screen(self, sim_index):
        # Show the detail screen for a specific visualization
        self.current_visualization = sim_index
        sim = self.simulations[sim_index]

        self.detail_title.setText(sim["name"])
        self.detail_description.setText(sim["description"])
        
        # Remove any existing pseudocode label if it exists
        for i in reversed(range(self.detail_content_layout.count())):
            widget = self.detail_content_layout.itemAt(i).widget()
            if widget is not None and widget.objectName() == "pseudocode_label":
                widget.deleteLater()
        
        # Special case for MazeRunner to include pseudocode
        if sim["name"] == "MazeRunner":
            self.detail_description.setText(sim["description"] + "\n How might you change the algorithm if the maze had loops?")
            # Create a gap before pseudocode
            self.detail_content_layout.addItem(QSpacerItem(60, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
            
            # Create pseudocode label
            pseudocode_label = QLabel()
            pseudocode_label.setObjectName("pseudocode_label")
            pseudocode_label.setText("""DFS(Maze):
        path = []
        visit(start_node, path)
    visit(location, path):
        if location == destination
            path.append(location)
            return True
        for each adjacent node neighbor
            if visit(neighbor, path)
                return True""")
            pseudocode_label.setFont(QFont("Courier New", 10))
            pseudocode_label.setStyleSheet("""
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
                text-align: left;
            """)
            pseudocode_label.setAlignment(Qt.AlignLeft)
            
            # Insert pseudocode label before the spacer that comes before the launch button
            spacer_index = -1
            for i in range(self.detail_content_layout.count()):
                if isinstance(self.detail_content_layout.itemAt(i), QSpacerItem):
                    spacer_index = i
                    break
            
            if spacer_index != -1:
                self.detail_content_layout.insertWidget(spacer_index, pseudocode_label)
            else:
                # Fallback if spacer not found
                self.detail_content_layout.addWidget(pseudocode_label)
        
        self.launch_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {sim['color']};
                color: white;
                font-size: 18px;
                padding: 15px 32px;
                border-radius: 10px;
                min-width: 250px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(sim['color'])};
            }}
        """)

        self.home_widget.hide()
        self.detail_widget.show()

    def show_home_screen(self):
        # Return to home screen
        self.detail_widget.hide()
        self.home_widget.show()

    def launch_visualization(self):
        # Launch the external visualization without blocking the main window
        if self.current_visualization is not None:
            external_file = self.simulations[self.current_visualization]["external"]
            try:
                # Use Popen instead of run for non-blocking execution
                subprocess.Popen([sys.executable, external_file])
                # No need to hide and show the main window anymore
            except Exception as e:
                print(f"Error running external visualization: {e}")

    def darken_color(self, hex_color):
        # Darken a hex color for hover effects
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        factor = 0.8
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))

        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = PygameQtApp()
    window.show()
    sys.exit(app.exec_())