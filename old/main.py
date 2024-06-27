import pygame
import math
import numpy as np
import time

import FluidMaths as fm
import SimSetup
from Rendering import Rendering
import SpatialHash as sh
from Gui import Gui

# Pygame init
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)
framerate = 120

screenSize = (SCREEN_WIDTH, SCREEN_HEIGHT)
guiSize = (350, SCREEN_HEIGHT)
gui = Gui(screenSize, guiSize)

SIM_AREA_WIDTH = SCREEN_WIDTH - guiSize[0]

render = Rendering(screen, SIM_AREA_WIDTH, SCREEN_HEIGHT)


# Start variables
GRID = 0
RANDOM = 1

# Colors
wallColor = (0,0,0)
waterColor = (10, 130, 255)
backgroundColorLight = (210, 210, 210)
backgroundColorDark = (10, 10, 14)
brushOutlineColor = (0,0,0)
menuBackgroundColor = backgroundColorLight

# Editor settings
brushSize = 50
particleSize = 8
numOfParticles = 200
particleSpacing = 25

# Simulation Settings
gravity = 0.0
collisionDamping = 0.5
particleMass = 1
smoothingRadius = 70
targetDensity = 7 / 1000.0
pressureMultiplier = 700.0
nearPressureMultiplier = 0
viscosityStrength = 0.5
#Debug
densityThreshhold = 0.000000000001

# Init particle arrays
positions = []
predictedPositions = []
velocities = []
densities = [] # Density, Near Density

# Init special lookup array
spatialIndecies = [] # particleIndex, cellHash, cellKey
spatialOffests = []

# Gui slider setup

gui.AddSlider(numOfParticles, "Num Of Particles", 1, 1000)
gui.AddSlider(particleSize, "Particle Size", 1, 100)
gui.AddSlider(particleSpacing, "Particle Spacing", 1, 100)
gui.AddSlider(gravity, "Gravity", -5, 5)
gui.AddSlider(collisionDamping, "Collision Damping", -1, 1)
gui.AddSlider(smoothingRadius, "Smoothing Radius", 1, 300)
gui.AddSlider(targetDensity, "Target Density", 1 / 1000.0, 1 / 1.0)
gui.AddSlider(pressureMultiplier,"Pressure Multiplier", 0, 10)
gui.AddSlider(nearPressureMultiplier,"Near Pressure Multiplier", 0, 1000)
gui.AddSlider(viscosityStrength,"Viscosity Strength", -1, 1)


def HandleCollisions(particleIndex):
    """ Detecting bound collision by checking if new position is in bounds, if not place it on the bound and reverce it's velocity"""
    new_position = positions[particleIndex] + velocities[particleIndex]
    velocity = velocities[particleIndex]

    HALF_BOUND_X = (SIM_AREA_WIDTH - particleSize) * 0.5
    HALF_BOUND_Y = (SCREEN_HEIGHT - particleSize) * 0.5

    # Check for collision horizontally
    if abs(new_position[0] - HALF_BOUND_X) >=  HALF_BOUND_X:
        new_position[0] = HALF_BOUND_X * np.sign(new_position[0]) + HALF_BOUND_X
        velocity[0] *= -1 * collisionDamping

    # Check for collision vertically
    if abs(new_position[1] - HALF_BOUND_Y) >=  HALF_BOUND_Y:
        new_position[1] = HALF_BOUND_Y * np.sign(new_position[1]) + HALF_BOUND_Y
        velocity[1] *= -1 * collisionDamping

    return [new_position, velocity]


def UpdateExternalForces(particleIndex):
    global velocities, predictedPositions
    
    gravityAcceleration = np.array((0, gravity))

    # Adding gravity 
    velocities[particleIndex] += gravityAcceleration

    # Prediction
    predictionFactor = 1
    predictedPositions[particleIndex] = positions[particleIndex] + (velocities[particleIndex] * predictionFactor)


