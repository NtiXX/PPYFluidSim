import pygame
import numpy as np

from Rendering import Rendering
from Gui import Gui
import Computing
import SimSetup

# Pygame init
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Python fluid simulation")
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)
framerate = 120

screenSize = (SCREEN_WIDTH, SCREEN_HEIGHT)
guiSize = (350, SCREEN_HEIGHT)
gui = Gui(screenSize, guiSize)

SIM_AREA_WIDTH = SCREEN_WIDTH - guiSize[0]

render = Rendering(screen, SIM_AREA_WIDTH, SCREEN_HEIGHT)

# Start options
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
particleSize = 8
numOfParticles = 200
particleSpacing = 25

# Simulation settings
gravity = 0
collisionDamping = 0.5
particleMass = 1
smoothingRadius = 50
targetDensity = 5 / 10000.0
pressureMultiplier = 500
viscosityStrength = 0.5
mouseInput = 0 # 1 - pushing appart, -1 pulling in
mouseInteractionStrength = 20 
mouseInteractionRadius = 50

#Debug
densityThreshhold = 0.0000001

# Init particle arrays1
positions = []


def Start(option):
    """
    Runs once at the start to initialize the simulation.

    Args:
        option: The start option, e.g., GRID or RANDOM.
    """
    SpawnParticles(option)
    SetupGui()

    Computing.InitializeValues(
        SCREEN_SIZE=(screenSize),
        GUI_SIZE=guiSize,
        gravity=gravity,
        collisionDamping=collisionDamping,
        particleSize=particleSize,
        particleMass=particleMass,
        smoothingRadius=smoothingRadius,
        targetDensity=targetDensity,
        pressureMultiplier=pressureMultiplier,
        viscosityStrength=viscosityStrength,
        densityThreshhold=densityThreshhold,
        mouseInteractionStrength=mouseInteractionStrength,
        mouseInteractionRadius=mouseInteractionRadius
        )
    
    Computing.InitializeArrays(positions)


def SpawnParticles(option):
    """
    Spawns particles in the simulation based on the given option.

    Args: 
        option: The spawning option, e.g., GRID or RANDOM.
    """
    global positions
    if option == GRID:
        positions = SimSetup.SpawnParticlesInGrid(numOfParticles, particleSize, particleSpacing, SIM_AREA_WIDTH, SCREEN_HEIGHT)
    elif option == RANDOM:
        positions = SimSetup.SpawnParticlesRandomly(numOfParticles, particleSize, SIM_AREA_WIDTH, SCREEN_HEIGHT)


def SetupGui():
    """ 
    Sets up GUI, sliders and buttons
    """
    global gui

    gui.AddSlider(numOfParticles, "Num Of Particles", 1, 1000)
    gui.AddSlider(particleSize, "Particle Size", 1, 100)
    gui.AddSlider(particleSpacing, "Particle Spacing", 1, 100)
    gui.AddSlider(gravity, "Gravity", -5.0, 5.0)
    gui.AddSlider(collisionDamping, "Collision Damping", -1, 1)
    gui.AddSlider(smoothingRadius, "Smoothing Radius", 1, 150)
    gui.AddSlider(targetDensity, "Target Density", 0, 4.0/ 100.0)
    gui.AddSlider(pressureMultiplier,"Pressure Multiplier", 0, 1000)
    gui.AddSlider(viscosityStrength,"Viscosity Strength", 0, 1.0)
    gui.AddSlider(mouseInteractionStrength,"Input Strength", 1, 200)
    gui.AddSlider(mouseInteractionRadius,"Input Radius", 1, 150)

    gui.AddResetButtons()


def Update(paused):
    """
    Runs every iteration to update the simulation state.
    """
    screen.fill(backgroundColorDark)
    #render.DrawAllParticlesWithVelColors(positions, velocities, waterColor, particleSize)
    render.DrawAllParticles(positions, waterColor, particleSize)

    if not paused:
        mousePos = pygame.mouse.get_pos()
        Computing.SimulationStep(mousePos)
        #Debug()

        if mouseInput != 0:
            render.BrushRendering(backgroundColorLight, mousePos, mouseInteractionRadius)
    
    gui.Render(screen, framerate)

    pygame.display.flip()
    clock.tick(framerate)


