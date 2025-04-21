import pygame
import sys
import random
import math
from collections import Counter
from fractions import Fraction

pygame.init()

WIDTH, HEIGHT = 800, 600
BG_COLOR = (240, 240, 240)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (120, 170, 220)
TEXT_COLOR = (20, 20, 20)
DIE_COLOR = (250, 250, 250)
DIE_BORDER = (80, 80, 80)
DIE_NUMBER_COLOR = (20, 20, 20)
STATS_BG_COLOR = (230, 230, 250)
font = pygame.font.Font(None, 24)
big_font = pygame.font.SysFont(None, 36)
small_font = pygame.font.Font(None, 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dice Roll Simulator")


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hover = False

    def draw(self):
        color = BUTTON_HOVER_COLOR if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, 0, 8)
        pygame.draw.rect(screen, DIE_BORDER, self.rect, 2, 8)

        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            if self.action:
                self.action()
            return True
        return False


class Die:
    def __init__(self, x, y, size, sides):
        self.rect = pygame.Rect(x, y, size, size)
        self.sides = sides
        self.value = random.randint(1, sides)
        self.size = size
        self.rolling = False
        self.roll_frames = 0
        self.max_frames = 30
        self.original_center = (x + size // 2, y + size // 2)
        self.center = self.original_center
        self.radius = size // 2 - 5
        self.shake_amplitude = 5  # Maximum displacement when shaking

    def roll(self):
        self.rolling = True
        self.roll_frames = 0

    def update(self):
        if self.rolling:
            if self.roll_frames < self.max_frames:
                # Update value randomly during roll
                self.value = random.randint(1, self.sides)

                # Create shaking animation
                shake_x = random.randint(-self.shake_amplitude, self.shake_amplitude)
                shake_y = random.randint(-self.shake_amplitude, self.shake_amplitude)
                self.center = (self.original_center[0] + shake_x, self.original_center[1] + shake_y)

                self.roll_frames += 1
            else:
                # Reset to original position when done rolling
                self.rolling = False
                self.center = self.original_center

    def draw(self):
        self._draw_at_position(self.center, self.size)

    def draw_at_position(self, x, y, size):
        center = (x + size // 2, y + size // 2)
        self._draw_at_position(center, size)

    def _draw_at_position(self, center, size):
        radius = size // 2 - 5
        # Special case for 2-sided (we'll draw an oval/pill shape)
        if self.sides == 2:
            # Draw an oval for 2-sided die
            rect = pygame.Rect(
                center[0] - size // 2,
                center[1] - size // 2,
                size,
                size
            )
            pygame.draw.ellipse(screen, DIE_COLOR, rect, 0)
            pygame.draw.ellipse(screen, DIE_BORDER, rect, 2)
        else:
            # For 3+ sides, draw a regular polygon
            points = []
            for i in range(self.sides):
                # Start at the top (270 degrees) and go around
                angle = math.radians(270 + (360 / self.sides) * i)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))

            # Draw the filled polygon and its border
            pygame.draw.polygon(screen, DIE_COLOR, points)
            pygame.draw.polygon(screen, DIE_BORDER, points, 2)

        # Draw the die value (number) in the center
        text = font.render(str(self.value), True, DIE_NUMBER_COLOR)
        text_rect = text.get_rect(center=center)
        screen.blit(text, text_rect)