def UpdateSpatialHash():
    global spatialIndecies, spatialOffests

    for particleIndex in range(len(positions)):
        # Reset offsets
        spatialOffests[particleIndex] = numOfParticles
        # Update spatialIndecies)
        particleCell = sh.GetCell(positions[particleIndex], smoothingRadius)
        cellHash = sh.HashCell(particleCell)
        cellKey = sh.GetKeyFromHash(cellHash, numOfParticles)

        spatialIndecies[particleIndex] = [particleIndex, cellHash, cellKey]

    # Sort by cell key
    spatialIndecies = sorted(spatialIndecies, key=lambda x : x[2])

    # Calculate Offsets
    for particleIndex in range(len(positions)):
        
        # Calculate start indices of each unique cell key in spatial look up
        key = spatialIndecies[particleIndex][2]
        keyPrev = (math.inf if particleIndex == 0 else spatialIndecies[particleIndex - 1][2])
        if key != keyPrev:
            spatialOffests[key] = int(particleIndex)


def CalculateDensity(particleIndex):
    position = predictedPositions[particleIndex]
    originCell = sh.GetCell(position, smoothingRadius)
    sqrRadius = smoothingRadius ** 2
    density = 0
    nearDensity = 0

    # Neighbour search
    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffests[neighbourKey]

        while currIndex < numOfParticles:
            indexData = spatialIndecies[currIndex]
            currIndex += 1

            # Break if no longer looking at correct bin
            if indexData[2] != neighbourKey: break
            # Skip if hash does not match
            if indexData[1] != neighbourHash: continue

            neighbourIndex = indexData[0]
            
            #if neighbourIndex == particleIndex: continue

            neighbourPosition = predictedPositions[neighbourIndex]
            offsetToNeighbour = neighbourPosition - position
            sqrDstToNeighbour = np.dot(offsetToNeighbour, offsetToNeighbour)

            # Skip if not within radius
            if sqrDstToNeighbour > sqrRadius: continue

            # Calculate densities
            distanceToNeighbour = math.sqrt(sqrDstToNeighbour)
            density += fm.SpikyFunctionPow2(smoothingRadius, distanceToNeighbour)
            #nearDensity += fm.SpikyFunctionPow3(smoothingRadius, distanceToNeighbour)

            
    return [density, nearDensity]


def UpdateDensity(particleIndex):
    global densities
    densities[particleIndex] = CalculateDensity(particleIndex)


def CalculatePressureForce(particleIndex):
    density = densities[particleIndex][0]
    nearDensity = densities[particleIndex][1]
    pressure = fm.PressureFromDensity(density, targetDensity, pressureMultiplier)
    #nearPressure = fm.NearPressureFromDensity(nearDensity, nearPressureMultiplier)

    position = predictedPositions[particleIndex]
    originCell = sh.GetCell(position, smoothingRadius)
    sqrRadius = smoothingRadius ** 2
    pressureForce = np.zeros(2, dtype=float)

    # Neighbour search
    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffests[neighbourKey]

        while currIndex < numOfParticles:
            indexData = spatialIndecies[currIndex]
            currIndex += 1
            # Break if no longer looking at correct bin
            if indexData[2] != neighbourKey: break
            # Skip if hash does not match
            if indexData[1] != neighbourHash: continue

            neighbourIndex = indexData[0]
            # Skip if looking at self
            if neighbourIndex == particleIndex: continue

            neighbourPosition = predictedPositions[neighbourIndex]
            offsetToNeighbour = neighbourPosition - position
            sqrDstToNeighbour = np.dot(offsetToNeighbour, offsetToNeighbour)

            # Skip if not within radius
            if sqrDstToNeighbour > sqrRadius: continue

            #Calculate pressure force
            distanceToNeighbour = math.sqrt(sqrDstToNeighbour)
            directionToNeighbour = offsetToNeighbour / distanceToNeighbour if distanceToNeighbour > 0 else np.array((0, 1))

            neighbourDensity = densities[neighbourIndex][0]
            neighbourNearDensity = densities[neighbourIndex][1]
            neighbourPressure = fm.PressureFromDensity(neighbourDensity, targetDensity, pressureMultiplier)
            neighbourNearPressure = fm.NearPressureFromDensity(neighbourNearDensity, nearPressureMultiplier)

            sharedPressure = (pressure + neighbourPressure) * 0.5
            #sharedNearPressure = (nearPressure + neighbourNearPressure) * 0.5

            if neighbourDensity > densityThreshhold:
                pressureForce += directionToNeighbour * fm.SpikyFunctionPow2Derivative(smoothingRadius, distanceToNeighbour) * sharedPressure / neighbourDensity
            
            # if neighbourNearDensity > densityThreshhold:
            #     pressureForce += directionToNeighbour * fm.SpikyFunctionPow3Derivative(smoothingRadius, distanceToNeighbour) * sharedNearPressure / neighbourNearDensity


    return pressureForce


