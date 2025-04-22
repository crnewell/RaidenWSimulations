import pygame
import sys
import math
import time


pygame.init()

WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
MAX_NODES = 7
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)
#
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Graph Visualization")

nodes = []
edges = []
adj_list = {}
adjacency_matrix = []

selected_node = None
show_matrix = False  # Toggle between adjacency list and matrix
traversal_mode = None  # Can be None, "BFS", or "DFS"
traversal_start = None
traversal_path = []
traversal_visited = set()
traversal_queue = []  # For BFS
traversal_stack = []  # For DFS
traversal_delay = 500  # milliseconds
last_traversal_time = 0
back_button_rect = pygame.Rect(WIDTH - 110, HEIGHT - 40, 100, 30)
back_button_active = False

# Variables for editing adjacency representations
editing_matrix = False
editing_list = False
matrix_cell = None  # (row, col) of selected matrix cell

# Text editing variables
editing_row = None  # Node index currently being edited
edit_text = ""  # Current text being edited
active_text_input = False  # Flag for active text input


def initialize_adj_matrix():
    global adjacency_matrix
    n = len(nodes)
    adjacency_matrix = [[0 for _ in range(n)] for _ in range(n)]
    for u, v in edges:
        adjacency_matrix[u][v] = 1
        adjacency_matrix[v][u] = 1  # For undirected graph


def update_from_matrix():
    global edges, adj_list
    edges = []
    adj_list = {i: [] for i in range(len(nodes))}

    for i in range(len(adjacency_matrix)):
        for j in range(i + 1, len(adjacency_matrix)):  # Start from i+1 to avoid duplicates for undirected graph
            if adjacency_matrix[i][j] == 1:
                edges.append((i, j))
                adj_list[i].append(j)
                adj_list[j].append(i)


def update_from_adj_list():
    global edges, adjacency_matrix
    edges = []
    n = len(nodes)
    adjacency_matrix = [[0 for _ in range(n)] for _ in range(n)]

    for node, neighbors in adj_list.items():
        for neighbor in neighbors:
            if (node, neighbor) not in edges and (neighbor, node) not in edges:
                edges.append((node, neighbor))
            adjacency_matrix[node][neighbor] = 1
            adjacency_matrix[neighbor][node] = 1


def parse_adj_list_input(node_idx, input_str):
    """Parse user input for adjacency list and update the graph"""
    global adj_list

    # Remove any brackets if present
    input_str = input_str.strip()
    if input_str.startswith('['):
        input_str = input_str[1:]
    if input_str.endswith(']'):
        input_str = input_str[:-1]

    # Split by commas and convert to integers
    try:
        if input_str:
            new_neighbors = [int(n.strip()) for n in input_str.split(',') if n.strip()]
            # Validate neighbors (must be valid node indices)
            valid_neighbors = [n for n in new_neighbors if 0 <= n < len(nodes) and n != node_idx]

            # Create set for efficient operations
            old_neighbors = set(adj_list[node_idx])
            new_neighbors_set = set(valid_neighbors)

            # Remove edges that are no longer present
            for old_neighbor in old_neighbors:
                if old_neighbor not in new_neighbors_set:
                    delete_edge(node_idx, old_neighbor)

            # Add new edges
            for new_neighbor in new_neighbors_set:
                if new_neighbor not in old_neighbors:
                    add_edge(node_idx, new_neighbor)
        else:
            # Empty input means remove all edges
            for neighbor in list(adj_list[node_idx]):
                delete_edge(node_idx, neighbor)
    except ValueError:
        # If input couldn't be parsed, just ignore
        pass


