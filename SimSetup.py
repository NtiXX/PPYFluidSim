import math
import numpy as np
import random


def SpawnParticlesInGrid(particleNumber, particleSize, particleSpacing, SCREEN_WIDTH, SCREEN_HEIGHT):
    """
    Spawns particles in a grid pattern.

    Args:
        particleNumber: The number of particles to spawn.
        particleSize: The size of each particle.
        particleSpacing: The spacing between particles.
        SCREEN_WIDTH: The width of the screen.
        SCREEN_HEIGHT: The height of the screen.

    Returns: An array of particle positions.
    """

    positions = np.zeros(particleNumber, dtype=object)

    particles_per_row = int(math.sqrt(particleNumber))  
    particles_per_col = (particleNumber - 1) // particles_per_row + 1
    spacing = particleSpacing + particleSize

    for i in range(particleNumber):
        x = SCREEN_WIDTH // 2 + (i % particles_per_row - particles_per_row // 2) * spacing
        y = SCREEN_HEIGHT // 2 + (int(i / particles_per_row) - particles_per_col // 2) * spacing

        positions[i] = np.array([x, y], dtype=float)

    return positions


def SpawnParticlesRandomly(particleNumber, particleSize, SCREEN_WIDTH, SCREEN_HEIGHT):
    """
    Spawns particles randomly within the screen boundaries.

    Args:
        particleNumber: The number of particles to spawn.
        particleSize: The size of each particle.
        SCREEN_WIDTH: The width of the screen.
        SCREEN_HEIGHT: The height of the screen.

    Returns: An array of particle positions.
    """
    positions = np.zeros(particleNumber, dtype=object)

    for i in range(particleNumber):
        x = random.randint(0 + particleSize, SCREEN_WIDTH - particleSize)
        y = random.randint(0 + particleSize, SCREEN_HEIGHT - particleSize)

        positions[i] = np.array([x, y], dtype=int)

    return positions