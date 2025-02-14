import numpy as np

import FluidMaths as fm
import SpatialHash as sh

SCREEN_SIZE = 0
GUI_SIZE = 0

# Settings
numOfParticles = 0
gravity = 0
collisionDamping = 0
particleMass = 0
particleSize = 0
smoothingRadius = 0
targetDensity = 0
pressureMultiplier = 0
viscosityStrength = 0
densityThreshhold = 0
mouseInput = 0 # 1 - pushing appart, -1 pulling in
mouseInteractionStrength = 0 
mouseInteractionRadius = 0

# Init particle arrays
positions = []
predictedPositions = []
velocities = []
densities = [] # Density

# Init special lookup array

spatialIndecies = [] # [particleIndex, cellHash, cellKey] sorted by cellKey, holding data for finding near particles, which particle in what cell 
spatialOffsets = [] # When looking for points in given cell, spatialOffsets[cellKey] returns an index of spatialIndecies where there is the first occurance of particle in a given cell:
                    #     cellKey -> the cell key of the cell where we want to what points are inside
                    #     index = spatialOffsets[cellKey] ex. 4
                    #     indexData = spatialIndecies[index] -> [particleIndex, cellHash, cellKey], index = 4, is the fisrt entry of point in given cell, points in cell continiue (index++) until original cellKey != cellKey from indexData 

## Functions
def DensityFunction(radius, distance):
    """
    Computes the density using the Spiky function with power 2.
    """
    return fm.SpikyFunctionPow2(radius, distance)


def DensityDerivatice(radius, distance):
    """
    Computes the derivative of the density using the Spiky function with power 2.
    """
    return fm.SpikyFunctionPow2Derivative(radius, distance)


def ViscosityFunction(radius, distance):
    """
    Computes the viscosity using the Smooth function with power 3.
    """
    return fm.SmoothFunctionPow3(radius, distance)

## Variable Initialazation
def InitializeArrays(initialPositions):
    """
    Run once at the start, initializes the particle arrays with the given initial positions.
    
    Args:
        initialPositions: A list of initial particle positions generated by Simulation Setup.
    """
    global numOfParticles, positions, predictedPositions, velocities, densities, spatialIndecies, spatialOffsets

    positions = initialPositions
    numOfParticles = len(positions)

    predictedPositions = np.empty(numOfParticles, dtype=object)
    velocities = np.array([np.zeros(2, dtype=float) for x in range(numOfParticles)])
    densities = np.empty(numOfParticles, dtype=object)
  
    spatialIndecies = np.empty(numOfParticles, dtype=object)
    spatialOffsets = np.empty(numOfParticles, dtype=int)


def InitializeValues(**values):
    """
    Initializes simulation settings with the provided values.

    Args:
        **values: Keyword arguments representing the settings to initialize.
    """

    global SCREEN_SIZE, GUI_SIZE, gravity, collisionDamping, particleSize, particleMass, smoothingRadius, targetDensity, pressureMultiplier, viscosityStrength, densityThreshhold, mouseInteractionStrength, mouseInteractionRadius

    for key, value in values.items():
        globals()[key] = value


def UpdateSettings(**values):
    """ 
    Updates setting variables whenever the user changes them
    
    Args:
        **values: Keyword arguments representing the settings to update.
    """
    global particleSize, gravity, collisionDamping, smoothingRadius, targetDensity, pressureMultiplier, viscosityStrength, mouseInteractionStrength, mouseInteractionRadius, mouseInput

    for key, value in values.items():
        globals()[key] = value

## Computing
def HandleCollisions(particleIndex):
    """ 
    Detects boundary collision by checking if new position is in bounds. 
    If not, places point on the boundary and reverces it's velocity.

    Returns: A list containing the new position and velocity of the particle.
    """
    new_position = positions[particleIndex] + velocities[particleIndex]
    velocity = velocities[particleIndex]

    simAreaWidth = SCREEN_SIZE[0] - GUI_SIZE[0]

    HALF_BOUND_X = (simAreaWidth - particleSize) * 0.5
    HALF_BOUND_Y = (SCREEN_SIZE[1] - particleSize) * 0.5

    # Check for collision horizontally
    if abs(new_position[0] - HALF_BOUND_X) >=  HALF_BOUND_X:
        new_position[0] = HALF_BOUND_X * np.sign(new_position[0]) + HALF_BOUND_X
        velocity[0] *= -1 * collisionDamping

    # Check for collision vertically
    if abs(new_position[1] - HALF_BOUND_Y) >=  HALF_BOUND_Y:
        new_position[1] = HALF_BOUND_Y * np.sign(new_position[1]) + HALF_BOUND_Y
        velocity[1] *= -1 * collisionDamping

    return [new_position, velocity]


