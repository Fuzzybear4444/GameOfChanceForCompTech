import pygame
import sys
from random import *
import Constants
from GUI import *
# 1. Setup / Constants
pygame.init()

SCREEN = pygame.display.set_mode(Constants.ScreenSize)

pygame.display.set_caption("My Pygame Project")

CLOCK = pygame.time.Clock()
FPS = Constants.FPS

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Matching the order: x, y, width, height, color, hover_color, text, textSize
Exit_Button = ExitButton(150, 120, 100, 50, (0, 100, 200), (0, 150, 255), "Exit", 24)


running = True
while running:
    mouse_pos = pygame.mouse.get_pos() # Get mouse position for hovering
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        
        # 3. Check for CLICKS (USING the class method)
    Exit_Button.handle_event(event)
    # 4. UPDATE and DRAW
    Exit_Button.update(mouse_pos) # Checks if mouse is over button
    
    SCREEN.fill((30, 30, 30))   # Background color
    Exit_Button.draw(SCREEN)      # Renders the button to the screen
    
    pygame.display.flip()
    CLOCK.tick(FPS) # Limit to 60 frames per second