def UpdatePressureForce(particleIndex):
    global velocities
    
    density = densities[particleIndex][0]

    pressureForce = CalculatePressureForce(particleIndex)

    if density > densityThreshhold:
        acceleration = pressureForce / density
        velocities[particleIndex] += acceleration


def CalculateViscosityForce(particleIndex):
    position = predictedPositions[particleIndex]
    originCell = sh.GetCell(position, smoothingRadius)
    sqrRadius = smoothingRadius ** 2

    viscosityForce = 0
    velocity = velocities[particleIndex]

    # Neighbour search
    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffests[neighbourKey]

        while currIndex < numOfParticles:
            indexData = spatialIndecies[currIndex]
            currIndex += 1

            # Break if no longer looking at correct bin
            if indexData[2] != neighbourKey: break
            # Skip if hash does not match
            if indexData[1] != neighbourHash: continue

            neighbourIndex = indexData[0]
            # Skip if looking at self
            if neighbourIndex == particleIndex: continue
            
            neighbourPosition = predictedPositions[neighbourIndex]
            offsetToNeighbour = neighbourPosition - position
            sqrDstToNeighbour = np.dot(offsetToNeighbour, offsetToNeighbour)

            # Skip if not within radius
            if sqrDstToNeighbour > sqrRadius: continue

            # Calculate viscosity
            distanceToNeighbour = math.sqrt(sqrDstToNeighbour)
            neighbourVelocity = velocities[neighbourIndex]
            viscosityForce += (neighbourVelocity - velocity) * fm.SpikyFunctionPow3(smoothingRadius, distanceToNeighbour)

    return viscosityForce


def UpdateViscosity(particleIndex):
    global velocities
    viscosityForce = CalculateViscosityForce(particleIndex)
    velocities[particleIndex] += viscosityForce * viscosityStrength


def UpdatePosition(particleIndex):
    global positions

    newPositionNVelocity = HandleCollisions(particleIndex)
    
    # print(positions[particleIndex], newPositionNVelocity[0])
    # print(velocities[particleIndex], newPositionNVelocity[1])
    positions[particleIndex] = newPositionNVelocity[0]
    velocities[particleIndex] = newPositionNVelocity[1]


def AddParticle(position):
    global numOfParticles, positions, predictedPositions, velocities, densities, spatialIndecies, spatialOffests

    positionVector = np.array((position[0], position[1]))

    numOfParticles += 1
    newIndex = numOfParticles
    
    print("Adding particle at: ", position)

    # Update positions & velocities array
    newPositions = np.zeros(numOfParticles, dtype=object)
    newPredictedPositions = np.empty(numOfParticles, dtype=object)
    newVelocities = np.array([np.zeros(2, dtype=float) for x in range(numOfParticles)])
    newDensities = np.empty(numOfParticles, dtype=object)
    newSpatialIndecies = np.empty(numOfParticles, dtype=object)
    newSpatialOffests = np.empty(numOfParticles, dtype=int)

    for i in range(len(positions)):
        newPositions = positions[i]
        newPredictedPositions = predictedPositions[i]
        newVelocities = velocities[i]
        newDensities = densities[i]
        newSpatialIndecies = spatialIndecies[i]
        newSpatialOffests = spatialOffests[i]

    newPositions[newIndex] = np.array([position[0], position[1]], dtype=int)
    newPredictedPositions[newIndex] = positionVector
    newVelocities[newIndex] = np.zeros(2, dtype=float)
    newDensities[newIndex] = []
    newSpatialIndecies[newIndex] = []
    newSpatialOffests[newIndex] = 0

    positions = newPositions
    predictedPositions = newPredictedPositions
    velocities = newVelocities
    densities = newDensities
    spatialIndecies = newSpatialIndecies
    spatialOffests = newSpatialOffests

    # velocities = np.append(velocities, [np.zeros(2, dtype=float) for x in range(numOfParticles)])

    # # Make room in neighbour search arrays
    # spatialIndecies = np.append(spatialIndecies, [])
    # spatialOffests = np.append(spatialOffests, 0)

    # densities = np.append(densities, [])

    # SimulationStep()