def UpdateExternalForces(particleIndex, mousePos):
    """ 
    Adding extarnal forces, such as gravity, and interaction force, to a particle at given index (particleIndex)
    """  
    gravityAcceleration = np.array((0, gravity))
    velocity = velocities[particleIndex]

    # Alter acceleration by user interaction
    if mouseInput != 0:
        particlePos = positions[particleIndex]

        offsetToInputt = mousePos - particlePos
        distanceToInput = np.linalg.norm(offsetToInputt)
        forceStrength = (distanceToInput / mouseInteractionRadius)

        if distanceToInput < mouseInteractionRadius:
            directionToInput = offsetToInputt / distanceToInput if distanceToInput > 0 else fm.GetRandomDirection()

            gravityAcceleration = gravityAcceleration + (directionToInput * mouseInteractionStrength * mouseInput * forceStrength)
            gravityAcceleration -= velocity
    
    # Adding gravity 
    velocities[particleIndex] += gravityAcceleration

    # Prediction
    predictionFactor = 1
    predictedPositions[particleIndex] = positions[particleIndex] + (velocities[particleIndex] * predictionFactor)


def UpdateSpatialHash():
    """
    Updates the spatial hash table for particle positions in a spatial grid.

    This function calculates the cell hash and key for each particle, stores this
    information in the spatial indecies table, sorts the table by cell key, and computes 
    the offsets for each unique cell key.
    """
    global spatialIndecies, spatialOffsets

    for particleIndex in range(numOfParticles):
        # Reset offsets so that each simulation iteration has a fresh offset array
        spatialOffsets[particleIndex] = -1

        # Update spatialIndecies array
        cell = sh.GetCell(predictedPositions[particleIndex], smoothingRadius)
        cellHash = sh.HashCell(cell)
        cellKey = sh.GetKeyFromHash(cellHash, numOfParticles)

        spatialIndecies[particleIndex] = [particleIndex, cellHash, cellKey]

    # Sorting spatialIndecies by cellKey
    spatialIndecies = sorted(spatialIndecies, key=lambda x : x[2])

    # Calculate Offsets
    for particleIndex in range(numOfParticles):
        # Calculate start indices of each unique cell key in spatial lookup
        indexData = spatialIndecies[particleIndex]
        previousIndexData = spatialIndecies[particleIndex - 1]

        cellKey = indexData[2]
        previousCellKey = -1 if particleIndex == 0 else previousIndexData[2]
        
        # If first occurance of key in spaitalIndecies
        if cellKey != previousCellKey:
            spatialOffsets[cellKey] = particleIndex

# Densities
def CalculateDensityNaive(samplePoint):
    """
    Old version of density calculation, used before the spatial hash algorithm
    Bad complexity, looping over every single particle - O(n)
    Calculates the density at a given sample point using a naive approach.
    """
    density = 0
    mass = 1
    for point in positions:
        dst = np.linalg.norm(point - samplePoint)
        influence = fm.SpikyFunctionPow2(smoothingRadius, dst)    
        density += mass * influence

    return density


def CalculateDensity(particleIndex):
    """
    Calculates the density of a particle at the given index using a spatial hash for efficiency.
    """
    position = predictedPositions[particleIndex]
    originCell = sh.GetCell(position, smoothingRadius)
    density = 0

    # Neighbour search
    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffsets[neighbourKey]

        while currIndex < numOfParticles:
            indexData = spatialIndecies[currIndex]
            currIndex += 1

            # Break if no longer looking points in neighbouring cell
            if indexData[2] != neighbourKey: break
            # Skip if hash does not match, additonal checking if looking at real neighbour, since grid can be infinite
            if indexData[1] != neighbourHash: continue

            neighbourIndex = indexData[0]

            neighbourPosition = predictedPositions[neighbourIndex]
            offsetToNeighbour = neighbourPosition - position
            distanceToNeighbour = np.linalg.norm(offsetToNeighbour)

            # Skip if not within radius
            if distanceToNeighbour >= smoothingRadius: continue

            # Calculate densities
            density += particleMass * fm.SpikyFunctionPow2(smoothingRadius, distanceToNeighbour)

    return density


