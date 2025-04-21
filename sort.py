import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CARD_WIDTH = 40
CARD_HEIGHT = 60
CARD_SPACING = 10
NUM_CARDS = 15
CARD_START_X = (WIDTH - (NUM_CARDS * (CARD_WIDTH + CARD_SPACING))) // 2
CARD_Y = HEIGHT // 2 - CARD_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.active_color = color
        self.font = pygame.font.SysFont('Arial', 16)
        
    def draw(self, screen, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.active_color
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_text(self, new_text):
        self.text = new_text

# Slider class for speed control
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.handle_radius = height * 1.5
        self.dragging = False
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Calculate handle position
        self.update_handle_pos()
    
    def update_handle_pos(self):
        # Map value to position
        val_range = self.max_val - self.min_val
        pos_range = self.rect.width
        
        rel_val = self.value - self.min_val
        rel_pos = (rel_val / val_range) * pos_range
        
        self.handle_pos = self.rect.left + rel_pos
    
    def draw(self, screen):
        # Draw track
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)
        
        # Draw handle
        pygame.draw.circle(screen, BLACK, (int(self.handle_pos), self.rect.centery), int(self.handle_radius))
        pygame.draw.circle(screen, WHITE, (int(self.handle_pos), self.rect.centery), int(self.handle_radius - 2))
        
        # Draw label and value
        label_text = self.font.render(f"{self.label}: {self.value:.1f}", True, BLACK)
        label_rect = label_text.get_rect(midleft=(self.rect.left, self.rect.top - 15))
        screen.blit(label_text, label_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if handle is clicked
            handle_rect = pygame.Rect(
                self.handle_pos - self.handle_radius, 
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2, self.handle_radius * 2
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update handle position and value
            rel_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.handle_pos = rel_x
            
            # Map position to value
            rel_pos = rel_x - self.rect.left
            pos_range = self.rect.width
            val_range = self.max_val - self.min_val
            
            self.value = self.min_val + (rel_pos / pos_range) * val_range
            return True  # Value changed
        
        return False  # Value not changed

# Card class
class Card:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.color = WHITE
        self.font = pygame.font.SysFont('Arial', 24)
        self.highlighted = False  # For search target highlighting
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # For search target highlighting (draw thicker border)
        if self.highlighted:
            pygame.draw.rect(screen, ORANGE, self.rect, 4)
        
        text_surf = self.font.render(str(self.value), True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

# TargetCard class for showing search target
class TargetCard:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.width = CARD_WIDTH + 10  # Slightly larger than regular cards
        self.height = CARD_HEIGHT + 10
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = ORANGE
        self.font = pygame.font.SysFont('Arial', 24)
        self.label_font = pygame.font.SysFont('Arial', 18)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0, 5)  # Rounded corners
        pygame.draw.rect(screen, BLACK, self.rect, 2, 5)
        
        # Draw label
        label = self.label_font.render("Target:", True, BLACK)
        label_rect = label.get_rect(center=(self.x + self.width // 2, self.y - 15))
        screen.blit(label, label_rect)
        
        # Draw value
        text_surf = self.font.render(str(self.value), True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def update_value(self, value):
        self.value = value

# SortVisualizer class
class SortVisualizer:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sorting and Searching Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        
        # Create cards
        self.reset_cards()
        
        # Control flags
        self.current_algorithm = None
        self.algorithm_running = False
        self.paused = False
        self.step_mode = False
        self.step_ready = False
        self.delay_frames = 0
        self.frame_counter = 0
        self.delay_time = 0.5  # seconds between steps
        self.last_step_time = time.time()
        
        # Create algorithm generators
        self.algorithm_generator = None
        self.current_step = None
        
        # Search-related variables
        self.search_value = random.randint(1, NUM_CARDS)
        self.search_result = None
        self.target_card = TargetCard(self.search_value, WIDTH - 100, 70)
        self.show_target_card = False
        
        # For insertion sort animation
        self.moving_card = None
        self.insertion_key_idx = None
        
        # Create buttons
        button_width, button_height = 120, 40
        button_spacing = 10
        button_y = HEIGHT - 140
        
        # Main algorithm buttons
        self.buttons = []
        algorithms = ["Bubble Sort", "Insertion Sort", "Selection Sort", "Quick Sort"]
        colors = [CYAN, YELLOW, GREEN, PURPLE]
        
        total_width = len(algorithms) * button_width + (len(algorithms) - 1) * button_spacing
        start_x = (WIDTH - total_width) // 2
        
        for i, (algo, color) in enumerate(zip(algorithms, colors)):
            btn_x = start_x + i * (button_width + button_spacing)
            self.buttons.append(Button(btn_x, button_y, button_width, button_height, algo, color))
        
        # Search buttons
        button_y += button_height + 20
        search_algorithms = ["Linear Search", "Binary Search", "Reset"]
        search_colors = [ORANGE, BLUE, RED]
        
        total_width = len(search_algorithms) * button_width + (len(search_algorithms) - 1) * button_spacing
        start_x = (WIDTH - total_width) // 2
        
        for i, (algo, color) in enumerate(zip(search_algorithms, search_colors)):
            btn_x = start_x + i * (button_width + button_spacing)
            self.buttons.append(Button(btn_x, button_y, button_width, button_height, algo, color))
        
        # Control buttons
        button_y += button_height + 20
        self.control_buttons = [
            Button(WIDTH // 2 - button_width - button_spacing, button_y, button_width, button_height, "Pause", RED),
            Button(WIDTH // 2 + button_spacing, button_y, button_width, button_height, "Step", BLUE)
        ]
        
        # Speed slider
        slider_width = 200
        slider_height = 8
        slider_x = (WIDTH - slider_width) // 2
        slider_y = button_y + button_height + 30
        self.speed_slider = Slider(slider_x, slider_y, slider_width, slider_height, 0.1, 2.0, 0.5, "Speed (seconds)")

    def reset_cards(self):
        self.cards = []
        values = list(range(1, NUM_CARDS + 1))
        random.shuffle(values)
        
        for i, value in enumerate(values):
            x = CARD_START_X + i * (CARD_WIDTH + CARD_SPACING)
            self.cards.append(Card(value, x, CARD_Y))
        
        # Reset card colors and highlighting
        for card in self.cards:
            card.color = WHITE
            card.highlighted = False
        
        # Reset moving card for insertion sort
        self.moving_card = None
        self.insertion_key_idx = None
            
    def set_card_positions(self):
        for i, card in enumerate(self.cards):
            x = CARD_START_X + i * (CARD_WIDTH + CARD_SPACING)
            card.set_position(x, CARD_Y)
    
    def highlight_search_targets(self):
        # Reset all highlights
        for card in self.cards:
            card.highlighted = False
        
        # Highlight cards with the search value
        for card in self.cards:
            if card.value == self.search_value:
                card.highlighted = True
    
    def bubble_sort_generator(self):
        n = len(self.cards)
        
        for i in range(n):
            swapped = False
            
            for j in range(0, n - i - 1):
                # Highlight cards being compared
                self.cards[j].color = BLUE
                self.cards[j+1].color = BLUE
                yield "comparing"
                
                if self.cards[j].value > self.cards[j+1].value:
                    # Highlight cards being swapped
                    self.cards[j].color = RED
                    self.cards[j+1].color = RED
                    yield "swapping"
                    
                    # Swap cards
                    self.cards[j], self.cards[j+1] = self.cards[j+1], self.cards[j]
                    self.set_card_positions()
                    swapped = True
                    yield "swapped"
                
                # Reset colors
                self.cards[j].color = WHITE
                self.cards[j+1].color = WHITE
            
            # Mark the last item as sorted
            self.cards[n-i-1].color = GREEN
            
            if not swapped:
                break
        
        # Mark all remaining cards as sorted
        for card in self.cards:
            card.color = GREEN
    
    def insertion_sort_generator(self):
        n = len(self.cards)
        
        for i in range(1, n):
            # Store the key card and its index
            key_card = self.cards[i]
            self.insertion_key_idx = i
            self.moving_card = Card(key_card.value, key_card.x, key_card.y)
            self.moving_card.color = BLUE
            key_card.color = BLUE
            yield "selected key"
            
            j = i - 1
            key_value = key_card.value
            
            while j >= 0 and self.cards[j].value > key_value:
                self.cards[j].color = RED
                yield "comparing"
                
                # Move larger element to the right, but keep key card visible
                self.cards[j+1] = self.cards[j]
                j -= 1
                
                # Update positions but keep moving card
                self.set_card_positions()
                # Update moving card position to follow along
                self.moving_card.set_position(
                    CARD_START_X + (j+1) * (CARD_WIDTH + CARD_SPACING),
                    CARD_Y - 20  # Slightly above other cards
                )
                yield "moved"
                
                # Reset color
                if j+1 < len(self.cards):
                    self.cards[j+1].color = WHITE
            
            # Place key card in the right position
            self.cards[j+1] = key_card
            key_card.color = GREEN
            self.set_card_positions()
            self.moving_card = None  # Clear moving card
            self.insertion_key_idx = None
            yield "inserted"
            
            # Mark sorted portion
            for k in range(i+1):
                self.cards[k].color = GREEN
        
        # Mark all cards as sorted
        for card in self.cards:
            card.color = GREEN
    
    def selection_sort_generator(self):
        n = len(self.cards)
        
        for i in range(n):
            min_idx = i
            self.cards[i].color = BLUE  # Current position
            yield "current position"
            
            for j in range(i+1, n):
                self.cards[j].color = YELLOW  # Currently checking
                yield "checking"
                
                if self.cards[j].value < self.cards[min_idx].value:
                    # Reset old min color
                    if min_idx != i:
                        self.cards[min_idx].color = WHITE
                    
                    min_idx = j
                    self.cards[min_idx].color = RED  # New minimum
                    yield "new minimum"
                else:
                    self.cards[j].color = WHITE  # Reset checking color
            
            # Swap the found minimum element with the first element
            if min_idx != i:
                self.cards[i].color = RED
                yield "ready to swap"
                
                self.cards[i], self.cards[min_idx] = self.cards[min_idx], self.cards[i]
                self.set_card_positions()
                yield "swapped"
            
            # Mark as sorted
            self.cards[i].color = GREEN
            
            # Reset any other colored cards
            for j in range(i+1, n):
                self.cards[j].color = WHITE
        
        # Mark all cards as sorted
        for card in self.cards:
            card.color = GREEN
    
    def quick_sort_generator(self):
        # Helper function for quicksort
        def _quick_sort(start, end):
            if start < end:
                # Get pivot index and sort around pivot
                pivot_idx = yield from _partition(start, end)
                
                # Recursively sort elements before and after partition
                yield from _quick_sort(start, pivot_idx - 1)
                yield from _quick_sort(pivot_idx + 1, end)
        
        def _partition(start, end):
            # Using last element as pivot
            pivot_value = self.cards[end].value
            self.cards[end].color = PURPLE  # Pivot color
            yield "pivot selected"
            
            i = start - 1  # Index of smaller element
            
            for j in range(start, end):
                self.cards[j].color = BLUE  # Currently examining
                yield "examining"
                
                # If current element is smaller than or equal to pivot
                if self.cards[j].value <= pivot_value:
                    i += 1
                    
                    if i != j:
                        self.cards[i].color = RED
                        self.cards[j].color = RED
                        yield "swapping"
                        
                        # Swap
                        self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
                        self.set_card_positions()
                        yield "swapped"
                
                # Reset colors
                for idx in range(start, end + 1):
                    if idx != end:  # Keep pivot color
                        self.cards[idx].color = WHITE
            
            # Swap the pivot element
            if i + 1 != end:
                self.cards[i + 1].color = RED
                yield "swapping pivot"
                
                self.cards[i + 1], self.cards[end] = self.cards[end], self.cards[i + 1]
                self.set_card_positions()
            
            # Mark pivot in its final position
            self.cards[i + 1].color = GREEN
            yield "pivot placed"
            
            return i + 1
        
        # Start the quicksort
        yield from _quick_sort(0, len(self.cards) - 1)
        
        # Mark all cards as sorted
        for card in self.cards:
            card.color = GREEN
    
    def linear_search_generator(self):
        target = self.search_value
        n = len(self.cards)
        
        # Reset result
        self.search_result = None
        
        # Reset card colors
        for card in self.cards:
            card.color = WHITE
        
        # Highlight all cards with the target value
        self.highlight_search_targets()
        
        for i in range(n):
            self.cards[i].color = BLUE  # Currently examining
            yield f"examining card {i+1}"
            
            if self.cards[i].value == target:
                self.cards[i].color = GREEN  # Found
                self.search_result = i
                yield f"found at position {i}"
                return
            else:
                self.cards[i].color = RED  # Not a match
                yield f"not a match"
                
                # Keep previous cards red to show they've been checked
        
        # Not found
        yield "target not found"
        self.search_result = -1
    
    def binary_search_generator(self):
        target = self.search_value
        
        # Check if array is sorted
        is_sorted = all(self.cards[i].value <= self.cards[i+1].value for i in range(len(self.cards)-1))
        
        if not is_sorted:
            # Sort the cards first
            self.cards.sort(key=lambda card: card.value)
            self.set_card_positions()
            yield "sorting array first"
        
        # Reset card colors
        for card in self.cards:
            card.color = WHITE
        
        # Highlight all cards with the target value
        self.highlight_search_targets()
        
        # Reset result
        self.search_result = None
        
        left, right = 0, len(self.cards) - 1
        
        while left <= right:
            # Color the current search range
            for i in range(len(self.cards)):
                if left <= i <= right:
                    self.cards[i].color = YELLOW
                else:
                    self.cards[i].color = GRAY
            
            yield "search range"
            
            mid = (left + right) // 2
            self.cards[mid].color = BLUE
            yield f"checking middle element at position {mid}"
            
            if self.cards[mid].value == target:
                self.cards[mid].color = GREEN
                self.search_result = mid
                yield f"found at position {mid}"
                return
            elif self.cards[mid].value < target:
                self.cards[mid].color = RED
                yield f"target is larger, searching right half"
                left = mid + 1
            else:
                self.cards[mid].color = RED
                yield f"target is smaller, searching left half"
                right = mid - 1
        
        # Not found
        yield "target not found"
        self.search_result = -1
    
    def start_algorithm(self, algorithm_name):
        self.reset_cards()
        self.current_algorithm = algorithm_name
        self.algorithm_running = True
        self.paused = False
        self.step_mode = False
        self.step_ready = False
        self.search_result = None
        
        # Show target card for search algorithms
        self.show_target_card = "search" in algorithm_name
        
        if algorithm_name == "bubble":
            self.algorithm_generator = self.bubble_sort_generator()
        elif algorithm_name == "insertion":
            self.algorithm_generator = self.insertion_sort_generator()
        elif algorithm_name == "selection":
            self.algorithm_generator = self.selection_sort_generator()
        elif algorithm_name == "quick":
            self.algorithm_generator = self.quick_sort_generator()
        elif algorithm_name == "linear" or algorithm_name == "binary":
            self.search_value = random.randint(1, NUM_CARDS)
            self.target_card.update_value(self.search_value)
            
            if algorithm_name == "linear":
                self.algorithm_generator = self.linear_search_generator()
            else:
                self.algorithm_generator = self.binary_search_generator()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle slider events
            if self.speed_slider.handle_event(event):
                self.delay_time = self.speed_slider.value
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Check main buttons
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(pos):
                        if i == 0:  # Bubble Sort
                            self.start_algorithm("bubble")
                        elif i == 1:  # Insertion Sort
                            self.start_algorithm("insertion")
                        elif i == 2:  # Selection Sort
                            self.start_algorithm("selection")
                        elif i == 3:  # Quick Sort
                            self.start_algorithm("quick")
                        elif i == 4:  # Linear Search
                            self.start_algorithm("linear")
                        elif i == 5:  # Binary Search
                            self.start_algorithm("binary")
                        elif i == 6:  # Reset
                            self.reset_cards()
                            self.algorithm_running = False
                            self.paused = False
                            self.current_algorithm = None
                            self.algorithm_generator = None
                            self.search_result = None
                            self.show_target_card = False
                
                # Check control buttons
                for i, button in enumerate(self.control_buttons):
                    if button.is_clicked(pos):
                        if i == 0:  # Pause/Resume
                            if self.algorithm_running:
                                self.paused = not self.paused
                                button.update_text("Resume" if self.paused else "Pause")
                        elif i == 1:  # Step
                            if self.algorithm_running:
                                if self.paused:
                                    self.step_ready = True
                                else:
                                    self.paused = True
                                    self.step_ready = True
                                    self.control_buttons[0].update_text("Resume")
    
    def update(self):
        current_time = time.time()
        
        if self.algorithm_running and self.algorithm_generator:
            if not self.paused or (self.paused and self.step_ready):
                if self.step_ready or (current_time - self.last_step_time >= self.delay_time):
                    try:
                        self.current_step = next(self.algorithm_generator)
                        self.step_ready = False
                        self.last_step_time = current_time
                    except StopIteration:
                        self.algorithm_running = False
                        self.paused = False
                        self.current_algorithm = None
                        self.algorithm_generator = None
                        self.control_buttons[0].update_text("Pause")
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen)
        
        # Draw moving card for insertion sort if present
        if self.moving_card:
            self.moving_card.draw(self.screen)
        
        # Draw target card for search if needed
        if self.show_target_card:
            self.target_card.draw(self.screen)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(self.screen, mouse_pos)
        
        for button in self.control_buttons:
            button.draw(self.screen, mouse_pos)
        
        # Draw slider
        self.speed_slider.draw(self.screen)
        
        # Draw current algorithm name and info
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 20)
        
        if self.current_algorithm:
            algorithm_names = {
                "bubble": "Bubble Sort",
                "insertion": "Insertion Sort",
                "selection": "Selection Sort",
                "quick": "Quick Sort",
                "linear": "Linear Search",
                "binary": "Binary Search"
            }
            algorithm_text = font.render(f"Algorithm: {algorithm_names[self.current_algorithm]}", True, BLACK)
            self.screen.blit(algorithm_text, (WIDTH // 2 - algorithm_text.get_width() // 2, 30))
            
            # Draw step info
            if self.current_step:
                step_text = small_font.render(f"Step: {self.current_step}", True, BLACK)
                self.screen.blit(step_text, (WIDTH // 2 - step_text.get_width() // 2, 70))
            
            # Draw mode info
            if self.paused:
                mode_text = small_font.render("Status: Paused", True, RED)
            else:
                mode_text = small_font.render("Status: Running", True, GREEN)
            
            self.screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 100))
            
            # Draw search info if applicable
            if "search" in self.current_algorithm:
                if self.search_result is not None:
                    if self.search_result >= 0:
                        result_text = small_font.render(f"Found at position: {self.search_result}", True, GREEN)
                    else:
                        result_text = small_font.render("Value not found in array", True, RED)
                    
                    self.screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 130))
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

# Main
if __name__ == "__main__":
    visualizer = SortVisualizer()
    visualizer.run()