def draw_graph():
    screen.fill(WHITE)

    # Draw edges
    for i, edge in enumerate(edges):
        start, end = nodes[edge[0]], nodes[edge[1]]
        # Highlight edge if it's part of the traversal path
        if traversal_mode and (edge[0], edge[1]) in traversal_path or (edge[1], edge[0]) in traversal_path:
            pygame.draw.line(screen, GREEN, start, end, 3)
        else:
            pygame.draw.line(screen, BLACK, start, end, 2)

    # Draw nodes
    for i, (x, y) in enumerate(nodes):
        if traversal_mode and i in traversal_visited:
            color = GREEN  # Visited node
        elif traversal_mode and i == traversal_start:
            color = YELLOW  # Start node
        elif i == selected_node:
            color = RED  # Selected node
        else:
            color = BLUE  # Regular node
        pygame.draw.circle(screen, color, (x, y), NODE_RADIUS)
        text = font.render(str(i), True, WHITE)
        screen.blit(text, (x - 5, y - 7))

    # Draw adjacency representation box
    pygame.draw.rect(screen, GRAY, (10, HEIGHT - 310, 350, 300))

    # Draw editing instructions
    if editing_matrix or editing_list:
        if editing_matrix:
            instruction_text = "Click cell to toggle edge"
        else:
            instruction_text = "Click on a row to edit neighbors"
        instruction_surface = font.render(instruction_text, True, BLACK)
        screen.blit(instruction_surface, (20, HEIGHT - 310 + 5))

    if show_matrix:
        # Draw adjacency matrix
        title = font.render("Adjacency Matrix (Editable):", True, BLACK)
        screen.blit(title, (20, HEIGHT - 290))

        if adjacency_matrix:
            cell_size = 30
            matrix_start_x = 30
            matrix_start_y = HEIGHT - 250

            # Draw row and column labels
            for i in range(len(adjacency_matrix)):
                # Row labels
                label = font.render(str(i), True, BLACK)
                screen.blit(label, (matrix_start_x - 20, matrix_start_y + i * cell_size + 10))
                # Column labels
                screen.blit(label, (matrix_start_x + i * cell_size + 10, matrix_start_y - 20))

            # Draw matrix cells
            for i in range(len(adjacency_matrix)):
                for j in range(len(adjacency_matrix[i])):
                    # Highlight cell when editing
                    if editing_matrix and matrix_cell == (i, j):
                        cell_color = RED if adjacency_matrix[i][j] == 0 else GREEN
                    else:
                        cell_color = WHITE if adjacency_matrix[i][j] == 0 else BLUE

                    pygame.draw.rect(screen, cell_color,
                                     (matrix_start_x + j * cell_size, matrix_start_y + i * cell_size,
                                      cell_size, cell_size))
                    pygame.draw.rect(screen, BLACK,
                                     (matrix_start_x + j * cell_size, matrix_start_y + i * cell_size,
                                      cell_size, cell_size), 1)
                    value = font.render(str(adjacency_matrix[i][j]), True,
                                        BLACK if adjacency_matrix[i][j] == 0 else WHITE)
                    screen.blit(value, (matrix_start_x + j * cell_size + 10, matrix_start_y + i * cell_size + 10))
    else:
        # Draw adjacency list
        title = font.render("Adjacency List (Editable):", True, BLACK)
        screen.blit(title, (20, HEIGHT - 290))

        y_offset = 35
        for node in sorted(adj_list.keys()):
            neighbors = sorted(adj_list[node])

            # Determine if this row is being edited
            is_editing_this_row = editing_list and editing_row == node and active_text_input

            # Draw row background if being edited
            if editing_list and editing_row == node:
                pygame.draw.rect(screen, LIGHT_GRAY, (20, HEIGHT - 280 + y_offset - 5, 320, 30))

            # Draw node index and bracket
            node_text = f"{node}: ["
            screen.blit(font.render(node_text, True, BLACK), (20, HEIGHT - 280 + y_offset))

            # If this row is actively being edited, show text input
            if is_editing_this_row:
                # Draw input box
                input_rect = pygame.Rect(20 + font.size(node_text)[0], HEIGHT - 280 + y_offset - 2,
                                         180, font.get_height() + 4)
                pygame.draw.rect(screen, WHITE, input_rect)
                pygame.draw.rect(screen, BLACK, input_rect, 1)

                # Render edit text with cursor
                edit_surface = font.render(edit_text + "|", True, BLACK)
                screen.blit(edit_surface, (input_rect.x + 5, input_rect.y + 2))

                # Draw closing bracket
                screen.blit(font.render("]", True, BLACK),
                            (input_rect.x + input_rect.width + 5, HEIGHT - 280 + y_offset))
            else:
                # Format neighbors with commas
                if neighbors:
                    neighbor_str = ", ".join(map(str, neighbors))
                    screen.blit(font.render(neighbor_str, True, BLACK),
                                (20 + font.size(node_text)[0], HEIGHT - 280 + y_offset))

                # Draw closing bracket
                bracket_x = 20 + font.size(node_text)[0]
                if neighbors:
                    bracket_x += font.size(", ".join(map(str, neighbors)))[0]
                screen.blit(font.render("]", True, BLACK), (bracket_x + 5, HEIGHT - 280 + y_offset))

            y_offset += 35

        # Add node capability
        if len(nodes) < MAX_NODES:
            add_node_text = f"+ Add node {len(nodes)}"
            add_node_surface = font.render(add_node_text, True, GREEN)
            screen.blit(add_node_surface, (20, HEIGHT - 280 + y_offset))

    # Traversal info and queue/stack visualization
    if traversal_mode:
        info_text = f"{traversal_mode} Traversal from node {traversal_start}"
        text_surface = font.render(info_text, True, BLACK)
        screen.blit(text_surface, (WIDTH - 250, HEIGHT - 50))

        if traversal_mode == "BFS":
            queue_text = f"Queue: {traversal_queue}"
            queue_surface = font.render(queue_text, True, BLACK)
            screen.blit(queue_surface, (WIDTH - 250, HEIGHT - 25))
        elif traversal_mode == "DFS":
            stack_text = f"Stack: {traversal_stack}"
            stack_surface = font.render(stack_text, True, BLACK)
            screen.blit(stack_surface, (WIDTH - 250, HEIGHT - 25))

    instructions = [
        f"Left Click: Add Node ({len(nodes)}/{MAX_NODES})",
        "Left Click Two Nodes: Add Edge",
        "Right Click Twice: Delete Node",
        "Right Click Two Nodes: Delete Edge",
        "M: Matrix/List View Toggle",
        "E: Edit Toggle",
        "B: Start BFS Traversal",
        "D: Start DFS Traversal",
        "ESC: Cancel Traversal/Editing"
    ]
    for i, text in enumerate(instructions):
        instruction = small_font.render(text, True, BLACK)
        screen.blit(instruction, (WIDTH - 210, 10 + i * 20))

    if back_button_active:
        pygame.draw.rect(screen, GREEN, back_button_rect)
    else:
        pygame.draw.rect(screen, BLUE, back_button_rect)
    pygame.draw.rect(screen, BLACK, back_button_rect, 1)
    back_text = font.render("Back", True, WHITE)
    screen.blit(back_text, (back_button_rect.x + 30, back_button_rect.y + 7))

    pygame.display.flip()


