import pygame
import sys
import random

CELL_SIZE = 15
BOTTOM_UI_HEIGHT = 120
FPS = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
GREEN = (0, 255, 0)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)

PRESETS = {
    'Glider': [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
    'Small Exploder': [(1,0), (0,1),(1,1),(2,1), (0,2),(2,2), (1,3)],
    'Exploder': [(0,0),(2,0),(4,0), (0,1),(4,1), (0,2),(4,2), (0,3),(4,3), (0,4),(2,4),(4,4)],
    '10 Cell Row': [(x, 0) for x in range(10)],
    'LWSS': [(1,0),(2,0),(3,0),(4,0), (0,1),(4,1), (4,2), (0,3),(3,3)],
    'Pulsar': [
        (2,0),(3,0),(4,0),(8,0),(9,0),(10,0),
        (0,2),(5,2),(7,2),(12,2),
        (0,3),(5,3),(7,3),(12,3),
        (0,4),(5,4),(7,4),(12,4),
        (2,5),(3,5),(4,5),(8,5),(9,5),(10,5),
        (2,7),(3,7),(4,7),(8,7),(9,7),(10,7),
        (0,8),(5,8),(7,8),(12,8),
        (0,9),(5,9),(7,9),(12,9),
        (0,10),(5,10),(7,10),(12,10),
        (2,12),(3,12),(4,12),(8,12),(9,12),(10,12)
    ],
    'Pentadecathlon': [
        (4,2), (4,3), (3,4), (5,4), (4,5), (4,6), (4,7), (4,8), (3,9), (5,9), (4,10), (4,11),
    ],
    'Beacon': [(0,0), (1,0), (0,1), (1,1), (2,2), (3,2), (2,3), (3,3)],
    'Gosper Glider Gun': [
        (24,0), (22,1),(24,1), (12,2),(13,2),(20,2),(21,2),(34,2),(35,2),
        (11,3),(15,3),(20,3),(21,3),(34,3),(35,3),
        (0,4),(1,4),(10,4),(16,4),(20,4),(21,4),
        (0,5),(1,5),(10,5),(14,5),(16,5),(17,5),(22,5),(24,5),
        (10,6),(16,6),(24,6), (11,7),(15,7), (12,8),(13,8)
    ],
    'R-pentomino': [(1,0), (2,0), (0,1), (1,1), (1,2)]
}

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Conway's Game of Life - Fullscreen")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)
large_font = pygame.font.SysFont('Arial', 20)

GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = (HEIGHT - BOTTOM_UI_HEIGHT) // CELL_SIZE

def create_grid(randomize=False):
    return [[random.randint(0, 1) if randomize else 0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def count_alive_neighbors(grid, x, y):
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if dx == 0 and dy == 0:
                continue
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                count += grid[ny][nx]
            # else: treat as dead (0), so no addition
    return count

def next_generation(grid):
    return [
        [1 if (grid[y][x] and 2 <= count_alive_neighbors(grid, x, y) <= 3)
            or (not grid[y][x] and count_alive_neighbors(grid, x, y) == 3) else 0
            for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)
    ]

def place_pattern(grid, pattern, top_left_x, top_left_y):
    for dx, dy in pattern:
        x, y = top_left_x + dx, top_left_y + dy
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            grid[y][x] = 1

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
    for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_cells(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_text(text, x, y, color=WHITE, font_obj=None, align_right=False):
    font_obj = font_obj or font
    img = font_obj.render(text, True, color)
    rect = img.get_rect()
    rect.topright if align_right else rect.topleft
    rect.topright = (x, y) if align_right else (x, y)
    screen.blit(img, rect)

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, surface):
        color = LIGHT_GRAY if self.hover else DARK_GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        txt = font.render(self.text, True, WHITE)
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            self.callback()

def main():
    grid = create_grid()
    generation = 0
    running = False
    speed = FPS
    custom_mode = False

    def start_pause():
        nonlocal running
        running = not running

    def step():
        nonlocal generation, grid
        grid = next_generation(grid)
        generation += 1

    def clear():
        nonlocal grid, generation, running
        grid = create_grid()
        generation = 0
        running = False

    def randomize():
        nonlocal grid, generation, running
        grid = create_grid(randomize=True)
        generation = 0
        running = False

    def toggle_custom():
        nonlocal custom_mode, running
        custom_mode = not custom_mode
        running = False

    def load(name):
        def inner():
            nonlocal grid, generation, running
            grid = create_grid()
            place_pattern(grid, PRESETS[name], GRID_WIDTH // 2 - 5, GRID_HEIGHT // 2 - 3)
            generation = 0
            running = False
        return inner

    buttons = []
    spacing = 10
    bw, bh = 130, 30
    buttons_per_row = 5
    all_buttons = [
        ("Start / Pause", start_pause),
        ("Step", step),
        ("Clear", clear),
        ("Soup", randomize),
        ("Custom Mode", toggle_custom)
    ] + [(name, load(name)) for name in PRESETS.keys()]

    for idx, (label, cb) in enumerate(all_buttons):
        row = idx // buttons_per_row
        col = idx % buttons_per_row
        x = spacing + col * (bw + spacing)
        y = HEIGHT - BOTTOM_UI_HEIGHT + spacing + row * (bh + spacing)
        buttons.append(Button((x, y, bw, bh), label, cb))

    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my < GRID_HEIGHT * CELL_SIZE:
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if custom_mode or not running:
                        grid[gy][gx] ^= 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_UP: speed = min(60, speed + 1)
                elif event.key == pygame.K_DOWN: speed = max(1, speed - 1)
            for btn in buttons:
                btn.handle_event(event)

        if running:
            grid = next_generation(grid)
            generation += 1

        draw_cells(grid)
        draw_grid()

        for btn in buttons:
            btn.draw(screen)

        mode_text = "CUSTOM MODE ON" if custom_mode else "Simulation Mode"
        draw_text(f"Gen: {generation} | Speed: {speed} FPS | {mode_text}", WIDTH - 10, HEIGHT - 25, align_right=True, font_obj=large_font)

        pygame.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    main()
