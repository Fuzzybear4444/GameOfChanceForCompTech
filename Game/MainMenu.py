import pygame
import Constants
from GUI import Button, ExitButton

# We declare these as None first, or just define them inside a class
CasinoBackground = None
Exit_Button = None
Start_Button = None

def init_menu():
    """Call this ONCE after pygame.init() to load assets"""
    global CasinoBackground, Exit_Button, Start_Button
    
    # Load assets here
    CasinoBackground = pygame.image.load("C:\\Users\\Student\\Downloads\\CasinoBackground.jpg")
    CasinoBackground = pygame.transform.smoothscale(CasinoBackground, Constants.ScreenSize)
  
    
    # Create buttons here
    Exit_Button = ExitButton(350, 775, 300, 100, (0, 100, 200), (0, 150, 255), "Exit", 24)
    Start_Button = Button(350, 900, 300, 100, (0, 100, 200), (0, 150, 255), "Start", 24)

def MainMenu(SCREEN, events):
    SCREEN.blit(CasinoBackground, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    
    # We loop through the events here so every button gets a chance to see them
    for event in events:
        Exit_Button.handle_event(event)
        Start_Button.handle_event(event)
    
    # Update and Draw happen once per frame
    Exit_Button.update(mouse_pos)
    Exit_Button.draw(SCREEN) 
    
    Start_Button.update(mouse_pos)
    Start_Button.draw(SCREEN)