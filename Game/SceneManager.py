import sys

import pygame
from Main import CLOCK, SCREEN
from Utility import MainMenu
from Utility.Constants import FPS
from Utility.MainMenu import *

class Scene:
    def handle_events(self, events):
        pass
    def update(self):
        pass
    def draw(self, screen):
        pass

class MenuScene(Scene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If they click, we return the name of the next scene
                return "GAMEPLAY"
        return None

    def draw(self, screen, events):
        MainMenu(screen, events)


class SceneManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(Constants.ScreenSize)
        self.clock = pygame.time.Clock()
        
        # Dictionary of available scenes
        self.scenes = {
            "MENU": MenuScene(),
            "GAME": None # You would create a GameplayScene class later
        }
        self.active_scene = self.scenes["MENU"]

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # 1. Handle Events & Switch Scene if needed
            next_scene = self.active_scene.handle_events(events)
            if next_scene:
                self.active_scene = self.scenes[next_scene]

            # 2. Update and Draw
            self.active_scene.update()
            self.active_scene.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(Constants.FPS)