def SimulationStep():
    # For every particle: 
        # ExternalForces
        # UpdateSpatialHash
        # UpdateDensities
        # UpdatePressureForce
        # CalculateViscosity
        # UpdatePositions

    for particleIndex in range(len(positions)):
        UpdateExternalForces(particleIndex)

    UpdateSpatialHash()
    
    for particleIndex in range(len(positions)):
        UpdateDensity(particleIndex)

    for particleIndex in range(len(positions)):    
        UpdatePressureForce(particleIndex)
        UpdateViscosity(particleIndex)
        UpdatePosition(particleIndex)


def HandleMouseInput():
    mouse_pressed = pygame.mouse.get_pressed()

    if mouse_pressed[0]:  # Left mouse button
        x, y = pygame.mouse.get_pos()
        AddParticle((x, y))
    elif mouse_pressed[2]:  # Right mouse button
        x, y = pygame.mouse.get_pos()
        

def UpdateVariables():
    global numOfParticles, particleSize, particleSpacing, gravity, collisionDamping, smoothingRadius, targetDensity, pressureMultiplier, nearPressureMultiplier
    
    values = gui.GetSliderValues()

    if numOfParticles != values[0] or particleSpacing != values[2]:
        numOfParticles = values[0]
        particleSpacing = values[2]
        Start(GRID)
   
    particleSize = values[1]
    gravity = values[3]
    collisionDamping = values[4]
    smoothingRadius = values[5]
    targetDensity = values[6] / 1000
    pressureMultiplier = values[7]
    nearPressureMultiplier = values[8]


def InitializeArrays(option):
    global positions, predictedPositions, velocities, densities, spatialIndecies, spatialOffests

    predictedPositions = np.empty(numOfParticles, dtype=object)
    velocities = np.array([np.zeros(2, dtype=float) for x in range(numOfParticles)])
    densities = np.empty(numOfParticles, dtype=object)
  
    spatialIndecies = np.empty(numOfParticles, dtype=object)
    spatialOffests = np.empty(numOfParticles, dtype=int)

    if option == GRID:
        positions = SimSetup.SpawnParticlesInGrid(numOfParticles, particleSize, particleSpacing, SIM_AREA_WIDTH, SCREEN_HEIGHT)
    elif option == RANDOM:
        positions = SimSetup.SpawnParticlesRandomly(numOfParticles, particleSize, SIM_AREA_WIDTH, SCREEN_HEIGHT)


def Start(option):

    InitializeArrays(option)


def Update(paused):
    screen.fill(backgroundColorDark)
    #render.DrawAllParticlesWithVelColors(positions, velocities, waterColor, particleSize)
    render.DrawAllParticles(positions, waterColor, particleSize)

    if not paused:
        SimulationStep()
        #Debug()
    
    gui.Render(screen, framerate)

    pygame.display.flip()
    clock.tick(framerate)


def Reset():
    global positions, predictedPositions, velocities, densities, spatialIndecies, spatialOffests
    positions = []
    predictedPositions = []
    velocities = []
    densities = []
    spatialIndecies = []
    spatialOffests = []


def Debug():
    mousePos = pygame.mouse.get_pos()
    center = (SIM_AREA_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.circle(screen, (200, 200, 200), center, smoothingRadius, 1)

    print(targetDensity, np.average([d[0] for d in densities]))


def MainLoop():
    paused = True 

    Start(GRID) 
    Update(paused)

    running = True
    while running:
        sliderMoved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    Reset()
                    Start(GRID)
                    paused = True
                if event.key == pygame.K_SPACE:
                    if paused:
                        # Unpause
                        paused = False
                    else:
                        # Pause
                        paused = True

            sliderMoved = gui.ProcessEvents(event)

        if sliderMoved:
            UpdateVariables()
        

        Update(paused)
        
        

    pygame.quit()

MainLoop()