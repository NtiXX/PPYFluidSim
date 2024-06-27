import pygame
import math
import numpy as np
import fluidMaths as fm
import random

# Pygame init
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)

# Colors
wall_color = (0,0,0)
water_color = (50, 50, 200)
background_color = (210, 210, 210)
brush_outline_color = (0,0,0)

#Editor settings
brush_size = 4
framerate = 60

particle_size = 5
num_of_particles = 100
particle_spacing = 15

# Grid states
EMPTY = 0
WATER = 1
WALL = 2

# Physics variable init
gravity = 0
air_resistance = 0.1
collision_damping = 0.7
particle_mass = 10
density_smoothing_radius = 100
target_density = 1
pressure_multiplier = 1

#Init particle arrays
positions = np.empty(num_of_particles, dtype = object)
velocities = np.empty(num_of_particles, dtype = object)
densities = np.empty(num_of_particles, dtype=float)

#Add frist particle
# positions[0] = np.array((SCREEN_WIDTH // 2.0, SCREEN_HEIGHT // 2.0))
# velocities[0] = np.array((0.0, 0.0))

def drawCircle(position, particle_size, color):
    """Draw one circle on screen in given position, particle size and color"""
    pygame.draw.circle(screen, color, position, particle_size)

def drawAllParticles():
    """Iterating over all particle positions and plotting them on the screen using pygame"""
    for position in positions:
        drawCircle(position, particle_size, water_color)

def resolveBoundsCollisions(position, velocity):
    """Check collision with borders of the screen
        return 2 arrays, #1 vector of position (x, y) #2 vector of velocity (x, y)"""

    position_X = position[0]
    position_Y = position[1]

    velocity_X = velocity[0]
    velocity_Y = velocity[1]

    HALF_BOUNDS = np.array(((SCREEN_WIDTH / 2) - particle_size, (SCREEN_HEIGHT / 2) - particle_size))
    
    if abs(position_X - HALF_BOUNDS[0]) > HALF_BOUNDS[0]:
        position_X = HALF_BOUNDS[0] * np.sign(position_X) + HALF_BOUNDS[0]
        velocity_X *= -1 * collision_damping
    
    if abs(position_Y - HALF_BOUNDS[1]) > HALF_BOUNDS[1]:
        position_Y = HALF_BOUNDS[1] * np.sign(position_Y) + HALF_BOUNDS[1]
        velocity_Y *= -1 * collision_damping

    return np.array((position_X, position_Y)), np.array((velocity_X, velocity_Y))

def calculateDensity(point):
    density = 0

    for position in positions:
        dst = np.linalg.norm(position - point)
        influence = fm.smoothingFunction(density_smoothing_radius, dst)
        density += particle_mass * influence
    
    return density

def getRandomDirection():
    direction = np.array(2)
    direction[0] = random.randint()
    direction[1] = random.randint()

    return direction

def calculatePressureForce(particle_index):
    pressure_force = np.zeros(2, dtype = float)

    for i in range(num_of_particles):
        if i != particle_index:
            offset = positions[i] - positions[particle_index]
            dst = np.linalg.norm(offset)
            direction = getRandomDirection() if dst == 0 else offset / dst
            slope = fm.smoothingFunctionDerivative(density_smoothing_radius, dst)
            density = densities[i]
            pressure_force += -fm.convertDensityToPressure(density, target_density, pressure_multiplier) * direction * slope * particle_mass / density

    return pressure_force

def simulationStep():
    """Updating the values of positions and velocities"""
    for i in range(num_of_particles):
        # Appy gravity and calculate densities
        gravity_vector = np.array((0, gravity))
        velocities[i] += gravity_vector
        densities[i] = calculateDensity(positions[i])

        # # Calculate and apply the pressure forces
        # pressure_force = calculatePressureForce(i)
        # pressure_acceleration = pressure_force / densities[i]
        # velocities[i] += pressure_acceleration

        # Update positions and resolve collisions
        positions[i] += velocities[i]
        col = resolveBoundsCollisions(positions[i], velocities[i])
        positions[i] = col[0]
        velocities[i] = col[1]

def spawnParticlesInGrid():
    particles_per_row = int(math.sqrt(num_of_particles))  
    particles_per_col = (num_of_particles - 1) / particles_per_row + 1
    spacing = particle_size * 2 + particle_spacing

    for i in range(num_of_particles):
        x = SCREEN_WIDTH / 2 + (i % particles_per_row - particles_per_row / 2.0) * spacing
        y = SCREEN_HEIGHT / 2 + (int(i / particles_per_row) - particles_per_col / 2) * spacing

        positions[i] = np.array((x, y))
        velocities[i] = np.array((0, 0))
    
def render():
    screen.fill(background_color)
    simulationStep()
    drawAllParticles()
    pygame.display.flip()
    clock.tick(framerate)

    mouse_pos = pygame.mouse.get_pos()
    density_on_mouse = calculateDensity(mouse_pos)
    pygame.draw.circle(screen, (0, 0, 0), mouse_pos, density_smoothing_radius, 1)
    print(density_on_mouse)

def main_loop():

    spawnParticlesInGrid()
    render()

    paused = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused:
                        # Unpause
                        paused = False
                    else:
                        # Pause
                        paused = True

        if not paused:
            render() 

    pygame.quit()

main_loop()




    
