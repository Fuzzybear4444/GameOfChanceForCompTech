# SceneManager.py
import pygame
import sys
import os
import Utility.Constants as Constants
from Utility.Colors import *
from Utility.GUI import Button
from Utility.EconManager import economy
# 1. THE BASE CLASS (Everything else inherits from this)
class Scene:
    def handle_events(self, events): return None
    def update(self): pass
    def draw(self, screen): pass

# 2. THE HUB (The game selection screen)
class HubScene(Scene):
    def __init__(self):
        img_path = r"C:\Users\Student\Downloads\CasinoBackground2.jpg"
        if os.path.exists(img_path):
            raw = pygame.image.load(img_path).convert()
            self.background = pygame.transform.smoothscale(raw, Constants.ScreenSize)
        else:
            self.background = pygame.Surface(Constants.ScreenSize)
            self.background.fill((20, 40, 20))
        w, h = Constants.ScreenSize
        #self.btn_casino = Button(w//2 - 150, 300, 300, 80, (60, 60, 100), (100, 100, 160), "Casino Game", 32
        self.btn_dating = Button(88, 450, 99, 30, (100, 60, 100), (160, 100, 160), "Isaac Dating Sim", 12)

    def handle_events(self, events):
        for event in events:
           # if self.btn_casino.handle_event(event): return "CASINO"
            if self.btn_dating.handle_event(event): return "DATING"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"
        return None

    def update(self):
        m_pos = pygame.mouse.get_pos()
        #self.btn_casino.update(m_pos)
        self.btn_dating.update(m_pos)

    def draw(self, screen):
        from Utility.EconManager import EconomyManager
        
        screen.blit(self.background, (0, 0))
        economy.draw_balance(screen)
        self.btn_dating.draw(screen)
        

# 4. THE MANAGER
class SceneManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(Constants.ScreenSize)
        self.clock = pygame.time.Clock()
        
        # Delayed imports to prevent circular dependency
        from Utility.MainMenu import MenuScene
        from DatingSim.isaacDatingSim import DatingSimScene
        self.scenes = {
            "MENU": MenuScene(),
            "HUB": HubScene(),
            "DATING": DatingSimScene() 
        }
        self.active_scene = self.scenes["MENU"]

    def run(self):
            while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()

                next_key = self.active_scene.handle_events(events)
                
                if next_key == "QUIT": 
                    break
                elif next_key and next_key in self.scenes:
                    # --- ADD THIS RESET LOGIC ---
                    if next_key == "DATING":
                        self.scenes["DATING"].reset_game()
                    
                    # Switch the scene
                    self.active_scene = self.scenes[next_key]
                # ----------------------------

                self.active_scene.update()
                self.active_scene.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(Constants.FPS)