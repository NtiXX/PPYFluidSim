import pygame_gui
import pygame
import numpy as np
import pygame_gui.elements.ui_text_box

class Gui:

    def __init__(self, screenSize, guiSize):
        """ Initialize gui with given screen size and gui size"""

        self.SCREEN_WIDTH = screenSize[0]
        self.SCREEN_HEIGHT = screenSize[1]
        self.GUI_WIDTH = guiSize[0]
        self.GUI_HEIGHT = guiSize[1]
        self.surface = pygame.Surface(guiSize)
        self.manager = pygame_gui.UIManager(screenSize)
        self.sliderArray = []
        self.variableArray = []
        self.labels = []
        self.buttons = []
        self.gridResetButton = 0
        self.randomResetButton = 0

        self.backgoundColorLight = (210, 210, 210)
        self.textColorDark = (10, 10, 14)
        
        self.sliderLength = self.GUI_WIDTH - 40
        self.sliderHeight = 40
        self.sliderYPadding = 10
        self.topPadding = 20
        self.sidePadding = (self.GUI_WIDTH - self.sliderLength) // 2
        self.labelHeight = 0

        self.surface.fill(self.backgoundColorLight)


    def AddSlider(self, value, variableName, minValue, maxValue):
        """ 
        Adds slider with label to GUI. Adds each slider, name and label to arrays for keeping track

        Args:
            value - Initial value of the slider
            variableName - Name of the variable the slider controls
            minValue - Minimum value of the slider
            maxValie - Maximum value of the sldier
        """

        numberOfSliders = len(self.sliderArray)

        position = (self.SCREEN_WIDTH - self.GUI_WIDTH + self.sidePadding, numberOfSliders * (self.sliderHeight + self.sliderYPadding) + self.topPadding)
        size = (self.sliderLength, self.sliderHeight)

        newSlider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(position, size),
            start_value=value,
            value_range=(minValue, maxValue),
            manager=self.manager,
            
        )

        self.sliderArray.append(newSlider)
        self.variableArray.append(variableName)

        label = self.CreateLabel(variableName, position, size)
        self.labels.append(label)
        

    def AddResetButtons(self):
        """
        Adds reset buttons (grid and random reset) to the GUI.
        """
        size = (self.sliderLength, self.sliderHeight)

        self.gridResetButton = self.CreateButton("RESET GRID", size)
        self.randomResetButton = self.CreateButton("RESET RANDOM", size)


    def CreateButton(self, text, size):
        """
        Creates a button with the given text and size.

        Returns: The created button.
        """
        numberOfSliders = len(self.sliderArray)
        slidersBottomEdge = numberOfSliders * (self.sliderHeight + self.sliderYPadding) + self.topPadding
        numberOfButtons = len(self.buttons)

        position = ((self.SCREEN_WIDTH - self.GUI_WIDTH) + self.sidePadding, slidersBottomEdge + ((self.sliderHeight + self.sliderYPadding) * numberOfButtons))
        position = np.array(position)

        button =  pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(position, size),
            text=text,
            manager=self.manager,
        )

        self.buttons.append(button)

        return button


    def CreateLabel(self, text, position, size):
        """
        Creates a label with the given text, position, and size.

        Returns: The created label.
        """
        position = np.array(position) - np.array((0, self.labelHeight))
        return pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(position, size),
            text=text,
            manager=self.manager,  
        )
    

    def UpdateLables(self):
        """
        Updates the text of all labels to reflect the current value of their associated sliders.
        """
        for i in range(len(self.sliderArray)):
            name = self.variableArray[i]
            slider = self.sliderArray[i]
            currentValue = slider.get_current_value()
            self.labels[i].set_text(f"{name}: {round(currentValue, 6)}")
    

    def ProcessEvents(self, event):
        """
        Processes Pygame events and updates the UI manager.

        Returns: 1 if a slider is moved, 2 if a button is pressed, 0 otherwise.
        """
        self.manager.process_events(event)
        
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            return 1
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            return 2
        return 0


    def GetPressedButton(self, event):
        """
        Returns the text of the button that was pressed.
        """
        for button in self.buttons:
            if event.ui_element == button:
                return button.text


    def Render(self, screen, framerate):
        """
        Renders the GUI on the screen.

        Args:
            screen: The screen surface to render the GUI on.
            framerate: The current framerate of the application.

        """
        self.manager.update(framerate)
        self.UpdateLables()
        screen.blit(self.surface, (self.SCREEN_WIDTH - self.GUI_WIDTH, 0))
        self.manager.draw_ui(screen)


    def GetSliderValues(self):
        """
        Gets the current values of all sliders.

        Returns: A list of current values of all sliders.
        """
        return [slider.get_current_value() for slider in self.sliderArray]
