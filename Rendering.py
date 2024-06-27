import pygame
import numpy as np

class Rendering:

    def __init__(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.screen = screen
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

    def DrawParticle(self, color, position, size):
        """
        Draw one circle on screen in given position, particle size and color
        """
        pygame.draw.circle(self.screen, color, position, size)

    def BrushRendering(self, color, position, size):
        """
        Draws the brush outline at given position with given color and size.
        """
        pygame.draw.circle(self.screen, color, position, size, 1)

    def DrawAllParticles(self, particles, color, size):
        """ 
        Draws and displays all particles on the screen
        """
        for index in range(len(particles)):
            self.DrawParticle(color, particles[index], size)

    def DrawAllParticlesWithVelColors(self, particles, velocities, color, size):
        """ 
        Draws and displays all particles on the screen with colors based on their velocities.
        """
        color = (10, 130, 255)
        maxSpeed = max([np.linalg.norm(vel) for vel in velocities])

        # Scale to fastest moving particle
        #colorScale = (255.0 / maxSpeed) if maxSpeed != 0 else 1

        for index in range(len(particles)):
            colorVector = np.array(color)
            speedVectorLength = np.linalg.norm(velocities[index])
            
            #speedColorVector = np.array((int(speedVectorLength * colorScale), 1, 1))
            speedColorVector = np.array((speedVectorLength * 2, 1, 1))
            outputColor = colorVector * speedColorVector

            outputColor = [int(min(255, c)) for c in outputColor]

            self.DrawParticle(outputColor, particles[index], size)