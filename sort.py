import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 900, 500
CARD_WIDTH, CARD_HEIGHT = 60, 100
GAP = 20
WHITE, BLACK, RED, GREEN, BLUE, GRAY = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (200, 200, 200)

# Button constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_X_reset = WINDOW_WIDTH - BUTTON_WIDTH - 20
BUTTON_Y_reset = WINDOW_HEIGHT - BUTTON_HEIGHT - 20
BUTTON_X_selection = WINDOW_WIDTH - 2*BUTTON_WIDTH - 40
BUTTON_Y_selection = WINDOW_HEIGHT - BUTTON_HEIGHT - 20

BUTTON_COLOR = (100, 100, 200)
BUTTON_HOVER_COLOR = (120, 120, 220)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_TEXT_reset = "Reset/Shuffle"
BUTTON_TEXT_selection = "Selection Sort"






# Setup the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sorting Visualization")
font = pygame.font.Font(None, 36)

# Generate shuffled list of numbers
num_cards = 8
def shuffle_values():
    global values
    values = list(range(1, num_cards + 1))
    random.shuffle(values)
shuffle_values()

positions = [(i * (CARD_WIDTH + GAP) + 50, WINDOW_HEIGHT // 2 - CARD_HEIGHT // 2) for i in range(num_cards)]

def draw_cards(highlight_index=None, swap_index=None):
    screen.fill(WHITE)
    for i, val in enumerate(values):
        x, y = positions[i]
        color = GREEN if i == highlight_index else RED if i == swap_index else BLUE
        pygame.draw.rect(screen, color, (x, y, CARD_WIDTH, CARD_HEIGHT))
        text = font.render(str(val), True, WHITE)
        screen.blit(text, (x + CARD_WIDTH // 3, y + CARD_HEIGHT // 3))
    draw_buttons()
    pygame.display.update()

def draw_buttons():
    buttons = [("Selection Sort", 50), ("Bubble Sort", 300), ("Insertion Sort", 550), ("Shuffle", 750)]
    for text, x in buttons:
        pygame.draw.rect(screen, GRAY, (x, 400, 200, 50))
        label = font.render(text, True, BLACK)
        screen.blit(label, (x + 10, 410))

def selection_sort_visual():
    for i in range(len(values)):
        min_idx = i
        draw_cards(highlight_index=i)
        time.sleep(0.5)
        for j in range(i + 1, len(values)):
            draw_cards(highlight_index=i, swap_index=j)
            time.sleep(0.5)
            if values[j] < values[min_idx]:
                min_idx = j
        values[i], values[min_idx] = values[min_idx], values[i]
        draw_cards()
        time.sleep(0.5)

def bubble_sort_visual():
    for i in range(len(values)):
        for j in range(len(values) - i - 1):
            draw_cards(highlight_index=j, swap_index=j + 1)
            time.sleep(0.5)
            if values[j] > values[j + 1]:
                values[j], values[j + 1] = values[j + 1], values[j]
                draw_cards()
                time.sleep(0.5)

def insertion_sort_visual():
    for i in range(1, len(values)):
        key = values[i]
        j = i - 1
        while j >= 0 and key < values[j]:
            draw_cards(highlight_index=j, swap_index=j + 1)
            time.sleep(0.5)
            values[j + 1] = values[j]
            j -= 1
        values[j + 1] = key
        draw_cards()
        time.sleep(0.5)

def draw_button(button_x, button_y, button_text, hover=False):
    color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, (button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT), border_radius=5)
    
    text_surface = font.render(button_text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(button_x + BUTTON_WIDTH // 2, button_y + BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def is_button_hovered(pos, button_x, button_y):
    x, y = pos
    return button_x <= x <= button_x + BUTTON_WIDTH and button_y <= y <= button_y + BUTTON_HEIGHT





running = True
clock = pygame.time.Clock()
button_hover_selection = False
button_hover_insertion = False
button_hover_bubble = False
button_hover_reset = False


while running:
    mouse_pos = pygame.mouse.get_pos()

    button_hover_reset = is_button_hovered(mouse_pos, BUTTON_X_reset, BUTTON_Y_reset)
    button_hover_selection = is_button_hovered(mouse_pos, BUTTON_X_selection, BUTTON_Y_selection)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_hover_reset:
                shuffle_values()
                draw_cards()
            elif button_hover_selection:
                selection_sort_visual()
    screen.fill(WHITE)
    draw_cards()
    draw_button(BUTTON_X_reset, BUTTON_Y_reset, BUTTON_TEXT_reset, button_hover_reset)
    draw_button(BUTTON_X_selection, BUTTON_Y_selection, BUTTON_TEXT_selection, button_hover_selection)


    # Update the display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(10)


pygame.quit()