def get_clicked_node(pos):
    x, y = pos
    for i, (nx, ny) in enumerate(nodes):
        if math.hypot(nx - x, ny - y) <= NODE_RADIUS:
            return i
    return None


def is_in_adj_list_area(pos):
    x, y = pos
    return (10 <= x <= 360) and (HEIGHT - 310 <= y <= HEIGHT - 10)


def check_matrix_cell_click(pos):
    if not adjacency_matrix or not show_matrix:
        return None

    cell_size = 30
    matrix_start_x = 30
    matrix_start_y = HEIGHT - 250
    x, y = pos

    if (matrix_start_x <= x <= matrix_start_x + len(adjacency_matrix) * cell_size and
            matrix_start_y <= y <= matrix_start_y + len(adjacency_matrix) * cell_size):
        col = (x - matrix_start_x) // cell_size
        row = (y - matrix_start_y) // cell_size
        if 0 <= row < len(adjacency_matrix) and 0 <= col < len(adjacency_matrix[0]):
            return (row, col)
    return None


def check_adj_list_row_click(pos):
    if not adj_list or show_matrix:
        return None

    y_offset = HEIGHT - 280 + 35  # Start of adjacency list items
    x, y = pos

    for node in sorted(adj_list.keys()):
        # Check if click is on this row
        if (20 <= x <= 340) and (y_offset - 5 <= y <= y_offset + font.get_height() + 5):
            return node
        y_offset += 35

    # Check for "+ Add node" click
    if len(nodes) < MAX_NODES:
        add_node_y = HEIGHT - 280 + 35 * (len(adj_list) + 1)
        if (20 <= x <= 150) and (add_node_y - 5 <= y <= add_node_y + font.get_height() + 5):
            return "add_node"

    return None


