import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (150, 150, 150)
MAX_NODES = 7
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Graph Visualization")

nodes = []
edges = []
adj_list = {}

selected_node = None


def draw_graph():
    screen.fill(WHITE)

    for edge in edges:
        pygame.draw.line(screen, BLACK, nodes[edge[0]], nodes[edge[1]], 2)

    for i, (x, y) in enumerate(nodes):
        color = RED if i == selected_node else BLUE
        pygame.draw.circle(screen, color, (x, y), NODE_RADIUS)
        text = font.render(str(i), True, WHITE)
        screen.blit(text, (x - 5, y - 7))

    pygame.draw.rect(screen, GRAY, (10, HEIGHT - 310, 250, 300))
    title = font.render("Adjacency List:", True, BLACK)
    screen.blit(title, (20, HEIGHT - 280))

    y_offset = 35
    for node in sorted(adj_list.keys()):
        neighbors = sorted(adj_list[node])
        adj_text = f"{node}: [{', '.join(map(str, neighbors))if neighbors else 'None'}]"
        text_surface = font.render(adj_text, True, BLACK)
        screen.blit(text_surface, (20, HEIGHT - 280 + y_offset))
        y_offset += 35

    instructions = [
        f"Left Click: Add node/edge ({len(nodes)}/{MAX_NODES})",
        "Right Click: Delete node/edge",
        "Red: Selected node"
    ]
    for i, text in enumerate(instructions):
        instruction = small_font.render(text, True, BLACK)
        screen.blit(instruction, (WIDTH - 200, 10 + i * 20))

    pygame.display.flip()


def get_clicked_node(pos):
    x, y = pos
    for i, (nx, ny) in enumerate(nodes):
        if math.hypot(nx - x, ny - y) <= NODE_RADIUS:
            return i
    return None


def is_in_adj_list_area(pos):
    x, y = pos
    return (10 <= x <= 260) and (HEIGHT - 310 <= y <= HEIGHT - 10)

def delete_node(node_index):
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
        edges[:] = [(u - 1 if u > node_index else u, v - 1 if v > node_index else v) for u, v in edges]
        return new_adj_list
    return adj_list


def delete_edge(node1, node2):
    if node1 in adj_list and node2 in adj_list[node1]:
        edges[:] = [edge for edge in edges if edge != (node1, node2) and edge != (node2, node1)]
        adj_list[node1].remove(node2)
        adj_list[node2].remove(node1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            pos = event.pos
            clicked_node = get_clicked_node(pos)

            if event.button == 1:
                if clicked_node is not None:
                    if selected_node is None:
                        selected_node = clicked_node
                    else:
                        if clicked_node != selected_node and (selected_node, clicked_node) not in edges and (clicked_node, selected_node) not in edges:
                            edges.append((selected_node, clicked_node))
                            adj_list.setdefault(selected_node, []).append(clicked_node)
                            adj_list.setdefault(clicked_node, []).append(selected_node)
                        selected_node = None
                else:
                    if len(nodes) < MAX_NODES and not is_in_adj_list_area(pos):  # Check node limit and position
                        nodes.append(pos)
                    adj_list[len(nodes) - 1] = []
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

    draw_graph()

pygame.quit()
sys.exit()
