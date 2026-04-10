# Utility/MainMenu.py
import pygame
import os
import Utility.Constants as Constants
from Utility.GUI import Button, ExitButton

# A base template for all scenes
class Scene:
    def handle_events(self, events): pass
    def update(self): pass
    def draw(self, screen): pass

class MenuScene(Scene):
    def __init__(self):
        # Load Background Image (Safely)
        img_path = "C:\\Users\\Student\\Downloads\\CasinoBackground.jpg"
        if os.path.exists(img_path):
            raw_bg = pygame.image.load(img_path).convert()
            self.background = pygame.transform.smoothscale(raw_bg, Constants.ScreenSize)
        else:
            print("Warning: Background image not found! Using a flat color instead.")
            self.background = pygame.Surface(Constants.ScreenSize)
            self.background.fill((30, 30, 40)) # Dark grayish blue fallback
        
        # Create buttons
        self.exit_button = ExitButton(350, 775, 300, 100, (0, 100, 200), (0, 150, 255), "Exit", 24)
        self.start_button = Button(350, 900, 300, 100, (0, 100, 200), (0, 150, 255), "Start", 24)

    def handle_events(self, events):
        for event in events:
            # If start is clicked, tell the manager to switch to GAME
            if self.start_button.handle_event(event):
                return "GAME"
            
            # If exit is clicked, tell the manager to QUIT
            if self.exit_button.handle_event(event):
                return "QUIT"
                
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.exit_button.update(mouse_pos)
        self.start_button.update(mouse_pos)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.exit_button.draw(screen)
        self.start_button.draw(screen)