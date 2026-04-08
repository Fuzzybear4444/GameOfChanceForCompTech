import pygame
import sys
from random import *
import Constants
from GUI import *
from Colors import *
from MainMenu import * # This imports init_menu and MainMenu directly

# 1. Setup / Constants
pygame.init()


init_menu() 

SCREEN = pygame.display.set_mode(Constants.ScreenSize)
pygame.display.set_caption("My Pygame Project")

CLOCK = pygame.time.Clock()
FPS = Constants.FPS

# 3. Main Game Loop
running = True
while running:
    # Get the list of all events that happened this frame
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    # --- LOGIC & DRAWING ---
    # We move MainMenu OUTSIDE the 'for event' loop.
    # This ensures the background and buttons are drawn 60 times per second.
    
    # IMPORTANT: We pass the list of events so the buttons can check for clicks
    # Note: If your MainMenu function expects a single event, 
    # you may need to loop through 'events' inside MainMenu.py instead.
    MainMenu(SCREEN, events) 
    
    # Update the physical display
    pygame.display.flip()
    
    # Maintain steady framerate
    CLOCK.tick(FPS) 

# 4. Cleanup
pygame.quit()
sys.exit()