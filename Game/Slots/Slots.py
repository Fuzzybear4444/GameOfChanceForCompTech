import pygame
import random
import math
import os
import sys
from Utility.EconManager import economy
from Utility.GUI import Button
import Utility.Constants as Constants

class SlotsScene:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # UI Elements
        self.exit_btn = Button(20, 20, 120, 45, (150, 50, 50), (200, 70, 70), "EXIT HUB", 20)
        self.font_score = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Game State
        self.reels = [Reel(200 + i*220, 250, 200, 450) for i in range(3)]
        self.sym_images = self._load_images()
        self.spinning = False
        self.particles = []
        self.checking_win = False

    def _load_images(self):
        imgs = []
        img_folder = os.path.join(self.base_path, "img")
        path = os.path.join(img_folder, f"super_win.png")
        img = pygame.image.load(path).convert_alpha()
        imgs.append(pygame.transform.smoothscale(img, (120, 120)))
        for i in range(6):
            path = os.path.join(img_folder, f"symbole_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                imgs.append(pygame.transform.smoothscale(img, (120, 120)))
            else:
                # Placeholder box if image is missing
                surf = pygame.Surface((120, 120))
                surf.fill((50, 50, 200))
                pygame.draw.rect(surf, (255, 255, 255), [0,0,120,120], 2)
                imgs.append(surf)
        return imgs

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.exit_btn.update(mouse_pos)

        for event in events:
            # Check Exit Button
            if self.exit_btn.handle_event(event):
                return "HUB"

            # Spin Logic
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.spinning and economy.get_balance() >= 10:
                    economy.spend_funds(10)
                    self.spinning = True
                    self.checking_win = True # Set this to true when a spin starts
                    for i, r in enumerate(self.reels):
                        r.speed = random.randint(30, 50) + (i * 10)
                        r.spinning = True
        return None

    def update(self):
        was_spinning = self.spinning
        self.spinning = any(r.spinning for r in self.reels)
        
        for r in self.reels:
            r.update()

        # IF THE REELS JUST STOPPED, CHECK THE WIN
        if was_spinning and not self.spinning and self.checking_win:
            self.check_for_payout()
            self.checking_win = False

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0: self.particles.remove(p)

    def check_for_payout(self):
        # Get the symbol index at the center for each reel
        results = []
        for r in self.reels:
            # We calculate which index is at the 'top' based on the offset
            # 150 is your spacing
            center_idx = int((abs(r.offset) // 150) % len(r.symbols))
            # Grab the actual symbol ID (0-6) from that position
            results.append(r.symbols[center_idx])

        r1, r2, r3 = results

        if r1 == r2 == r3:
            # 3 OF A KIND - BIG WIN
            payout = 100
            economy.add_funds(payout)
            self.spawn_win_effect(amount=100)
            print(f"JACKPOT! Won {payout}")

        elif r1 == r2 or r2 == r3 or r1 == r3:
            # 2 OF A KIND - SMALL WIN
            payout = 20
            economy.add_funds(payout)
            self.spawn_win_effect(amount=20)
            print(f"Small Win! Won {payout}")
    
    def draw(self, screen):
        screen.fill((15, 15, 35)) # Slots Background
        
        # Draw Reels with Clipping
        clip_rect = pygame.Rect(0, 250, Constants.Screen_Size[0], 450)
        screen.set_clip(clip_rect)
        for r in self.reels:
            r.draw(screen, self.sym_images)
        screen.set_clip(None)

        # Draw UI
        self.exit_btn.draw(screen)
        
        bal_text = self.font_score.render(f"Credits: {economy.get_balance()}", True, (255, 255, 255))
        screen.blit(bal_text, (Constants.Screen_Size[0]//2 - bal_text.get_width()//2, 850))
        
        hint_text = self.font_score.render("SPACE TO SPIN (10)", True, (200, 200, 200))
        screen.blit(hint_text, (Constants.Screen_Size[0]//2 - hint_text.get_width()//2, 100))
        for p in self.particles:
            p.draw(screen)
            
    def spawn_win_effect(self, amount):
        count = 100 if amount > 50 else 30
        colors = [(255, 215, 0), (255, 255, 255), (200, 0, 0)]
        for _ in range(count):
            self.particles.append(Particle(500, 500, random.choice(colors)))

class Reel:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.offset = 0
        self.speed = 0
        self.spinning = False
        # Spacing should match your symbol size + some padding
        self.spacing = 150 
        self.symbols = [random.randint(0, 6) for _ in range(20)]

    def update(self):
        if self.spinning:
            self.offset += self.speed
            self.speed *= 0.97
            if self.speed < 0.5:
                self.spinning = False
                self.speed = 0
                # Snap to nearest symbol so it looks centered
                self.offset = round(self.offset / self.spacing) * self.spacing

    def draw(self, surface, sym_images):
        total_reel_height = len(self.symbols) * self.spacing
        
        for i, s_idx in enumerate(self.symbols):
            # Calculate base position
            y_pos = self.rect.y + (i * self.spacing) + (self.offset % total_reel_height)
            
            # Wrap symbols that go off the bottom back to the top
            if y_pos > self.rect.y + self.rect.h:
                y_pos -= total_reel_height
            
            # Draw if the symbol is even partially inside the view area
            if y_pos > self.rect.y - self.spacing and y_pos < self.rect.y + self.rect.h:
                surface.blit(sym_images[s_idx], (self.rect.x + 40, y_pos))

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 10)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.lifetime = 120

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15 # Gravity
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            # Create a small surface for the glow effect
            alpha = max(0, min(255, self.lifetime * 2))
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (4, 4), 4)
            surface.blit(s, (self.x - 4, self.y - 4))