import pygame
import math
import numpy as np

import fluidMaths as fm
import simSetup


# Pygame init
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)
framerate = 60

# Colors
wall_color = (0,0,0)
water_color = (50, 50, 200)
background_color = (210, 210, 210)
brush_outline_color = (0,0,0)

#Editor settings
brush_size = 4
particle_size = 10
num_of_particles = 50
particle_spacing = 10

# Physics variable init
gravity =  0
collision_damping = 0.7
particle_mass = 1
density_smoothing_radius = 200
target_density = 0.1
pressure_multiplier = 0.1

#Init particle arrays
positions = np.empty(num_of_particles, dtype = object)
velocities = np.array([np.zeros(2, dtype=float) for x in range(num_of_particles)])
densities = np.empty(num_of_particles, dtype=float)

def drawParticle(position_index, particle_size, color):
    """Draw one circle on screen in given position, particle size and color"""
    # density_scaled = densities[position_index] * 100000
    # color = (min(density_scaled, 255) , 50, 50)

    speeds = [np.linalg.norm(velocities[i]) for i in range(num_of_particles)]
    max_speed = max(speeds)

    speed_color_scale = 255 / max_speed

    color = (min(255, speeds[position_index] * speed_color_scale), 50, 200)
    pygame.draw.circle(screen, color , positions[position_index], particle_size)

def drawAllParticles():
    for index in range(num_of_particles):
        drawParticle(index, particle_size, water_color)

def resolveBoundsCollisions(particle_index):
    """ Detecting bound collision by checking if new position is in bounds, if not place it on the bound and reverce it's velocity"""
    new_position = positions[particle_index] + velocities[particle_index]
    velocity = velocities[particle_index]

    # HALF_BOUND_X = SCREEN_WIDTH // 2 - particle_size
    # HALF_BOUND_Y = SCREEN_HEIGHT // 2 - particle_size

    # # Check for collision horizontally
    # if abs(new_position[0] - HALF_BOUND_X) >=  HALF_BOUND_X:
    #     new_position[0] = HALF_BOUND_X * np.sign(new_position[0]) + HALF_BOUND_X
    #     velocity[0] *= -1 * collision_damping

    # # Check for collision vertically
    # if abs(new_position[1] - HALF_BOUND_Y) >=  HALF_BOUND_Y:
    #     new_position[1] = HALF_BOUND_Y * np.sign(new_position[1]) + HALF_BOUND_Y
    #     velocity[1] *= -1 * collision_damping

    if new_position[0] >= SCREEN_WIDTH - particle_size or new_position[0] <= particle_size:
        new_position[0] = positions[particle_index][0]
        velocities[0] *= -1 * collision_damping
    
    if new_position[1] >= SCREEN_HEIGHT - particle_size or new_position[1] <= particle_size:
        new_position[1] = positions[particle_index][1]
        velocities[1] *= -1 * collision_damping

    return new_position, velocity

def calculatePressureForce(particle_index):
    pressure_force = np.zeros(2, dtype = float)

    for i in range(num_of_particles):
        if i != particle_index:
            offset = positions[i] - positions[particle_index]
            dst = np.linalg.norm(offset)
            direction = fm.getRandomDirection() if dst == 0 else offset / dst

            slope = fm.smoothingFunctionDerivative(density_smoothing_radius, dst)
            density = densities[i]


            pressure_force += 0 if density == 0 else -fm.convertDensityToPressure(density, target_density, pressure_multiplier) * direction * slope * particle_mass / density
    
    return pressure_force

def simulationStep():
    """Updating the values of positions and velocities"""
    for i in range(num_of_particles):
        drawParticle(i, particle_size, water_color)
        # Appy gravity and calculate densities
        gravity_vector = np.array((0, gravity))
        velocities[i] += gravity_vector
        densities[i] = fm.calculateDensity(positions[i], positions, particle_mass, density_smoothing_radius, particle_size)
        print(densities[i])

        # Calculate and apply the pressure forces
        pressure_force = calculatePressureForce(i)
        pressure_acceleration = pressure_force / densities[i]
        velocities[i] += pressure_acceleration

        # Update positions and resolve collisions1
        positions[i] += velocities[i]
        col = resolveBoundsCollisions(i)
        positions[i] = col[0]
        velocities[i] = col[1]

        

def start():
    """ Setting up the simulation """
    global positions
    positions = simSetup.spawnParticlesRandomly (num_of_particles, particle_size, particle_spacing, SCREEN_WIDTH, SCREEN_HEIGHT)

def render():
    screen.fill(background_color)
    simulationStep()
   
    # mouse_pos = pygame.mouse.get_pos()
    # density_on_mouse = fm.calculateDensity(mouse_pos, positions, particle_mass, density_smoothing_radius)
    # pygame.draw.circle(screen, (0,0,0), mouse_pos, density_smoothing_radius, 1)
    # print(density_on_mouse)

    pygame.display.flip()
    clock.tick(framerate)

def main_loop():
    start()
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