def UpdatePositions():
    """
    Updates the positions of particles from the computing module.
    """
    global positions
    positions = Computing.GetPositions()


def UpdateSettings():
    """
    Updates simulation settings based on GUI slider values.
    """
    global numOfParticles, particleSpacing, particleSize, gravity, collisionDamping, smoothingRadius, targetDensity, pressureMultiplier, viscosityStrength, mouseInteractionStrength, mouseInteractionRadius
    
    values = gui.GetSliderValues()

    if numOfParticles != values[0] or particleSpacing != values[2]:
        numOfParticles = values[0]
        particleSpacing = values[2]
        Reset(GRID)

    particleSize=values[1]
    gravity=values[3]
    collisionDamping=values[4]
    smoothingRadius=values[5] 
    targetDensity=values[6] 
    pressureMultiplier=values[7]
    viscosityStrength = values[8]
    mouseInteractionStrength=values[9]
    mouseInteractionRadius=values[10]

    Computing.UpdateSettings(
        particleSize=particleSize, 
        gravity=gravity, 
        collisionDamping=collisionDamping, 
        smoothingRadius=smoothingRadius, 
        targetDensity=targetDensity, 
        pressureMultiplier=pressureMultiplier,
        viscosityStrength=viscosityStrength,
        mouseInteractionStrength=mouseInteractionStrength,
        mouseInteractionRadius=mouseInteractionRadius
    )


def Reset(option):
    """
    Resets the simulation with the given spawning option.

    Args:
        option: The reset option, e.g., GRID or RANDOM.
    """
    global positions, predictedPositions, velocities, densities, spatialIndecies, spatialOffests
    positions = []
    predictedPositions = []
    velocities = []
    densities = []
    spatialIndecies = []
    spatialOffests = []

    SpawnParticles(option)
    
    Computing.InitializeValues(
        SCREEN_SIZE=(screenSize),
        GUI_SIZE=guiSize,
        gravity=gravity,
        collisionDamping=collisionDamping,
        particleSize=particleSize,
        particleMass=particleMass,
        smoothingRadius=smoothingRadius,
        targetDensity=targetDensity,
        pressureMultiplier=pressureMultiplier,
        viscosityStrength=viscosityStrength,
        densityThreshhold=densityThreshhold
        )
    
    Computing.InitializeArrays(positions)


def Debug():
    """
    Debug function to display additional information, such as a circle around the mouse position.
    """
    mousePos = pygame.mouse.get_pos()
    center = np.array((SIM_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
    pygame.draw.circle(screen, (200, 200, 200), mousePos, smoothingRadius, 1)


def HandleMouseInput(event):
    """
    Handles mouse input events to update the simulation based on user interactions.
    """
    global mouseInput
    changed = False
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == pygame.BUTTON_LEFT:
            mouseInput = 1 
            changed = True
        elif event.button == pygame.BUTTON_RIGHT:
            mouseInput = -1
            changed = True
            
    if event.type == pygame.MOUSEBUTTONUP:
        mouseInput = 0
        changed = True

    if changed:
        Computing.UpdateSettings(mouseInput=mouseInput)
    
    
def MainLoop():
    """
    Main loop of the simulation, handling events and updates.
    """
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
                if event.key == pygame.K_SPACE:
                    if paused:
                        # Unpause
                        paused = False
                    else:
                        # Pause
                        paused = True

            HandleMouseInput(event)

            sliderMoved = gui.ProcessEvents(event)
            
            if sliderMoved == 1:
                UpdateSettings()
            if sliderMoved == 2:
                button = gui.GetPressedButton(event)
                if button == "RESET GRID":
                    Reset(GRID)
                    paused = True
                elif button == "RESET RANDOM":
                    Reset(RANDOM)
                    paused = True
        
        Update(paused)
        
    pygame.quit()

MainLoop()

