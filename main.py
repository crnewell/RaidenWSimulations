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
                "description": "Solve a maze by using the breadth-first or depth-first searches on the tree representation of the maze.",
                "color": "#4CAF50"  # Green
            },
            {
                "name": "Graph Manipulation",
                "external": "adjlist.py",
                "description": "Create a graph and convert it to an adjacency list, or vice versa.",
                "color": "#2196F3"  # Blue
            },
            {
                "name": "Sorting/Searching",
                "external": "sort.py",
                "description": "Visualize different sorting and searching algorithms in action.",
                "color": "#9C27B0"  # Purple
            },
            {
                "name": "Probability",
                "external": "probability.py",
                "description": "Understand basic probability concepts through a dice simulation",
                "color": "#FF9800"  # Orange
            },
            {
                "name": "Set Theory",
                "external": "setTheory.py",
                "description": "Learn about unions, intersections, and other common set operations through playing cards",
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
        self.detail_widget.setStyleSheet("background-color: #ffffff;")
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

        # Add scroll area for content
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setFrameShape(QFrame.NoFrame)
        detail_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.detail_content = QWidget()
        self.detail_content_layout = QVBoxLayout(self.detail_content)
        # Reduce margins to allow more content space
        self.detail_content_layout.setContentsMargins(40, 30, 40, 30)
        self.detail_content_layout.setAlignment(Qt.AlignTop)  # Align to top

        self.detail_title = QLabel()
        self.detail_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #333; margin-bottom: 20px;")
        self.detail_title.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.addWidget(self.detail_title)

        self.detail_description = QLabel()
        self.detail_description.setWordWrap(True)
        self.detail_description.setStyleSheet("font-size: 18px; color: #555; line-height: 150%;")
        self.detail_description.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.addWidget(self.detail_description)

        # Remove the spacer that could push content up
        # self.detail_content_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.launch_button = QPushButton("Open Visualization")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #5e72e4;
                color: white;
                font-size: 18px;
                padding: 15px 32px;
                border-radius: 10px;
                min-width: 250px;
                margin-top: 20px;
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

        # Add a spacer at the bottom to ensure good padding when scrolling
        self.detail_content_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Set the content widget to the scroll area
        detail_scroll.setWidget(self.detail_content)
        self.detail_layout.addWidget(detail_scroll)

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

#     def show_detail_screen(self, sim_index):
#         # Show the detail screen for a specific visualization
#         self.current_visualization = sim_index
#         sim = self.simulations[sim_index]
#
#         self.detail_title.setText(sim["name"])
#         self.detail_description.setText(sim["description"])
#
#         # Remove any existing pseudocode label if it exists
#         for i in reversed(range(self.detail_content_layout.count())):
#             widget = self.detail_content_layout.itemAt(i).widget()
#             if widget is not None and (widget.objectName() == "pseudocode_label" or
#                                     widget.objectName() == "pseudocode_label2" or
#                                     widget.objectName() == "pseudocode_label3" or
#                                     widget.objectName() == "pseudocode_adjlist" or
#                                     widget.objectName() == "pseudocode_adjmatrix" or
#                                     widget.objectName() == "pseudocode_union" or
#                                     widget.objectName() == "pseudocode_intersection" or
#                                     widget.objectName() == "pseudocode_difference" or
#                                     widget.objectName() == "pseudocode_symdifference"):
#                 widget.deleteLater()
#
#         # Special case for MazeRunner to include pseudocode
#         if sim["name"] == "MazeRunner":
#             self.detail_description.setText(sim["description"] + "\n How might you change the algorithm if the maze had loops?")
#             # Create a gap before pseudocode
#             self.detail_content_layout.addItem(QSpacerItem(60, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # Create pseudocode label
#             pseudocode_label = QLabel()
#             pseudocode_label.setObjectName("pseudocode_label")
#             pseudocode_label.setText("""DFS(Maze):
#     path = []
#     visit(start_node, path)
# visit(location, path):
#     if location == destination
#         path.append(location)
#         return True
#     for each adjacent node neighbor
#         if visit(neighbor, path)
#             path.append(location)
#             return True""")
#             pseudocode_label.setFont(QFont("Courier New", 10))
#             pseudocode_label.setStyleSheet("""
#                 background-color: #f5f5f5;
#                 padding: 15px;
#                 border-radius: 5px;
#                 border: 1px solid #e0e0e0;
#                 text-align: left;
#             """)
#             pseudocode_label.setAlignment(Qt.AlignLeft)
#
#             # Insert pseudocode label before the spacer that comes before the launch button
#             spacer_index = -1
#             for i in range(self.detail_content_layout.count()):
#                 if isinstance(self.detail_content_layout.itemAt(i), QSpacerItem):
#                     spacer_index = i
#                     break
#
#             if spacer_index != -1:
#                 self.detail_content_layout.insertWidget(spacer_index, pseudocode_label)
#             else:
#                 # Fallback if spacer not found
#                 self.detail_content_layout.addWidget(pseudocode_label)
#
#
#         elif sim["name"] == "Probability":
#             self.detail_content_layout.addItem(QSpacerItem(60, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # Create pseudocode label for Exact Roll Probability
#             pseudocode_label = QLabel()
#             pseudocode_label.setObjectName("pseudocode_label")
#             pseudocode_label.setText("""exact_roll_probability():
#                 probability = 1
#                 for die in dice:
#                     probability *= (1 / die.num_sides)
#                 return probability
#                 """)
#             pseudocode_label.setFont(QFont("Courier New", 10))
#             pseudocode_label.setStyleSheet("""
#                             background-color: #f5f5f5;
#                             padding: 15px;
#                             border-radius: 5px;
#                             border: 1px solid #e0e0e0;
#                             text-align: left;
#                         """)
#             pseudocode_label.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label)
#
#             # Add spacing between code blocks
#             self.detail_content_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # Create pseudocode label for Insertion Sort
#             pseudocode_label2 = QLabel()
#             pseudocode_label2.setObjectName("pseudocode_label2")
#             pseudocode_label2.setText("""unordered_roll_probability(target_roll, dice):
#     value_counts = {}
#     for value in target_roll:
#         if value not in value_counts:
#             value_counts[value] = 0
#         value_counts[value] += 1
#
#     num_permutations = factorial(len(target_roll))
#     for count in value_counts.values():
#         num_permutations /= factorial(count)
#
#     probability = 1
#     for i in range(len(target_roll)):
#         probability *= (1 / dice[i].num_sides)
#
#     return probability * num_permutations""")
#             pseudocode_label2.setFont(QFont("Courier New", 10))
#             pseudocode_label2.setStyleSheet("""
#                             background-color: #f5f5f5;
#                             padding: 15px;
#                             border-radius: 5px;
#                             border: 1px solid #e0e0e0;
#                             text-align: left;
#                         """)
#             pseudocode_label2.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label2)
#
#             # Add spacing between code blocks
#             self.detail_content_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # # Create title label for Selection Sort
#             # ss_title = QLabel("Selection Sort:")
#             # ss_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
#             # ss_title.setAlignment(Qt.AlignLeft)
#             # self.detail_content_layout.addWidget(ss_title)
#
#             # Create pseudocode label for Selection Sort
#             pseudocode_label3 = QLabel()
#             pseudocode_label3.setObjectName("pseudocode_label3")
#             pseudocode_label3.setText("""sum_roll_probability(target_roll, dice):
#     target_sum = sum(target_roll)
#
#     total_outcomes = 1
#     for die in dice:
#         total_outcomes *= die.num_sides
#
#     successful_outcomes = 0
#
#     def count_successful(current_roll, index):
#         nonlocal successful_outcomes
#         if index == len(dice):
#             if sum(current_roll) == target_sum:
#                 successful_outcomes += 1
#             return
#         for face in range(1, dice[index].num_sides + 1):
#             count_successful(current_roll + [face], index + 1)
#
#     count_successful([], 0)
#
#     return successful_outcomes / total_outcomes""")
#             pseudocode_label3.setFont(QFont("Courier New", 10))
#             pseudocode_label3.setStyleSheet("""
#                             background-color: #f5f5f5;
#                             padding: 15px;
#                             border-radius: 5px;
#                             border: 1px solid #e0e0e0;
#                             text-align: left;
#                         """)
#             pseudocode_label3.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label3)
#
#         # Special case for Sorting/Searching to include pseudocode
#         elif sim["name"] == "Sorting/Searching":
#             # Create a gap before pseudocode
#             self.detail_content_layout.addItem(QSpacerItem(60, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # # Create title label for Binary Search
#             # bs_title = QLabel("Binary Search:")
#             # bs_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
#             # bs_title.setAlignment(Qt.AlignLeft)
#             # self.detail_content_layout.addWidget(bs_title)
#
#             # Create pseudocode label for Binary Search
#             pseudocode_label = QLabel()
#             pseudocode_label.setObjectName("pseudocode_label")
#             pseudocode_label.setText("""binary_search(list, target):
#     left = 0
#     right = length(list) - 1
#     while left <= right:
#         mid = (left + right) // 2
#         if list[mid] == target:
#             return mid
#         elif list[mid] < target:
#             left = mid + 1
#         else:
#             right = mid - 1
#     return -1""")
#             pseudocode_label.setFont(QFont("Courier New", 10))
#             pseudocode_label.setStyleSheet("""
#                 background-color: #f5f5f5;
#                 padding: 15px;
#                 border-radius: 5px;
#                 border: 1px solid #e0e0e0;
#                 text-align: left;
#             """)
#             pseudocode_label.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label)
#
#             # Add spacing between code blocks
#             self.detail_content_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # # Create title label for Insertion Sort
#             # is_title = QLabel("Insertion Sort:")
#             # is_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
#             # is_title.setAlignment(Qt.AlignLeft)
#             # self.detail_content_layout.addWidget(is_title)
#
#             # Create pseudocode label for Insertion Sort
#             pseudocode_label2 = QLabel()
#             pseudocode_label2.setObjectName("pseudocode_label2")
#             pseudocode_label2.setText("""insertion_sort(array):
#     for i from 1 to length(array) - 1:
#         key = array[i]
#         j = i - 1
#         while j >= 0 and array[j] > key:
#             array[j + 1] = array[j]
#             j = j - 1
#         array[j + 1] = key
#     return array""")
#             pseudocode_label2.setFont(QFont("Courier New", 10))
#             pseudocode_label2.setStyleSheet("""
#                 background-color: #f5f5f5;
#                 padding: 15px;
#                 border-radius: 5px;
#                 border: 1px solid #e0e0e0;
#                 text-align: left;
#             """)
#             pseudocode_label2.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label2)
#
#             # Add spacing between code blocks
#             self.detail_content_layout.addItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
#
#             # # Create title label for Selection Sort
#             # ss_title = QLabel("Selection Sort:")
#             # ss_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
#             # ss_title.setAlignment(Qt.AlignLeft)
#             # self.detail_content_layout.addWidget(ss_title)
#
#             # Create pseudocode label for Selection Sort
#             pseudocode_label3 = QLabel()
#             pseudocode_label3.setObjectName("pseudocode_label3")
#             pseudocode_label3.setText("""selection_sort(array):
#     for i from 0 to length(array) - 1:
#         min_index = i
#         for j from i + 1 to length(array) - 1:
#             if array[j] < array[min_index]:
#                 min_index = j
#         if min_index != i:
#             swap array[i] and array[min_index]
#     return array""")
#             pseudocode_label3.setFont(QFont("Courier New", 10))
#             pseudocode_label3.setStyleSheet("""
#                 background-color: #f5f5f5;
#                 padding: 15px;
#                 border-radius: 5px;
#                 border: 1px solid #e0e0e0;
#                 text-align: left;
#             """)
#             pseudocode_label3.setAlignment(Qt.AlignLeft)
#             self.detail_content_layout.addWidget(pseudocode_label3)
#
#         elif sim["name"] == "Graph Manipulation":
#             # Extend the description
#             self.detail_description.setText(
#                 sim["description"]
#             )
#
#             # Spacer before pseudocode
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Adjacency List Pseudocode
#             pnl = QLabel()
#             pnl.setObjectName("pseudocode_adjlist")
#             pnl.setText(
#                 "def build_adjacency_list(graph):\n"
#                 "    # initialize empty list for each node\n"
#                 "    adjacency = { node: [] for node in graph.nodes() }\n"
#                 "    # populate edges\n"
#                 "    for u, v in graph.edges():\n"
#                 "        adjacency[u].append(v)\n"
#                 "        adjacency[v].append(u)  # if undirected\n"
#                 "    return adjacency"
#             )
#             pnl.setFont(QFont("Courier New", 10))
#             pnl.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             pnl.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(pnl)
#
#             # Small spacer between code blocks
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Adjacency Matrix Pseudocode
#             pmx = QLabel()
#             pmx.setObjectName("pseudocode_adjmatrix")
#             pmx.setText(
#                 "def build_adjacency_matrix(graph):\n"
#                 "    n = graph.number_of_nodes()\n"
#                 "    # create n×n zero matrix\n"
#                 "    matrix = [[0]*n for _ in range(n)]\n"
#                 "    # fill in edges\n"
#                 "    for u, v in graph.edges():\n"
#                 "        matrix[u][v] = 1\n"
#                 "        matrix[v][u] = 1  # if undirected\n"
#                 "    return matrix"
#             )
#             pmx.setFont(QFont("Courier New", 10))
#             pmx.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             pmx.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(pmx)
#
#             # Spacer before launching external visualization
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#         elif sim["name"] == "Set Theory":
#             # Extend the description
#             self.detail_description.setText(
#                 sim["description"]
#             )
#
#             # Spacer before pseudocode
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Union Pseudocode
#             pu = QLabel()
#             pu.setObjectName("pseudocode_union")
#             pu.setText(
#                 "def union(A, B):\n"
#                 "    # return a new set containing all elements in A or B\n"
#                 "    result = set()\n"
#                 "    for x in A:\n"
#                 "        result.add(x)\n"
#                 "    for x in B:\n"
#                 "        result.add(x)\n"
#                 "    return result"
#             )
#             pu.setFont(QFont("Courier New", 10))
#             pu.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             pu.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(pu)
#
#             # Spacer
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Intersection Pseudocode
#             pi = QLabel()
#             pi.setObjectName("pseudocode_intersection")
#             pi.setText(
#                 "def intersection(A, B):\n"
#                 "    # return a new set containing elements in both A and B\n"
#                 "    result = set()\n"
#                 "    for x in A:\n"
#                 "        if x in B:\n"
#                 "            result.add(x)\n"
#                 "    return result"
#             )
#             pi.setFont(QFont("Courier New", 10))
#             pi.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             pi.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(pi)
#
#             # Spacer
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Difference Pseudocode
#             pd = QLabel()
#             pd.setObjectName("pseudocode_difference")
#             pd.setText(
#                 "def difference(A, B):\n"
#                 "    # return elements in A that are not in B\n"
#                 "    result = set()\n"
#                 "    for x in A:\n"
#                 "        if x not in B:\n"
#                 "            result.add(x)\n"
#                 "    return result"
#             )
#             pd.setFont(QFont("Courier New", 10))
#             pd.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             pd.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(pd)
#
#             # Spacer
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#             # Symmetric Difference Pseudocode
#             ps = QLabel()
#             ps.setObjectName("pseudocode_symdifference")
#             ps.setText(
#                 "def symmetric_difference(A, B):\n"
#                 "    # return elements in A or B but not both\n"
#                 "    result = set()\n"
#                 "    for x in A:\n"
#                 "        if x not in B:\n"
#                 "            result.add(x)\n"
#                 "    for x in B:\n"
#                 "        if x not in A:\n"
#                 "            result.add(x)\n"
#                 "    return result"
#             )
#             ps.setFont(QFont("Courier New", 10))
#             ps.setStyleSheet(
#                 "background-color: #f5f5f5;"
#                 "padding: 10px;"
#                 "border-radius: 4px;"
#                 "border: 1px solid #ddd;"
#             )
#             ps.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#             self.detail_content_layout.addWidget(ps)
#
#             # Spacer before launch button
#             self.detail_content_layout.addItem(
#                 QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
#             )
#
#
#         self.launch_button.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: {sim['color']};
#                 color: white;
#                 font-size: 18px;
#                 padding: 15px 32px;
#                 border-radius: 10px;
#                 min-width: 250px;
#             }}
#             QPushButton:hover {{
#                 background-color: {self.darken_color(sim['color'])};
#             }}
#         """)
#
#         self.home_widget.hide()
#         self.detail_widget.show()
    def show_detail_screen(self, sim_index):
        # Show the detail screen for a specific visualization
        self.current_visualization = sim_index
        sim = self.simulations[sim_index]

        self.detail_title.setText(sim["name"])
        self.detail_description.setText(sim["description"])

        # First, clear all dynamic content from previous views
        self.clear_dynamic_content()

        # Now add the specific content for this visualization
        if sim["name"] == "MazeRunner":
            self.add_mazerunner_content(sim)
        elif sim["name"] == "Probability":
            self.add_probability_content(sim)
        elif sim["name"] == "Sorting/Searching":
            self.add_sorting_content(sim)
        elif sim["name"] == "Graph Manipulation":
            self.add_graph_content(sim)
        elif sim["name"] == "Set Theory":
            self.add_set_theory_content(sim)

        # Configure the launch button
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

    def clear_dynamic_content(self):
        """Remove all dynamically added content (pseudocode, spacers) from the detail layout"""
        # Get the position of the title, description and launch button
        title_pos = self.detail_content_layout.indexOf(self.detail_title)
        desc_pos = self.detail_content_layout.indexOf(self.detail_description)
        launch_pos = self.detail_content_layout.indexOf(self.launch_button)

        # We need to keep track of the indices of items to remove
        items_to_remove = []

        # Find all widgets and spacers between description and launch button
        for i in range(desc_pos + 1, launch_pos):
            items_to_remove.append(i)

        # Remove items in reverse (to avoid index shifting)
        for i in sorted(items_to_remove, reverse=True):
            item = self.detail_content_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
            else:  # It's a spacer
                self.detail_content_layout.removeItem(item)

    def add_mazerunner_content(self, sim):
        """Add MazeRunner specific content"""
        self.detail_description.setText(
            sim["description"] + "\n How might you change the algorithm if the maze had loops?")

        # Add spacer
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(60, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Add pseudocode
        pseudocode_label = QLabel()
        pseudocode_label.setObjectName("pseudocode_label")
        pseudocode_label.setText("""def DFS(Maze):
        path = []
        visited_nodes = {}
        visit(start_node, path, visited_nodes)
        return path
def visit(location, path, visited_nodes):
    visited_nodes.add(location)
    if location == destination
        path.append(location)
        return True
    for each adjacent node neighbor
        if neighbor not in visited_nodes
            if visit(neighbor, path)
                path.append(location)
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

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label
        )

    def add_probability_content(self, sim):
        """Add Probability specific content"""

        # Add spacer
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(60, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Exact Roll Probability
        pseudocode_label = QLabel()
        pseudocode_label.setObjectName("pseudocode_label")
        pseudocode_label.setText("""exact_roll_probability():
        probability = 1
        for die in dice:
            probability *= (1 / die.num_sides)
        return probability
        """)
        pseudocode_label.setFont(QFont("Courier New", 10))
        pseudocode_label.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Unordered Roll Probability
        pseudocode_label2 = QLabel()
        pseudocode_label2.setObjectName("pseudocode_label2")
        pseudocode_label2.setText("""unordered_roll_probability(target_roll, dice):
        value_counts = {}
        for value in target_roll:
            if value not in value_counts:
                value_counts[value] = 0
            value_counts[value] += 1

        num_permutations = factorial(len(target_roll))
        for count in value_counts.values():
            num_permutations /= factorial(count)

        probability = 1
        for i in range(len(target_roll)):
            probability *= (1 / dice[i].num_sides)

        return probability * num_permutations""")
        pseudocode_label2.setFont(QFont("Courier New", 10))
        pseudocode_label2.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label2.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label2
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Sum Roll Probability
        pseudocode_label3 = QLabel()
        pseudocode_label3.setObjectName("pseudocode_label3")
        pseudocode_label3.setText("""sum_roll_probability(target_roll, dice):
        target_sum = sum(target_roll)

        total_outcomes = 1
        for die in dice:
            total_outcomes *= die.num_sides

        successful_outcomes = 0

        def count_successful(current_roll, index):
            nonlocal successful_outcomes
            if index == len(dice):
                if sum(current_roll) == target_sum:
                    successful_outcomes += 1
                return
            for face in range(1, dice[index].num_sides + 1):
                count_successful(current_roll + [face], index + 1)

        count_successful([], 0)

        return successful_outcomes / total_outcomes""")
        pseudocode_label3.setFont(QFont("Courier New", 10))
        pseudocode_label3.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label3.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label3
        )

    def add_sorting_content(self, sim):
        """Add Sorting/Searching specific content"""

        # Add spacer
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(60, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Binary Search
        pseudocode_label = QLabel()
        pseudocode_label.setObjectName("pseudocode_label")
        pseudocode_label.setText("""binary_search(list, target):
        left = 0
        right = length(list) - 1
        while left <= right:
            mid = (left + right) // 2
            if list[mid] == target:
                return mid
            elif list[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1""")
        pseudocode_label.setFont(QFont("Courier New", 10))
        pseudocode_label.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Insertion Sort
        pseudocode_label2 = QLabel()
        pseudocode_label2.setObjectName("pseudocode_label2")
        pseudocode_label2.setText("""insertion_sort(array):
        for i from 1 to length(array) - 1:
            key = array[i]
            j = i - 1
            while j >= 0 and array[j] > key:
                array[j + 1] = array[j]
                j = j - 1
            array[j + 1] = key
        return array""")
        pseudocode_label2.setFont(QFont("Courier New", 10))
        pseudocode_label2.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label2.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label2
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create pseudocode label for Selection Sort
        pseudocode_label3 = QLabel()
        pseudocode_label3.setObjectName("pseudocode_label3")
        pseudocode_label3.setText("""selection_sort(array):
        for i from 0 to length(array) - 1:
            min_index = i
            for j from i + 1 to length(array) - 1:
                if array[j] < array[min_index]:
                    min_index = j
            if min_index != i:
                swap array[i] and array[min_index]
        return array""")
        pseudocode_label3.setFont(QFont("Courier New", 10))
        pseudocode_label3.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            text-align: left;
        """)
        pseudocode_label3.setAlignment(Qt.AlignLeft)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pseudocode_label3
        )

    def add_graph_content(self, sim):
        """Add Graph Manipulation specific content"""

        # Add spacer
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Adjacency List Pseudocode
        pnl = QLabel()
        pnl.setObjectName("pseudocode_adjlist")
        pnl.setText(
            "def build_adjacency_list(graph):\n"
            "    # initialize empty list for each node\n"
            "    adjacency = { node: [] for node in graph.nodes() }\n"
            "    # populate edges\n"
            "    for u, v in graph.edges():\n"
            "        adjacency[u].append(v)\n"
            "        adjacency[v].append(u)  # if undirected\n"
            "    return adjacency"
        )
        pnl.setFont(QFont("Courier New", 10))
        pnl.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        pnl.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pnl
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Adjacency Matrix Pseudocode
        pmx = QLabel()
        pmx.setObjectName("pseudocode_adjmatrix")
        pmx.setText(
            "def build_adjacency_matrix(graph):\n"
            "    n = graph.number_of_nodes()\n"
            "    # create n×n zero matrix\n"
            "    matrix = [[0]*n for _ in range(n)]\n"
            "    # fill in edges\n"
            "    for u, v in graph.edges():\n"
            "        matrix[u][v] = 1\n"
            "        matrix[v][u] = 1  # if undirected\n"
            "    return matrix"
        )
        pmx.setFont(QFont("Courier New", 10))
        pmx.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        pmx.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pmx
        )

        # Add spacing before launch button
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

    def add_set_theory_content(self, sim):
        """Add Set Theory specific content"""

        # Add spacer
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Union Pseudocode
        pu = QLabel()
        pu.setObjectName("pseudocode_union")
        pu.setText(
            "def union(A, B):\n"
            "    # return a new set containing all elements in A or B\n"
            "    result = set()\n"
            "    for x in A:\n"
            "        result.add(x)\n"
            "    for x in B:\n"
            "        result.add(x)\n"
            "    return result"
        )
        pu.setFont(QFont("Courier New", 10))
        pu.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        pu.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pu
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Intersection Pseudocode
        pi = QLabel()
        pi.setObjectName("pseudocode_intersection")
        pi.setText(
            "def intersection(A, B):\n"
            "    # return a new set containing elements in both A and B\n"
            "    result = set()\n"
            "    for x in A:\n"
            "        if x in B:\n"
            "            result.add(x)\n"
            "    return result"
        )
        pi.setFont(QFont("Courier New", 10))
        pi.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        pi.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pi
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Difference Pseudocode
        pd = QLabel()
        pd.setObjectName("pseudocode_difference")
        pd.setText(
            "def difference(A, B):\n"
            "    # return elements in A that are not in B\n"
            "    result = set()\n"
            "    for x in A:\n"
            "        if x not in B:\n"
            "            result.add(x)\n"
            "    return result"
        )
        pd.setFont(QFont("Courier New", 10))
        pd.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        pd.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            pd
        )

        # Add spacing between code blocks
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Symmetric Difference Pseudocode
        ps = QLabel()
        ps.setObjectName("pseudocode_symdifference")
        ps.setText(
            "def symmetric_difference(A, B):\n"
            "    # return elements in A or B but not both\n"
            "    result = set()\n"
            "    for x in A:\n"
            "        if x not in B:\n"
            "            result.add(x)\n"
            "    for x in B:\n"
            "        if x not in A:\n"
            "            result.add(x)\n"
            "    return result"
        )
        ps.setFont(QFont("Courier New", 10))
        ps.setStyleSheet(
            "background-color: #f5f5f5;"
            "padding: 10px;"
            "border-radius: 4px;"
            "border: 1px solid #ddd;"
        )
        ps.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Insert before launch button
        self.detail_content_layout.insertWidget(
            self.detail_content_layout.indexOf(self.launch_button),
            ps
        )

        # Add spacing before launch button
        self.detail_content_layout.insertItem(
            self.detail_content_layout.indexOf(self.launch_button),
            QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

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