def UpdateDensity(particleIndex):
    """
    Updates the density of a particle at the given index.
    """
    global densities
    densities[particleIndex] = CalculateDensity(particleIndex)

# Pressure forces
def CalculatePressureForce(particleIndex):
    """
    Calculates the pressure force acting on a particle at the given index using a spatial hash for efficiency.
   Pressure force is calculated by using the DensityDerivative for the slope value
    """
    position = predictedPositions[particleIndex]
    density = densities[particleIndex]
    pressure = fm.PressureFromDensity(density, targetDensity, pressureMultiplier)

    originCell = sh.GetCell(position, smoothingRadius)
    pressureForce = np.zeros(2, dtype=float)

    # Neighbour search
    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffsets[neighbourKey]

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
            distanceToNeighbour = np.linalg.norm(offsetToNeighbour)

            # Skip if not within radius
            if distanceToNeighbour >= smoothingRadius: continue

            #Calculate pressure force
            directionToNeighbour = offsetToNeighbour / distanceToNeighbour if distanceToNeighbour > 0 else fm.GetRandomDirection()

            neighbourDensity = densities[neighbourIndex]
            neighbourPressure = fm.PressureFromDensity(neighbourDensity, targetDensity, pressureMultiplier)
            sharedPressure = (pressure + neighbourPressure) * 0.5 # Newton's third law of motion

            pressureForce += directionToNeighbour * DensityDerivatice(smoothingRadius, distanceToNeighbour) * sharedPressure / neighbourDensity
     
    return pressureForce
 

def UpdatePressureForce(particleIndex):
    """
    Updates the pressure force acting on a particle at the given index.
    """
    global velocities
    
    density = densities[particleIndex]
    
    pressureForce = CalculatePressureForce(particleIndex)

    if density > densityThreshhold:
        acceleration = pressureForce / density
        velocities[particleIndex] += acceleration  

# Viscosities
def CalculateViscosityForce(particleIndex):
    """
    Calculates the viscosity force acting on a particle at the given index using a spatial hash for efficiency
    Viscostiy is calculated by bluring together the velosities of nearby regions of fluid
    """
    position = predictedPositions[particleIndex]
    originCell = sh.GetCell(position, smoothingRadius)

    viscosityForce = 0
    velocity = velocities[particleIndex]

    for i in range(9):
        neighbourHash = sh.HashCell(originCell + sh.offsets[i])
        neighbourKey = sh.GetKeyFromHash(neighbourHash, numOfParticles)
        currIndex = spatialOffsets[neighbourKey]

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
            distanceToNeighbour = np.linalg.norm(offsetToNeighbour)

            # Skip if not in radius
            if distanceToNeighbour >= smoothingRadius: continue

            # Calculate viscosity
            neighbourVelocity = velocities[neighbourIndex]
            viscosityForce += (neighbourVelocity - velocity) * ViscosityFunction(smoothingRadius, distanceToNeighbour)

    return viscosityForce


def UpdateViscosity(particleIndex):
    """
    Updates the viscosity force acting on a particle at the given index.
    """
    viscosityForce = CalculateViscosityForce(particleIndex)
    velocities[particleIndex] += viscosityForce * viscosityStrength


def UpdatePosition(particleIndex):
    """
    Updates the position and velocity of a particle at the given index based on collision handling.
    """
    newValues = HandleCollisions(particleIndex)

    positions[particleIndex] = newValues[0]
    velocities[particleIndex] = newValues[1]


def SimulationStep(mousePos):
    """"
    Performs a single simulation step, updating forces, densities, and positions for all particles.
    For every particle: 
        Update External Forces
        Update Spatial Hash
        Update Density
        Update Pressure Force
        Update Viscosity
        Update Position
    """
    for particleIndex in range(numOfParticles):
        UpdateExternalForces(particleIndex, mousePos)

    UpdateSpatialHash()
    
    for particleIndex in range(numOfParticles):
        UpdateDensity(particleIndex)

    for particleIndex in range(numOfParticles):    
        UpdatePressureForce(particleIndex)
        UpdateViscosity(particleIndex)
        UpdatePosition(particleIndex)


def GetPositions():
    """
    Returns the current positions of all particles.
    """
    return positions