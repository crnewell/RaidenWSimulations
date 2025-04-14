import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
BG_COLOR = (240, 240, 240)
BUTTON_COLOR = (100, 150, 200)
BUTTON_HOVER_COLOR = (120, 170, 220)
TEXT_COLOR = (20, 20, 20)
DIE_COLOR = (250, 250, 250)
DIE_BORDER = (80, 80, 80)
DIE_NUMBER_COLOR = (20, 20, 20)
font = pygame.font.Font(None, 24)
big_font = pygame.font.SysFont(None, 36)

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
        self.max_frames = 20

    def roll(self):
        self.rolling = True
        self.roll_frames = 0

    def update(self):
        if self.rolling:
            if self.roll_frames < self.max_frames:
                self.value = random.randint(1, self.sides)
                self.roll_frames += 1
            else:
                self.rolling = False

    def draw(self):
        pygame.draw.rect(screen, DIE_COLOR, self.rect, 0, 10)
        pygame.draw.rect(screen, DIE_BORDER, self.rect, 2, 10)

        text = font.render(str(self.value), True, DIE_NUMBER_COLOR)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


num_dice = 2
dice_sides = 6
rolling = False
dice = []


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
    if dice_sides > 3:
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
    global rolling
    if not any(die.rolling for die in dice):
        rolling = True
        for die in dice:
            die.roll()


start_button = Button(WIDTH // 2 - 60, HEIGHT - 100, 120, 50, "Roll Dice", start_roll)
dice_up_button = Button(WIDTH // 4 - 20, HEIGHT - 150, 40, 40, "+", increase_dice)
dice_down_button = Button(WIDTH // 4 - 20, HEIGHT - 100, 40, 40, "-", decrease_dice)
sides_up_button = Button(3 * WIDTH // 4 - 20, HEIGHT - 150, 40, 40, "+", increase_sides)
sides_down_button = Button(3 * WIDTH // 4 - 20, HEIGHT - 100, 40, 40, "-", decrease_sides)
buttons = [start_button, dice_up_button, dice_down_button, sides_up_button, sides_down_button]

update_dice()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.handle_event(event):
                    break
        if event.type == pygame.MOUSEMOTION:
            for button in buttons:
                button.check_hover(event.pos)

    for die in dice:
        die.update()

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