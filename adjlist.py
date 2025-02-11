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
        pygame.draw.circle(screen, BLUE, (x, y), NODE_RADIUS)
        text = font.render(str(i), True, WHITE)
        screen.blit(text, (x - 5, y - 7))

    y_offset = 10
    for node, neighbors in adj_list.items():
        adj_text = f"{node}: {', '.join(map(str, neighbors))}"
        text_surface = font.render(adj_text, True, BLACK)
        screen.blit(text_surface, (10, HEIGHT - 150 + y_offset))
        y_offset += 20

    pygame.display.flip()


def get_clicked_node(pos):
    x, y = pos
    for i, (nx, ny) in enumerate(nodes):
        if math.hypot(nx - x, ny - y) <= NODE_RADIUS:
            return i
    return None


font = pygame.font.Font(None, 24)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                node_index = get_clicked_node(event.pos)
                if node_index is not None:
                    if selected_node is None:
                        selected_node = node_index
                    else:
                        if node_index != selected_node and (selected_node, node_index) not in edges and (
                        node_index, selected_node) not in edges:
                            edges.append((selected_node, node_index))
                            adj_list.setdefault(selected_node, []).append(node_index)
                            adj_list.setdefault(node_index, []).append(selected_node)
                        selected_node = None
                else:
                    nodes.append(event.pos)
                    adj_list[len(nodes) - 1] = []
                    selected_node = None

    draw_graph()

pygame.quit()
sys.exit()