def delete_node(node_index):
    global adj_list, adjacency_matrix
    if node_index in adj_list:
        edges[:] = [edge for edge in edges if node_index not in edge]
        del adj_list[node_index]
        for node in adj_list:
            adj_list[node] = [n for n in adj_list[node] if n != node_index]
        del nodes[node_index]
        new_adj_list = {}
        for i, neighbors in adj_list.items():
            new_i = i - 1 if i > node_index else i
            new_neighbors = [n - 1 if n > node_index else n for n in neighbors]
            new_adj_list[new_i] = new_neighbors
        adj_list = new_adj_list
        edges[:] = [(u - 1 if u > node_index else u, v - 1 if v > node_index else v) for u, v in edges]
        initialize_adj_matrix()
    return adj_list


def delete_edge(node1, node2):
    if node1 in adj_list and node2 in adj_list[node1]:
        edges[:] = [edge for edge in edges if edge != (node1, node2) and edge != (node2, node1)]
        adj_list[node1].remove(node2)
        adj_list[node2].remove(node1)
        adjacency_matrix[node1][node2] = 0
        adjacency_matrix[node2][node1] = 0


def add_edge(node1, node2):
    if node1 != node2 and node2 not in adj_list[node1]:
        edges.append((node1, node2))
        adj_list[node1].append(node2)
        adj_list[node2].append(node1)
        adjacency_matrix[node1][node2] = 1
        adjacency_matrix[node2][node1] = 1


def start_bfs(start_node):
    global traversal_mode, traversal_start, traversal_visited, traversal_queue, traversal_path
    if start_node is not None:
        traversal_mode = "BFS"
        traversal_start = start_node
        traversal_visited = set()
        traversal_queue = [start_node]
        traversal_path = []


def perform_bfs_step():
    global traversal_queue, traversal_visited, traversal_path
    if traversal_queue:
        current = traversal_queue.pop(0)
        if current not in traversal_visited:
            traversal_visited.add(current)
            for neighbor in adj_list.get(current, []):
                if neighbor not in traversal_visited and neighbor not in traversal_queue:
                    traversal_queue.append(neighbor)
                    traversal_path.append((current, neighbor))
        return True
    return False


def start_dfs(start_node):
    global traversal_mode, traversal_start, traversal_visited, traversal_stack, traversal_path
    if start_node is not None:
        traversal_mode = "DFS"
        traversal_start = start_node
        traversal_visited = set()
        traversal_stack = [start_node]
        traversal_path = []


def perform_dfs_step():
    global traversal_stack, traversal_visited, traversal_path
    if traversal_stack:
        current = traversal_stack.pop()
        if current not in traversal_visited:
            traversal_visited.add(current)
            neighbors = sorted(adj_list.get(current, []), reverse=True)  # Process in reverse order for visualization
            for neighbor in neighbors:
                if neighbor not in traversal_visited:
                    traversal_stack.append(neighbor)
                    traversal_path.append((current, neighbor))
        return True
    return False


def toggle_matrix_cell(row, col):
    if row == col:  # Ignore diagonal (self-loops not supported)
        return

    # Toggle the cell value
    adjacency_matrix[row][col] = 1 - adjacency_matrix[row][col]
    adjacency_matrix[col][row] = adjacency_matrix[row][col]  # Keep symmetric for undirected graph

    # Update edges and adjacency list
    update_from_matrix()


def add_new_node():
    global nodes, adj_list, adjacency_matrix
    if len(nodes) < MAX_NODES:
        # Add node in the middle of the screen
        x = WIDTH // 2
        y = HEIGHT // 2 - 100
        nodes.append((x, y))
        node_idx = len(nodes) - 1
        adj_list[node_idx] = []
        initialize_adj_matrix()

