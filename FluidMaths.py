import math
import numpy as np
import random


def SpikyFunctionPow2(radius, dst):
    """
    Computes the Spiky function with a power of 2.

    """
    if (dst >= radius):
        return 0

    volume = 2 * math.pi * (radius ** 3) / 3
    value = max(0, radius - dst) ** 2
    return value * (volume ** -1)


def SpikyFunctionPow3(radius, dst):
    """
    Computes the Spiky function with a power of 3.
    """
    if dst >= radius:
        return 0

    volume = math.pi * (radius ** 4) / 2
    value = max(0, radius - dst) ** 3
    return value * (volume ** -1)


def SmoothFunctionPow3(radius, dst):
    """
    Computes the Smooth function with a power of 3.
    """
    if dst >= radius:
        return 0
    
    value = max(0, radius ** 2 - dst ** 2) ** 3
    volume = 16/35.0 * radius ** 7

    return value * (volume ** -1)


def SpikyFunctionPow2Derivative(radius, dst):
    """
    Computes the derivative of the Spiky function with a power of 2.
    """
    if dst >= radius:
        return 0
    
    value = radius - dst
    scale = 3 / (math.pi * radius ** 3)

    # Negative so it returns the slope value
    return -value * scale
    

def SpikyFunctionPow3Derivative(radius, dst):
    """
    Computes the derivative of the Spiky function with a power of 3.
    """
    if dst >= radius:
        return 0

    value = (radius - dst) ** 2
    scale = 6 / (math.pi * radius ** 4)
    # Negative so it returns the slope value
    return - value * scale



def PressureFromDensity(density, targetDensity, pressureMultiplier):
    """
    Computes the pressure from the density.
    """
    densityError = density - targetDensity
    pressure =  densityError * pressureMultiplier
    return pressure


def CalcualteSharedPressure(density_A, density_B, targetDensity, pressureMultiplier):
    """
    Calculates the shared pressure between two densities. Used for averaging pressures between particles.
    Newton's third law states: "For every action (force) in nature there is an equal and opposite reaction".
    Each particle gets an equal force with opposite directions
    """
    pressure_A = PressureFromDensity(density_A, targetDensity, pressureMultiplier)
    pressure_B = PressureFromDensity(density_B, targetDensity, pressureMultiplier)

    return (pressure_A + pressure_B) / 2


def GetRandomDirection():
    """ 
    Returns random vector [x,y] with x and y in range -1 & 1
    """
    direction = np.zeros(2)
    direction[0] = random.random() * 2 - 1
    direction[1] = random.random() * 2 - 1

    return direction
