import pygame
import sys
import random
import math
from typing import List, Dict, Set, Tuple

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 900  # Increased window size
BACKGROUND_COLOR = (50, 120, 50)  # Dark green (card table)
SET_COLORS = {
    "Hearts": (218, 41, 28, 160),  # Red with alpha
    "Diamonds": (218, 41, 28, 160),  # Red with alpha
    "Clubs": (20, 20, 20, 160),  # Black with alpha
    "Spades": (20, 20, 20, 160),  # Black with alpha
    "Red": (218, 41, 28, 160),  # Red with alpha
    "Black": (20, 20, 20, 160),  # Black with alpha
    "Face": (148, 0, 211, 160),  # Purple with alpha
    "Number": (30, 144, 255, 160),  # Blue with alpha
}
INTERSECTION_COLOR = (80, 80, 80, 180)  # Dark gray with alpha
TEXT_COLOR = (240, 240, 240)  # Light text for dark background
CARD_COLOR = (255, 255, 255)  # White for cards
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Card Deck Set Theory Visualization")

# Fonts
title_font = pygame.font.SysFont('Arial', 28, bold=True)
regular_font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 14)
card_font = pygame.font.SysFont('Arial', 16, bold=True)

# Card suit symbols
SUIT_SYMBOLS = {
    "Hearts": "♥",
    "Diamonds": "♦",
    "Clubs": "♣",
    "Spades": "♠"
}

# Card values
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
FACE_CARDS = ["J", "Q", "K", "A"]


class Card:
    """Class representing a playing card"""

    def __init__(self, suit: str, value: str, x: float, y: float, width: int = 50,
                 height: int = 70):  # Slightly larger cards
        self.suit = suit
        self.value = value
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dragging = False
        self.hover = False
        self.highlighted = False

        # Determine card color and other properties
        self.color = "Red" if suit in ["Hearts", "Diamonds"] else "Black"
        self.is_face = value in FACE_CARDS
        self.is_number = value not in FACE_CARDS or value == "A"  # A can be both

        # Set memberships
        self.sets = {suit, self.color}
        if self.is_face:
            self.sets.add("Face")
        if self.is_number:
            self.sets.add("Number")

    def get_display_text(self) -> str:
        """Get the text to display on the card"""
        return f"{self.value}{SUIT_SYMBOLS[self.suit]}"

    def draw(self, screen):
        # Determine card background color
        bg_color = CARD_COLOR
        text_color = (0, 0, 0)  # Default black text

        # If card is from Hearts or Diamonds, use red text
        if self.suit in ["Hearts", "Diamonds"]:
            text_color = (218, 41, 28)

        # Draw highlight if highlighted
        if self.highlighted or self.hover:
            highlight_rect = pygame.Rect(self.x - 3, self.y - 3, self.width + 6, self.height + 6)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlight_rect, border_radius=3)

        # Draw card background
        card_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 100), card_rect, 1, border_radius=3)

        # Draw card text
        text = self.get_display_text()
        text_surface = card_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_point_inside(self, point_x, point_y) -> bool:
        """Check if a point is inside this card"""
        return (self.x <= point_x <= self.x + self.width and
                self.y <= point_y <= self.y + self.height)


