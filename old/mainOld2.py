import pygame
import numpy as np

# Initialize Pygame
pygame.init()
width, height = 800, 600
cell_size = 10
cols, rows = width // cell_size, height // cell_size
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Grid States
EMPTY = 0
WATER = 1
SOLID = 2

gravity = 0.1

# Create Grid
grid = np.zeros((rows, cols), dtype=int)
velocity = np.zeros((rows, cols), dtype=float)


def update_grid(grid, velocity):
    new_grid = grid.copy()
    new_velocity = velocity.copy()
    gravity = 0.1

    for y in range(rows - 2, -1, -1):
        for x in range(cols):
            if grid[y, x] == WATER:
                # Apply gravity
                new_velocity[y, x] += gravity

                # Determine new position
                new_y = int(y + new_velocity[y, x])

                # Ensure the new position is within bounds
                if new_y >= rows:
                    new_y = rows - 1

                # Move water down if the cell below is empty
                if grid[new_y, x] == EMPTY:
                    new_grid[y, x] = EMPTY
                    new_grid[new_y, x] = WATER
                    new_velocity[new_y, x] = new_velocity[y, x]
                    new_velocity[y, x] = 0
                else:
                    # Reset velocity if blocked by a solid or water
                    new_velocity[y, x] = 0

    return new_grid, new_velocity



def handle_input(grid):
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0]:  # Left mouse button
        x, y = pygame.mouse.get_pos()
        grid[y // cell_size, x // cell_size] = SOLID
    elif mouse_pressed[2]:  # Right mouse button
        x, y = pygame.mouse.get_pos()
        grid[y // cell_size, x // cell_size] = WATER

def draw_grid(screen, grid):
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if grid[y, x] == EMPTY:
                pygame.draw.rect(screen, WHITE, rect)
            elif grid[y, x] == WATER:
                pygame.draw.rect(screen, BLUE, rect)
            elif grid[y, x] == SOLID:
                pygame.draw.rect(screen, BLACK, rect)

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_input(grid)
    grid, velocity = update_grid(grid, velocity)
    screen.fill(WHITE)
    draw_grid(screen, grid)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
