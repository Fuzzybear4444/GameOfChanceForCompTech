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
            self.background = pygame.transform.smoothscale(raw, Constants.Screen_Size)
        else:
            self.background = pygame.Surface(Constants.Screen_Size)
            self.background.fill((20, 40, 20))
        w, h = Constants.Screen_Size
        self.btn_blackjack = Button(605, 500, 105, 30, (60, 60, 100), (100, 100, 160), "Blackjack", 20)
        self.btn_dating = Button(88, 450, 99, 30, (100, 60, 100), (160, 100, 160), "Isaac Dating Sim", 12)
        self.btn_russian_roulette = Button(88, 700, 99, 30, (100, 60, 100), (160, 100, 160), "RUSSIANROULETTE", 12)

    def handle_events(self, events):
        for event in events:
           # if self.btn_casino.handle_event(event): return "CASINO"
            if self.btn_dating.handle_event(event): return "DATING"
            if self.btn_blackjack.handle_event(event): return "BLACKJACK"
            if self.btn_russian_roulette.handle_event(event): return "RUSSIANROULETTE"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "HUB"
        return None

    def update(self):
        m_pos = pygame.mouse.get_pos()
        #self.btn_casino.update(m_pos)
        self.btn_dating.update(m_pos)
        self.btn_blackjack.update(m_pos)
        self.btn_russian_roulette.update(m_pos)

    def draw(self, screen):
        from Utility.EconManager import EconomyManager
        
        screen.blit(self.background, (0, 0))
        economy.draw_balance(screen)
        self.btn_dating.draw(screen)
        self.btn_blackjack.draw(screen)
        self.btn_russian_roulette.draw(screen)


class SceneManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.scenes = {}
        self.current_scene = None
        self.running = True

    def add_scene(self, name, scene_object):
        self.scenes[name] = scene_object

    def switch_scene(self, name):
        if name in self.scenes:
            self.current_scene = self.scenes[name]
            # If the scene has an 'on_enter' method, call it
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter()
        else:
            print(f"Scene '{name}' not found!")

    def run(self):
            while self.running:
                if self.current_scene is None:
                    continue

                # 1. Handle "Internal Loop" scenes (like the Roulette)
                if hasattr(self.current_scene, 'run_scene'):
                    self.current_scene.run_scene()
                else:
                    # 2. Capture ALL events for this frame
                    events = pygame.event.get()
                    
                    # 3. Check for global events (like quitting)
                    for event in events:
                        if event.type == pygame.QUIT:
                            self.running = False
                    
                    # 4. Pass the FULL LIST of events to the scene's handler
                    # This fixes the 'not iterable' error
                    result = self.current_scene.handle_events(events)
                    
                    # 5. Handle scene switching if the scene returns a name
                    if result:
                        self.switch_scene(result)
                    
                    # 6. Standard update and draw calls
                    self.current_scene.update()
                    self.current_scene.draw(self.screen)
                    
                    pygame.display.flip()
                    self.clock.tick(60)

    def quit(self):
        self.running = False