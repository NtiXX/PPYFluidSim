import pygame
import numpy as np

# Pygame init
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 720
cell_size = 10
cols, rows = SCREEN_WIDTH // cell_size, SCREEN_HEIGHT // cell_size
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
framerate = 60
pygame.mouse.set_visible(False)

# Colors
wall_color = (0,0,0)
water_color = (50, 50, 200)
background_color = (210, 210, 210)
brush_outline_color = (0,0,0)

#Editor settings
brush_size = 4

# Grid states
EMPTY = 0
WATER = 1
WALL = 2

# Physics variable init
gravity = 1
air_resistance = 0.1
energy_loss = -0.9
water_energy_loss = -0.3

# Grid init
grid = np.zeros((rows, cols), dtype=int)

# Velocity array init
vx = np.zeros((rows, cols), dtype=float)
vy = np.zeros((rows, cols), dtype=float)

# Acceleration array init
ax = np.zeros((rows, cols), dtype=float)
ay = np.zeros((rows, cols), dtype=float)

# Calculating path from old particle position to new particle position
# def interpolatePoints(old_x, old_y, new_x, new_y):
#     points = []

#     # Distance between points
#     dx = abs(new_x - old_x)
#     dy = abs(new_y - old_y)
    
#     # Direction of vector
#     sx = 1 if old_x < new_x else -1
#     sy = 1 if old_y < new_y else -1

#     # Error between line and grid cells
#     error = dx - dy

#     while True:
#         points.append((old_x, old_y))

#         if old_x == new_x and old_y == new_y:
#             break

#         e2 = error * 2

#         if e2 > -dy:
#             error -= dy
#             old_x += sx
#         if e2 < dx:
#             error += dx
#             old_y += sy
    
#     return points[1:len(points) - 2]

# Simulation logic

# def checkNeighbours(grid, point):
#     x = point[0]
#     y = point[1]
#     neighbours = [grid[y - 1, x -1], grid[y - 1, x], grid[y - 1, x + 1],
#                     grid[y, x - 1], grid[y, x], grid[y, x + 1],
#                     grid[y + 1, x - 1], grid[y + 1, x], grid[y + 1, x + 1]]
    
#     return neighbours

#def checkForRoom(grid):

def updateGrid(grid, vx, vy, ax, ay):
    new_grid = grid.copy()
    new_vx = vx.copy()
    new_vy = vy.copy()
    new_ax = ax.copy()
    new_ay = ay.copy()

    for y in range(rows - 1, -1, -1):
        for x in range(cols):
            if grid[y, x] == WATER:
                
                # Add gravity as constant acceleration
                new_ay[y, x] += gravity

                # Add air resistance
                new_ax[y, x] -= air_resistance * vx[y, x]
                new_ay[y, x] -= air_resistance * vy[y, x]
                
                # Update velocities with acceleration
                new_vx[y, x] += new_ax[y, x]
                new_vy[y, x] += new_ay[y, x]

                # Calculate new position
                new_x = x + int(new_vx[y, x])
                new_y = y + int(new_vy[y, x])

                # Boundary check
                if new_y >= rows - 2:
                    new_y = rows - 2
                    new_vy[y, x] *= energy_loss
                if new_y < 1:
                    new_y = 1
                    new_vy[y, x] *= energy_loss
                if new_x >= cols - 2:
                    new_x = cols - 2
                    new_vx[y, x] *= energy_loss
                if new_x < 1:
                    new_x = 1
                    new_vx[y, x] *= energy_loss

                # new_x and new_y are set
                
                #checkForRoom(grid, new_x, new_y)



                
                # path = EMPTY
                # collision_point = (new_y, new_x)
                # points = interpolatePoints(x, y, new_x, new_y)
                # for i, (px, py) in enumerate(points):
                #     if new_grid[py, px] != EMPTY:
                #         path = grid[py,px]
                #         collision_point = points[i - 1] #(x, y)
                #         print(checkNeighbours(new_grid, collision_point))
                
                if grid[new_y, new_x] == EMPTY:
                    new_grid[new_y, new_x] = WATER
                    new_vx[new_y, new_x] = new_vx[y, x]
                    new_vy[new_y, new_x] = new_vy[y, x]
                    new_ax[new_y, new_x] = new_ax[y, x]
                    new_ay[new_y, new_x] = new_ay[y, x]
                    new_grid[y, x] = EMPTY
                    new_vx[y, x] = 0
                    new_vy[y, x] = 0
                    new_ax[y, x] = 0
                    new_ay[y, x] = 0
                else:
                    # Simple bounce effect
                    new_vx[y, x] *= -0.5
                    new_vy[y, x] *= -0.5


    return new_grid, new_vx, new_vy, new_ax, new_ay

def resetGrid():
    # Grid init
    grid = np.zeros((rows, cols), dtype=int)

    # Velocity array init
    vx = np.zeros((rows, cols), dtype=float)
    vy = np.zeros((rows, cols), dtype=float)

    # Acceleration array init
    ax = np.zeros((rows, cols), dtype=float)
    ay = np.zeros((rows, cols), dtype=float)
    
    return grid, vx, vy, ax, ay

def snapToGrid(pos):
    x, y = pos
    snapped_x = (x // cell_size) * cell_size
    snapped_y = (y // cell_size) * cell_size
    return snapped_x, snapped_y


def cellsInBrush(x, y):
    snapped_x,snapped_y = snapToGrid((x, y))
    scaled_x, scaped_y = snapped_x // cell_size, snapped_y // cell_size
    cells = []
    
    for i in range(brush_size):
        for j in range(brush_size):
            cells.append((scaled_x + i, scaped_y + j))
    return cells

def drawMaterial(x, y, material):
    cells_to_fill = cellsInBrush(x,y)
    for cell in cells_to_fill[::-1]:
        x = cell[0]
        y = cell[1]
        if x < SCREEN_WIDTH // cell_size and x > 0 - brush_size and y < SCREEN_HEIGHT // cell_size and y > 0 - brush_size and grid[y, x] == EMPTY:
            grid[y, x] = material

def handleInput(grid):
    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0]:  # Left mouse button
        x, y = pygame.mouse.get_pos()
        drawMaterial(x, y, WALL)
    elif mouse_pressed[2]:  # Right mouse button
        x, y = pygame.mouse.get_pos()
        drawMaterial(x, y, WATER)
           

def drawGrid(screen, grid):
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if grid[y, x] == EMPTY:
                pygame.draw.rect(screen, background_color, rect)
            elif grid[y, x] == WATER:
                pygame.draw.rect(screen, water_color, rect)
            elif grid[y, x] == WALL:
                pygame.draw.rect(screen, wall_color, rect)
                
def brushRendering(screen):
    x, y = pygame.mouse.get_pos()
    snapped_x, snapped_y = snapToGrid((x, y))
    brush_outline_rect = pygame.Rect(snapped_x, snapped_y, cell_size * brush_size, cell_size * brush_size)
    pygame.draw.rect(screen, brush_outline_color, brush_outline_rect, 1)



def brushSizeUpdate(direction):
    brush_size -= direction

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
       
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                grid, vx, vy, ax, ay = resetGrid()
        
        elif event.type == pygame.MOUSEWHEEL:
            direction = event.y
            brush_size += direction


    handleInput(grid)
    grid, vx, vy, ax, ay = updateGrid(grid, vx, vy, ax, ay)

    screen.fill(background_color)
    drawGrid(screen, grid)
    brushRendering(screen)
    pygame.display.flip()
    clock.tick(framerate)

pygame.quit()