class ProbabilityCalculator:
    @staticmethod
    def format_fraction(numerator, denominator):
        if numerator == 0:
            return "0"

        fraction = Fraction(numerator, denominator).limit_denominator()

        if fraction.denominator == 1:
            return str(fraction.numerator)
        else:
            return f"{fraction.numerator}/{fraction.denominator}"

    @staticmethod
    def exact_roll_probability(dice_values, sides):
        # Probability of getting exact values (order matters)
        total_outcomes = sides ** len(dice_values)
        # Each value has 1/sides probability, and they're independent events
        return 1, total_outcomes  # 1 in total_outcomes

    @staticmethod
    def combination_probability(dice_values, sides):
        # Probability of getting same values (order doesn't matter)
        total_outcomes = sides ** len(dice_values)

        # Count frequencies of each value
        value_counts = Counter(dice_values)

        # Calculate number of ways to arrange the dice (multinomial coefficient)
        ways = math.factorial(len(dice_values))
        for count in value_counts.values():
            ways //= math.factorial(count)

        return ways, total_outcomes

    @staticmethod
    def sum_probability(dice_sum, num_dice, sides):
        # For typical dice combinations, we'll calculate the probability
        # of getting the exact sum

        # This is a more complex calculation, especially for larger numbers of dice
        # We'll use a recursive approach for arbitrary dice and sides

        # Create a dictionary to store ways to make each sum
        ways = {}

        # Initialize base case (1 die)
        for i in range(1, sides + 1):
            ways[(1, i)] = 1

        # Build up for multiple dice
        for die in range(2, num_dice + 1):
            for s in range(die, die * sides + 1):
                ways[(die, s)] = 0
                # For each possible value of the current die
                for face in range(1, sides + 1):
                    if s - face >= die - 1:  # Check if remaining sum is possible
                        ways[(die, s)] += ways.get((die - 1, s - face), 0)

        # Get number of ways to make the sum
        favorable_outcomes = ways.get((num_dice, dice_sum), 0)
        total_outcomes = sides ** num_dice

        return favorable_outcomes, total_outcomes

    @staticmethod
    def most_probable_sum(num_dice, sides):
        if num_dice == 0:
            return 0, (0, 1)

        # For fair dice with equal probability for each face,
        # the most probable sum is in the middle of the range
        # For odd number of sides, it's exactly in the middle
        # For even number of sides, there are two equally probable sums

        # Calculate expected value
        expected_value = num_dice * (sides + 1) / 2

        # Find closest integer(s)
        lower = math.floor(expected_value)
        upper = math.ceil(expected_value)

        # Calculate probabilities
        lower_prob = ProbabilityCalculator.sum_probability(lower, num_dice, sides)
        upper_prob = ProbabilityCalculator.sum_probability(upper, num_dice, sides)

        lower_prob_frac = lower_prob[0] / lower_prob[1]
        upper_prob_frac = upper_prob[0] / upper_prob[1]

        if lower == upper:
            return lower, lower_prob
        elif lower_prob_frac > upper_prob_frac:
            return lower, lower_prob
        elif upper_prob_frac > lower_prob_frac:
            return upper, upper_prob
        else:
            # Both have equal probability
            return (lower, upper), lower_prob


num_dice = 2
dice_sides = 6
rolling = False
dice = []
prob_calculator = ProbabilityCalculator()
stats_to_display = {}
showing_stats = False
stats_delay = 60  # Frames to wait before showing stats (1 second at 60 FPS)
stats_timer = 0
clock = pygame.time.Clock()


def increase_dice():
    global num_dice
    if num_dice < 6:
        num_dice += 1
    update_dice()


def decrease_dice():
    global num_dice
    if num_dice > 1:
        num_dice -= 1
    update_dice()


def increase_sides():
    global dice_sides
    if dice_sides < 9:
        dice_sides += 1
    update_dice()


def decrease_sides():
    global dice_sides
    if dice_sides > 2:
        dice_sides -= 1
    update_dice()


