# main.py
import os

import pygame
import sys
import Utility.Constants as Constants
from Utility.MainMenu import Scene, MenuScene
from Utility.Colors import BLACK, WHITE

# --- A placeholder for your actual game ---
class GameplayScene(Scene):
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 48)
        
        # 1. LOAD ONCE DURING INITIALIZATION
        img_path = r"C:\Users\Student\Downloads\CasinoBackground2.jpg"
        if os.path.exists(img_path):
            raw_bg = pygame.image.load(img_path).convert()
            self.background = pygame.transform.smoothscale(raw_bg, Constants.ScreenSize)
        else:
            print("Warning: Background image not found! Using a flat color instead.")
            self.background = pygame.Surface(Constants.ScreenSize)
            self.background.fill((30, 30, 40)) # Dark grayish blue fallback

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU" # Press ESC to go back to menu
        return None

    def draw(self, screen): # 2. ADD 'screen' PARAMETER HERE
        # 3. ONLY DRAW THE PRE-LOADED IMAGE HERE
        screen.blit(self.background, (0, 0))
# ------------------------------------------

class SceneManager:
    def __init__(self):
        # 1. Start engines
        pygame.init()
        
        # 2. Build window FIRST
        # This is the "Video Mode" the error is looking for
        self.screen = pygame.display.set_mode(Constants.ScreenSize)
        pygame.display.set_caption("Casino Game of Chance")
        self.clock = pygame.time.Clock()
        
        # 3. NOW create the scenes
        # Because self.screen exists, .convert() will now work!
        self.scenes = {
            "MENU": MenuScene(),
            "GAME": GameplayScene() 
        }
        self.active_scene = self.scenes["MENU"]

    def run(self):
        running = True
        while running:
            # Collect events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            # Scene Logic
            next_scene_key = self.active_scene.handle_events(events)
            
            # Check for scene switching or quitting
            if next_scene_key == "QUIT":
                running = False
            elif next_scene_key and next_scene_key in self.scenes:
                self.active_scene = self.scenes[next_scene_key]

            # Update & Draw
            self.active_scene.update()
            self.active_scene.draw(self.screen)

            # Refresh
            pygame.display.flip()
            self.clock.tick(Constants.FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SceneManager()
    game.run()