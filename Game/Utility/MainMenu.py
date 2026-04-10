# Utility/MainMenu.py
import pygame
import os
import Utility.Constants as Constants
from Utility.GUI import Button, ExitButton
# Note: We don't import Scene from SceneManager here to avoid circular imports.
# We just assume the methods exist.

class MenuScene:
    def __init__(self):
        img_path = r"C:\Users\Student\Downloads\CasinoBackground.jpg"
        if os.path.exists(img_path):
            raw = pygame.image.load(img_path).convert()
            self.background = pygame.transform.smoothscale(raw, Constants.ScreenSize)
        else:
            self.background = pygame.Surface(Constants.ScreenSize)
            self.background.fill(pygame.Color("black"))
            
        self.start_button = Button(350, 800, 300, 80, (0, 100, 200), (0, 150, 255), "Start", 32)
        self.exit_button = ExitButton(350, 900, 300, 80, (150, 0, 0), (200, 0, 0), "Exit", 32)

    def handle_events(self, events):
        for event in events:
            if self.start_button.handle_event(event): return "HUB"
            if self.exit_button.handle_event(event):  return "QUIT"
        return None

    def update(self):
        m_pos = pygame.mouse.get_pos()
        self.start_button.update(m_pos)
        self.exit_button.update(m_pos)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.start_button.draw(screen)
        self.exit_button.draw(screen)