def check_back_button(pos):
    return back_button_rect.collidepoint(pos)


running = True
while running:
    current_time = pygame.time.get_ticks()

    # Handle traversal animations (unchanged)
    if traversal_mode and current_time - last_traversal_time > traversal_delay:
        if traversal_mode == "BFS":
            if not perform_bfs_step():
                # BFS complete
                pass
        elif traversal_mode == "DFS":
            if not perform_dfs_step():
                # DFS complete
                pass
        last_traversal_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if active_text_input:
                if event.key == pygame.K_RETURN:
                    parse_adj_list_input(editing_row, edit_text)
                    active_text_input = False
                    edit_text = ""
                elif event.key == pygame.K_ESCAPE:
                    active_text_input = False
                    edit_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    edit_text = edit_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == ',':
                        edit_text += event.unicode
            else:
                if event.key == pygame.K_m and not traversal_mode:
                    show_matrix = not show_matrix
                    editing_matrix = False
                    editing_list = False
                    editing_row = None
                    matrix_cell = None
                elif event.key == pygame.K_e and not traversal_mode:
                    if show_matrix:
                        editing_matrix = not editing_matrix
                        editing_list = False
                    else:
                        editing_list = not editing_list
                        editing_matrix = False
                    editing_row = None
                    matrix_cell = None
                elif event.key == pygame.K_b and not traversal_mode:
                    if selected_node is not None:
                        start_bfs(selected_node)
                        selected_node = None
                    editing_matrix = False
                    editing_list = False
                elif event.key == pygame.K_d and not traversal_mode:
                    if selected_node is not None:
                        start_dfs(selected_node)
                        selected_node = None
                    editing_matrix = False
                    editing_list = False
                elif event.key == pygame.K_ESCAPE:
                    traversal_mode = None
                    traversal_start = None
                    traversal_visited = set()
                    traversal_queue = []
                    traversal_stack = []
                    traversal_path = []
                    editing_matrix = False
                    editing_list = False
                    editing_row = None
                    matrix_cell = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # NEW: If the back button is clicked, finish the program.
            if check_back_button(pos):
                running = False
                continue

            # Handle editing mode clicks
            if editing_matrix and event.button == 1:
                cell = check_matrix_cell_click(pos)
                if cell:
                    matrix_cell = cell
                    toggle_matrix_cell(cell[0], cell[1])
                continue

            if editing_list and event.button == 1:
                row = check_adj_list_row_click(pos)
                if row == "add_node":
                    add_new_node()
                elif row is not None and isinstance(row, int):
                    editing_row = row
                    neighbors = sorted(adj_list[row])
                    edit_text = ", ".join(map(str, neighbors))
                    active_text_input = True
                continue

            if traversal_mode:
                continue

            clicked_node = get_clicked_node(pos)
            if event.button == 1:  # Left click
                if clicked_node is not None:
                    if selected_node is None:
                        selected_node = clicked_node
                    else:
                        if (clicked_node != selected_node and
                            (selected_node, clicked_node) not in edges and
                            (clicked_node, selected_node) not in edges):
                            edges.append((selected_node, clicked_node))
                            adj_list.setdefault(selected_node, []).append(clicked_node)
                            adj_list.setdefault(clicked_node, []).append(selected_node)
                            initialize_adj_matrix()
                        selected_node = None
                else:
                    if len(nodes) < MAX_NODES and not is_in_adj_list_area(pos) and not check_back_button(pos):
                        nodes.append(pos)
                        adj_list[len(nodes) - 1] = []
                        initialize_adj_matrix()
            elif event.button == 3:  # Right click - Delete
                if clicked_node is not None:
                    if selected_node is None:
                        selected_node = clicked_node
                    else:
                        if (selected_node, clicked_node) in edges or (clicked_node, selected_node) in edges:
                            delete_edge(selected_node, clicked_node)
                        else:
                            adj_list = delete_node(clicked_node)
                        selected_node = None

        elif event.type == pygame.MOUSEMOTION:
            # Update back button active state (optional)
            back_button_active = check_back_button(event.pos)

    draw_graph()

pygame.quit()
sys.exit()