def update_dice():
    global dice
    dice = []

    die_size = min(100, (WIDTH - 100) // max(num_dice, 1))
    start_x = (WIDTH - (die_size * num_dice + 20 * (num_dice - 1))) // 2

    for i in range(num_dice):
        x = start_x + i * (die_size + 20)
        y = HEIGHT // 2 - die_size // 2
        dice.append(Die(x, y, die_size, dice_sides))


def start_roll():
    global rolling, stats_to_display, showing_stats, stats_timer
    if not any(die.rolling for die in dice) and not showing_stats:
        rolling = True
        stats_to_display = {}  # Clear previous stats
        stats_timer = 0
        for die in dice:
            die.roll()


def close_stats():
    global showing_stats
    showing_stats = False


def calculate_stats():
    global stats_to_display, stats_timer

    # Get current values
    dice_values = [die.value for die in dice]
    dice_sum = sum(dice_values)

    # Calculate various probabilities
    exact_prob = prob_calculator.exact_roll_probability(dice_values, dice_sides)
    comb_prob = prob_calculator.combination_probability(dice_values, dice_sides)
    sum_prob = prob_calculator.sum_probability(dice_sum, num_dice, dice_sides)
    most_prob_sum, most_prob_prob = prob_calculator.most_probable_sum(num_dice, dice_sides)

    # Store in display dictionary
    stats_to_display = {
        "values": dice_values,
        "sum": dice_sum,
        "exact_prob": exact_prob,
        "comb_prob": comb_prob,
        "sum_prob": sum_prob,
        "most_prob_sum": most_prob_sum,
        "most_prob_prob": most_prob_prob
    }

    # Start countdown to show stats
    stats_timer = 1


def draw_stats_screen():
    # Fill the entire screen with stats background
    pygame.draw.rect(screen, STATS_BG_COLOR, pygame.Rect(0, 0, WIDTH, HEIGHT))

    # Draw title
    title = big_font.render("Roll Statistics", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    # Draw dice configuration
    config_text = f"{num_dice} Dice with {dice_sides} Sides Each"
    config = font.render(config_text, True, TEXT_COLOR)
    screen.blit(config, (WIDTH // 2 - config.get_width() // 2, 70))

    # Draw values
    y_pos = 110
    line_height = 35

    # Dice values
    # values_text = f"Dice Values: {', '.join(map(str, stats_to_display['values']))}"
    # text = font.render(values_text, True, TEXT_COLOR)
    # screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
    # y_pos += line_height

    # Show exact roll probability
    exact_num, exact_denom = stats_to_display["exact_prob"]
    text = font.render(
        f"Probability of exact roll (order matters): {prob_calculator.format_fraction(exact_num, exact_denom)}",
        True, TEXT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
    y_pos += line_height

    # Show combination probability
    comb_num, comb_denom = stats_to_display["comb_prob"]
    text = font.render(
        f"Probability of same values (any order): {prob_calculator.format_fraction(comb_num, comb_denom)}",
        True, TEXT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
    y_pos += line_height

    # Show sum probability
    sum_num, sum_denom = stats_to_display["sum_prob"]
    text = font.render(
        f"Probability of sum ({stats_to_display['sum']}): {prob_calculator.format_fraction(sum_num, sum_denom)}",
        True, TEXT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
    y_pos += line_height

    # Show most probable sum
    most_prob = stats_to_display["most_prob_sum"]
    most_prob_num, most_prob_denom = stats_to_display["most_prob_prob"]

    if isinstance(most_prob, tuple):
        most_prob_text = f"{most_prob[0]} and {most_prob[1]}"
    else:
        most_prob_text = str(most_prob)

    text = font.render(
        f"Most probable sum: {most_prob_text} ({prob_calculator.format_fraction(most_prob_num, most_prob_denom)})",
        True, TEXT_COLOR)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
    y_pos += line_height * 1.5  # Add extra space before dice visualization

    # Draw dice visualization
    die_size = min(60, (WIDTH - 100) // max(num_dice, 1))
    start_x = (WIDTH - (die_size * num_dice + 20 * (num_dice - 1))) // 2

    # Draw a label for the visualization
    visual_label = font.render("Dice Roll Result:", True, TEXT_COLOR)
    screen.blit(visual_label, (WIDTH // 2 - visual_label.get_width() // 2, y_pos))
    y_pos += 30

    # Draw each die
    for i, die in enumerate(dice):
        x = start_x + i * (die_size + 20)
        die.draw_at_position(x, y_pos, die_size)

    # Draw close button
    close_button.draw()


start_button = Button(WIDTH // 2 - 60, HEIGHT - 100, 120, 50, "Roll Dice", start_roll)
dice_up_button = Button(WIDTH // 4 - 20, HEIGHT - 150, 40, 40, "+", increase_dice)
dice_down_button = Button(WIDTH // 4 - 20, HEIGHT - 100, 40, 40, "-", decrease_dice)
sides_up_button = Button(3 * WIDTH // 4 - 20, HEIGHT - 150, 40, 40, "+", increase_sides)
sides_down_button = Button(3 * WIDTH // 4 - 20, HEIGHT - 100, 40, 40, "-", decrease_sides)
close_button = Button(WIDTH // 2 - 60, HEIGHT - 100, 120, 50, "Close Stats", close_stats)
buttons = [start_button, dice_up_button, dice_down_button, sides_up_button, sides_down_button]

update_dice()

running = True
while running:
    clock.tick(60)  # Limit to 60 FPS for smooth animation

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if showing_stats:
                close_button.handle_event(event)
            else:
                for button in buttons:
                    if button.handle_event(event):
                        break
        if event.type == pygame.MOUSEMOTION:
            if showing_stats:
                close_button.check_hover(event.pos)
            else:
                for button in buttons:
                    button.check_hover(event.pos)

    # Update dice and check if roll just finished
    any_rolling = False
    for die in dice:
        was_rolling = die.rolling
        die.update()
        any_rolling = any_rolling or die.rolling
        # If this die just finished rolling and it's the last one
        if was_rolling and not die.rolling and not any_rolling:
            calculate_stats()

    # Handle stats timer
    if stats_timer > 0:
        stats_timer += 1
        if stats_timer > stats_delay:  # Show stats after delay
            showing_stats = True
            stats_timer = 0

    # Draw everything
    if showing_stats:
        draw_stats_screen()
    else:
        screen.fill(BG_COLOR)
        title = big_font.render("Probability Simulator", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        for die in dice:
            die.draw()
        for button in buttons:
            button.draw()

        dice_label = font.render(f"Number of Dice: {num_dice}", True, TEXT_COLOR)
        screen.blit(dice_label, (WIDTH // 4 - dice_label.get_width() // 2, HEIGHT - 200))
        sides_label = font.render(f"Sides per Die: {dice_sides}", True, TEXT_COLOR)
        screen.blit(sides_label, (3 * WIDTH // 4 - sides_label.get_width() // 2, HEIGHT - 200))

    pygame.display.flip()

pygame.quit()
sys.exit()

# Make the app look more interesting
# Make the pop-out menu happen from a button on a page, rather than clicking the simulation title
# Add relevant code for each simulation to the PyQT page
#
# Create project documentation
# Create final project presentation
# Final project meeting, where we take notes and submit the notes and agenda (ask how he wants code)
# Submit code, report, video, and final grade survey to Dobbins
# End of Semester peer evaluation
#