class Button:
    """Class for interactive buttons"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, action, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hover = False
        self.active = False
        self.color = color

    def draw(self, screen):
        # Button background
        if self.active and self.color:
            bg_color = self.color
            text_color = (240, 240, 240)  # White text for colored buttons
        else:
            bg_color = (180, 180, 180) if self.hover else (200, 200, 200)
            text_color = (0, 0, 0)  # Black text for normal buttons

        if self.hover:
            bg_color = tuple(max(0, c - 20) for c in bg_color)  # Darken on hover

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2, border_radius=5)

        # Button text
        text_surface = small_font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_point_inside(self, point_x, point_y) -> bool:
        return self.rect.collidepoint(point_x, point_y)


class SetIndicator:
    """Class representing a set indicator"""

    def __init__(self, name: str, x: int, y: int, width: int, height: int, color):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.active = False

    def draw(self, screen):
        # Draw the indicator rectangle
        alpha_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        if self.active:
            # Full color when active
            pygame.draw.rect(alpha_surface, self.color,
                             (0, 0, self.rect.width, self.rect.height), border_radius=5)
        else:
            # Gray with outline when inactive
            pygame.draw.rect(alpha_surface, (150, 150, 150, 120),
                             (0, 0, self.rect.width, self.rect.height), border_radius=5)

        # Always draw a border
        pygame.draw.rect(alpha_surface, (100, 100, 100),
                         (0, 0, self.rect.width, self.rect.height), 2, border_radius=5)

        screen.blit(alpha_surface, self.rect)

        # Draw the set name
        text_surface = small_font.render(self.name, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class DifferenceSelector:
    """A selector for choosing which sets to use in difference operations"""

    def __init__(self, active_sets):
        self.active_sets = active_sets
        self.selected_set_index = 0 if active_sets else -1
        self.is_open = False

        # Set up selector UI elements
        self.base_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 300)
        self.title_rect = pygame.Rect(self.base_rect.x, self.base_rect.y, self.base_rect.width, 40)

        # Create "Set A" buttons (what to subtract from)
        self.set_a_buttons = []
        self.create_set_buttons()

        # Create "Set B" buttons (what to subtract)
        self.set_b_buttons = []
        self.create_set_buttons(is_set_a=False)

        # Create control buttons
        button_width, button_height = 100, 30

        self.apply_button = Button(
            self.base_rect.centerx - button_width - 10,
            self.base_rect.bottom - button_height - 20,
            button_width, button_height,
            "Apply", self.apply
        )

        self.cancel_button = Button(
            self.base_rect.centerx + 10,
            self.base_rect.bottom - button_height - 20,
            button_width, button_height,
            "Cancel", self.cancel
        )

        # Selected sets
        self.selected_set_a = None
        self.selected_set_b = None

    def create_set_buttons(self, is_set_a=True):
        """Create buttons for the sets"""
        button_width, button_height = 100, 30
        button_margin = 10

        # Position and create buttons
        if is_set_a:
            title_y = self.title_rect.bottom + 10
            title_text = "Select Set A (to subtract from):"
        else:
            title_y = self.title_rect.bottom + 110  # Position below Set A section
            title_text = "Select Set B (to subtract):"

        buttons_per_row = 3
        buttons_container = []

        for i, set_name in enumerate(self.active_sets):
            row = i // buttons_per_row
            col = i % buttons_per_row

            btn_x = self.base_rect.x + 20 + col * (button_width + button_margin)
            btn_y = title_y + 30 + row * (button_height + button_margin)

            if is_set_a:
                action = lambda s=set_name: self.select_set_a(s)
            else:
                action = lambda s=set_name: self.select_set_b(s)

            btn = Button(btn_x, btn_y, button_width, button_height, set_name, action,
                         SET_COLORS.get(set_name, (150, 150, 150, 160)))

            if is_set_a:
                self.set_a_buttons.append(btn)
            else:
                self.set_b_buttons.append(btn)

    def select_set_a(self, set_name):
        """Select a set as Set A"""
        self.selected_set_a = set_name
        # Update button states
        for btn in self.set_a_buttons:
            btn.active = btn.text == set_name

    def select_set_b(self, set_name):
        """Select a set as Set B"""
        self.selected_set_b = set_name
        # Update button states
        for btn in self.set_b_buttons:
            btn.active = btn.text == set_name

    def apply(self):
        """Apply the difference operation with selected sets"""
        self.is_open = False
        # Return selected sets so CardSetVisualization can use them
        return self.selected_set_a, self.selected_set_b

    def cancel(self):
        """Cancel the difference operation"""
        self.is_open = False
        return None, None

    def show(self):
        """Show the difference selector dialog"""
        self.is_open = True
        # Reset selections
        self.selected_set_a = None
        self.selected_set_b = None
        # Reset button states
        for btn in self.set_a_buttons + self.set_b_buttons:
            btn.active = False

    def handle_event(self, event):
        """Handle pygame events"""
        if not self.is_open:
            return False

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Handle mouse movement for hover effects
        if event.type == pygame.MOUSEMOTION:
            for btn in self.set_a_buttons + self.set_b_buttons + [self.apply_button, self.cancel_button]:
                btn.hover = btn.is_point_inside(mouse_x, mouse_y)

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check Set A buttons
                for btn in self.set_a_buttons:
                    if btn.is_point_inside(mouse_x, mouse_y):
                        btn.action()
                        return True

                # Check Set B buttons
                for btn in self.set_b_buttons:
                    if btn.is_point_inside(mouse_x, mouse_y):
                        btn.action()
                        return True

                # Check control buttons
                if self.apply_button.is_point_inside(mouse_x, mouse_y):
                    if self.selected_set_a and self.selected_set_b:
                        self.apply_button.action()
                        return True

                if self.cancel_button.is_point_inside(mouse_x, mouse_y):
                    self.cancel_button.action()
                    return True

        return True  # Event was handled

    def draw(self, screen):
        """Draw the difference selector dialog"""
        if not self.is_open:
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Draw dialog background
        pygame.draw.rect(screen, (80, 80, 80), self.base_rect, border_radius=5)
        pygame.draw.rect(screen, (40, 40, 40), self.title_rect, border_radius=5)

        # Draw dialog title
        title_text = title_font.render("Select Sets for Difference", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=self.title_rect.center)
        screen.blit(title_text, title_rect)

        # Draw set A section title
        set_a_title = regular_font.render("Select Set A (to subtract from):", True, TEXT_COLOR)
        screen.blit(set_a_title, (self.base_rect.x + 20, self.title_rect.bottom + 10))

        # Draw set B section title
        set_b_title = regular_font.render("Select Set B (to subtract):", True, TEXT_COLOR)
        screen.blit(set_b_title, (self.base_rect.x + 20, self.title_rect.bottom + 110))

        # Draw all buttons
        for btn in self.set_a_buttons + self.set_b_buttons + [self.apply_button, self.cancel_button]:
            btn.draw(screen)

        # Draw operation preview
        if self.selected_set_a and self.selected_set_b:
            preview_text = f"Operation: {self.selected_set_a} - {self.selected_set_b}"
            preview_surface = regular_font.render(preview_text, True, TEXT_COLOR)
            preview_rect = preview_surface.get_rect(
                center=(self.base_rect.centerx, self.base_rect.bottom - 70)
            )
            screen.blit(preview_surface, preview_rect)
        else:
            # Display instruction if sets are not selected
            instruction = "Select both sets to perform difference operation"
            instruction_surface = small_font.render(instruction, True, (200, 200, 200))
            instruction_rect = instruction_surface.get_rect(
                center=(self.base_rect.centerx, self.base_rect.bottom - 70)
            )
            screen.blit(instruction_surface, instruction_rect)


class CardSetVisualization:
    """Main class handling the card set theory visualization"""

    def __init__(self):
        # Set up active sets
        self.active_set_names = ["Hearts", "Diamonds", "Clubs", "Spades"]

        # Set up cards (initially empty)
        self.cards: List[Card] = []

        # Set up operation display
        self.current_operation = "Card Sets"
        self.operation_result = "Interact to see results"
        self.operand_sets = []

        # Set up set indicators at the bottom (centered)
        self.set_indicators = {}
        indicator_width = 120
        indicator_height = 40
        indicator_margin = 10
        indicator_y = HEIGHT - 150  # Position above the info panel

        # Calculate total width needed for all indicators
        total_indicators = len(SET_COLORS)
        indicators_per_row = 4
        rows = (total_indicators + indicators_per_row - 1) // indicators_per_row

        # Center the indicators horizontally
        start_x = (WIDTH - (indicators_per_row * (indicator_width + indicator_margin) - indicator_margin)) // 2

        for i, (set_name, color) in enumerate(SET_COLORS.items()):
            row = i // indicators_per_row
            col = i % indicators_per_row
            y = indicator_y + row * (indicator_height + indicator_margin)
            x = start_x + col * (indicator_width + indicator_margin)

            indicator = SetIndicator(set_name, x, y, indicator_width, indicator_height, color)
            indicator.active = set_name in self.active_set_names
            self.set_indicators[set_name] = indicator

        # Operation buttons across the top
        self.operation_buttons = []
        button_width, button_height = 130, 30
        total_buttons = 8
        button_margin = 10
        buttons_width = total_buttons * button_width + (total_buttons - 1) * button_margin
        start_x = (WIDTH - buttons_width) // 2
        start_y = 10

        operations = [
            ("Generate Full Deck", self.generate_deck),
            ("Clear Cards", self.clear_cards),
            ("Union", self.show_union),
            ("Intersection", self.show_intersection),
            ("Difference", self.show_difference_dialog),
            ("Symmetric Diff", self.show_symmetric_difference),
            ("Select All Sets", self.select_all_sets),
            ("Reset View", self.reset_view)
        ]

        for i, (text, action) in enumerate(operations):
            x = start_x + i * (button_width + button_margin)
            btn = Button(x, start_y, button_width, button_height, text, action)
            self.operation_buttons.append(btn)

        self.buttons = self.operation_buttons

        # Track the currently selected card
        self.selected_card = None
        self.highlighted_cards = []

        # Create the difference selector
        self.difference_selector = DifferenceSelector(self.active_set_names)

    def toggle_set(self, set_name: str):
        """Toggle a set on or off"""
        if set_name in self.active_set_names:
            self.active_set_names.remove(set_name)
        else:
            self.active_set_names.append(set_name)

        # Update indicator active states
        self.set_indicators[set_name].active = set_name in self.active_set_names

        # Update the difference selector
        self.difference_selector = DifferenceSelector(self.active_set_names)

        self.reset_view()

    def select_all_sets(self):
        """Select all available sets"""
        self.active_set_names = list(SET_COLORS.keys())

        # Update all indicators
        for indicator in self.set_indicators.values():
            indicator.active = True

        # Update the difference selector
        self.difference_selector = DifferenceSelector(self.active_set_names)

        self.reset_view()

    def add_card(self, suit=None, value=None, x=None, y=None):
        """Add a new card to the visualization"""
        if suit is None:
            suit = random.choice(list(SUIT_SYMBOLS.keys()))

        if value is None:
            value = random.choice(CARD_VALUES)

        if x is None or y is None:
            # Random position in the visible area
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 200)  # Keep above the set indicators

        card = Card(suit, value, x, y)
        self.cards.append(card)
        return card

    def generate_deck(self):
        """Generate a full deck of cards"""
        self.clear_cards()

        # Calculate layout parameters - more spread out for bigger pane
        cards_per_suit = len(CARD_VALUES)
        margin_x, margin_y = 80, 120
        spacing_x = (WIDTH - 2 * margin_x) / 13
        spacing_y = (HEIGHT - 2 * margin_y - 150) / 4  # Leave space for indicators

        # Generate cards for each suit
        for i, suit in enumerate(SUIT_SYMBOLS.keys()):
            y = margin_y + i * spacing_y
            for j, value in enumerate(CARD_VALUES):
                x = margin_x + j * spacing_x
                self.add_card(suit, value, x, y)

    def clear_cards(self):
        """Remove all cards"""
        self.cards = []
        self.selected_card = None
        self.highlighted_cards = []
        self.reset_view()

    def show_union(self):
        """Highlight cards in the union of all active sets"""
        if len(self.active_set_names) < 2:
            self.operation_result = "Please select at least 2 sets for union"
            return

        self.operand_sets = self.active_set_names
        set_names_str = " ∪ ".join(self.operand_sets)
        self.current_operation = f"Union: {set_names_str}"

        self.highlighted_cards = []
        for card in self.cards:
            if any(set_name in card.sets for set_name in self.operand_sets):
                self.highlighted_cards.append(card)

        count = len(self.highlighted_cards)
        self.operation_result = f"Found {count} cards in the union"

    def show_intersection(self):
        """Highlight cards in the intersection of all active sets"""
        if len(self.active_set_names) < 2:
            self.operation_result = "Please select at least 2 sets for intersection"
            return

        self.operand_sets = self.active_set_names
        set_names_str = " ∩ ".join(self.operand_sets)
        self.current_operation = f"Intersection: {set_names_str}"

        self.highlighted_cards = []
        for card in self.cards:
            if all(set_name in card.sets for set_name in self.operand_sets):
                self.highlighted_cards.append(card)

        count = len(self.highlighted_cards)
        self.operation_result = f"Found {count} cards in the intersection"

    def show_difference_dialog(self):
        """Show dialog to select sets for difference operation"""
        if len(self.active_set_names) < 2:
            self.operation_result = "Please select at least 2 sets for difference"
            return

        # Update the difference selector with current active sets
        self.difference_selector = DifferenceSelector(self.active_set_names)
        self.difference_selector.show()

    def perform_difference(self, set_a, set_b):
        """Perform the difference operation between two specific sets"""
        self.operand_sets = [set_a, set_b]
        set_names_str = f"{set_a} - {set_b}"
        self.current_operation = f"Difference: {set_names_str}"

        self.highlighted_cards = []
        for card in self.cards:
            if set_a in card.sets and set_b not in card.sets:
                self.highlighted_cards.append(card)

        count = len(self.highlighted_cards)
        self.operation_result = f"Found {count} cards in the difference"

    def show_symmetric_difference(self):
        """Highlight cards in exactly one of the active sets (symmetric difference)"""
        if len(self.active_set_names) < 2:
            self.operation_result = "Please select at least 2 sets for symmetric difference"
            return

        self.operand_sets = self.active_set_names
        set_names_str = " Δ ".join(self.operand_sets)
        self.current_operation = f"Symmetric Difference: {set_names_str}"

        self.highlighted_cards = []
        for card in self.cards:
            # Count how many active sets this card belongs to
            count = sum(1 for set_name in self.operand_sets if set_name in card.sets)
            if count == 1:  # Card belongs to exactly one set
                self.highlighted_cards.append(card)

        count = len(self.highlighted_cards)
        self.operation_result = f"Found {count} cards in the symmetric difference"

    def reset_view(self):
        """Reset the visualization view"""
        self.current_operation = "Card Sets"
        self.highlighted_cards = []
        self.operation_result = "Interact to see results"
        self.selected_card = None
        self.operand_sets = []

    def handle_event(self, event):
        """Handle pygame events"""
        # First, check if the difference selector is open
        if self.difference_selector.is_open:
            if self.difference_selector.handle_event(event):
                # If the event was handled by the difference selector, don't process it further
                # Check if we need to apply a difference operation
                if not self.difference_selector.is_open:  # Dialog was closed
                    set_a, set_b = self.difference_selector.selected_set_a, self.difference_selector.selected_set_b
                    if set_a and set_b:
                        self.perform_difference(set_a, set_b)
                return

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Handle mouse movement
        if event.type == pygame.MOUSEMOTION:
            # Check if dragging any card
            if self.selected_card and self.selected_card.dragging:
                self.selected_card.x = mouse_x
                self.selected_card.y = mouse_y

            # Handle button hover
            for button in self.buttons:
                button.hover = button.is_point_inside(mouse_x, mouse_y)

            # Handle card hover
            for card in self.cards:
                card.hover = card.is_point_inside(mouse_x, mouse_y)

        # Handle mouse button press
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicking on a button
                for button in self.buttons:
                    if button.is_point_inside(mouse_x, mouse_y):
                        button.action()
                        return

                # Check if clicking on a card
                for card in reversed(self.cards):  # Check from top to bottom
                    if card.is_point_inside(mouse_x, mouse_y):
                        self.selected_card = card
                        card.dragging = True
                        return

                # Check if clicking on a set indicator
                for set_name, indicator in self.set_indicators.items():
                    if indicator.rect.collidepoint(mouse_x, mouse_y):
                        self.toggle_set(set_name)
                        return

        # Handle mouse button release
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                if self.selected_card:
                    self.selected_card.dragging = False

    def update(self):
        """Update the visualization state"""
        # Mark cards as highlighted
        for card in self.cards:
            card.highlighted = card in self.highlighted_cards

    def draw(self, screen):
        """Draw the visualization"""
        # Clear the screen
        screen.fill(BACKGROUND_COLOR)

        # Draw the set indicators at the bottom
        for indicator in self.set_indicators.values():
            indicator.draw(screen)

        # Draw the cards
        for card in self.cards:
            card.draw(screen)

        # Draw the UI buttons
        for button in self.buttons:
            button.draw(screen)

        # Draw information panel at the bottom
        info_panel = pygame.Rect(0, HEIGHT - 60, WIDTH, 60)
        pygame.draw.rect(screen, (40, 40, 40), info_panel)
        pygame.draw.line(screen, (60, 60, 60), (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)

        # Draw operation title
        title_text = title_font.render(self.current_operation, True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT - 55))

        # Draw operation result
        result_text = regular_font.render(self.operation_result, True, TEXT_COLOR)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT - 25))

        # Draw active sets indicator
        active_sets_text = small_font.render(f"Active Sets: {', '.join(self.active_set_names)}", True, TEXT_COLOR)
        screen.blit(active_sets_text, (10, HEIGHT - 25))

        # Draw the difference selector if open
        if self.difference_selector.is_open:
            self.difference_selector.draw(screen)


def main():
    # Create the visualization
    visualization = CardSetVisualization()

    # Generate some initial cards
    visualization.generate_deck()

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            visualization.handle_event(event)

        # Update
        visualization.update()

        # Draw
        visualization.draw(screen)

        # Refresh display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
