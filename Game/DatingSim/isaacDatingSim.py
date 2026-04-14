# DatingSim/isaacDatingSim.py
import pygame
import textwrap
import math
import random
import os
from Utility.EconManager import EconomyManager
from Utility.Fonts import font_med, font_small, font_large
from Utility.Colors import *
import Utility.Constants as Constants
from Utility.EconManager import economy

class DatingSimScene:
    def __init__(self, player_name="Player"):
        # 1. Setup Game State
        self.player_name = player_name
        self.story = self.build_story(self.player_name)
        self.state = "start"
        self.in_ending = False
        self.ending_text = ""
        self.fade_alpha = 255
        self.IsMarried = False
        self.isMarriedNumOfTimes = 0
        # 2. Text Reveal Logic
        self.reveal_index = 0
        self.reveal_timer = 0
        self.REVEAL_DELAY = 22
        self.current_text = ""
        self.full_text = self.story["start"]["text"]
        
        # 3. Animation State
        self.anim_time = 0.0
        self.shake_timer = 0.0
        self.spin_angle = 0.0
        self.spin_timer = 0.0
        self.pop_scale = 1.0
        self.pop_timer = 0.0
        self.shake_xy = (0, 0)
        self.ending_delay = 0.0

        # 4. Image Loading
        self.isaac_image = self.load_asset("isaac.png", (340, 500))
        self.bg_image = self.load_asset("background.png", Constants.ScreenSize)

        self.buttons = [] 
        
        # Animation Trigger Map
        self.ANIM_MAP = {
            "a_pretty": "pop",
            "end_explode_kiss": "spin",
            "end_milk_explode": "spin",
            "end_backflip": "spin",
            "b_yell": "shake",
            "b_meanie": "shake",
            "end_married": "pop",
            "end_jail": "shake",
        }

    def load_asset(self, filename, size):
        path = os.path.join(os.getcwd(), filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except:
            return None

    def build_story(self, name):
        return {
            "start": {
                "text": "You walk up to the big man. He smiles and says... Hello.",
                "choices": [
                    ("Hey big guy, what's your name?", "a_greet"),
                    ("Shut up nerd! What's your name?", "b_greet"),
                    ("Leave without saying a word", "end_leave"),
                ]
            },
            "a_greet": {
                "text": "Isaac says: Well small guy, my name is Isaac — what's yours?",
                "choices": [
                    (f"That's a pretty name, Isaac. My name is {name}.", "a_pretty"),
                    ("Who names their kid Isaac? Weird name — get away from me!", "a_rude"),
                ]
            },
            "a_pretty": {
                "text": f"Isaac blushes red as a tomato and stammers: Di- did you ju- just call me PRETTY?! Yo- your name is pretty too, {name}!!",
                "choices": [
                    ("Go in for a kiss 💋", "end_explode_kiss"),
                    ("Thank you! Want to get a drink with me? (milk 🥛)", "a_milk_ask"),
                ]
            },
            "a_milk_ask": {
                "text": "Isaac, still tomato-red, says: Yes I do!!",
                "choices": [
                    ("Great!! Let's go!", "a_bar"),
                    ("*you pull out a bazooka* 🪖", "end_jail"),
                ]
            },
            "a_bar": {
                "text": "You both walk up to the bar and order a tall glass of milk.",
                "choices": [
                    ("Drink your milk 🥛", "end_milk_explode"),
                    ("Get down on one knee and propose 💍", "end_married"),
                ]
            },
            "a_rude": {
                "text": "You push Isaac away and sprint out the door. He watches you go, confused.",
                "choices": [],
                "ending": "💨 Ending: Not Interested"
            },
            "b_greet": {
                "text": "Isaac looks confused. He says: Nerd?! My name's Isaac and I'm NO nerd!",
                "choices": [
                    ("That's EXACTLY what a nerd would say, NERD!!", "b_meanie"),
                    ("Well I like nerds, so I guess you're not my type.", "b_reveal"),
                ]
            },
            "b_meanie": {
                "text": "Isaac's lower lip quivers. His eyes fill with tears. He runs away sobbing into the night.",
                "choices": [],
                "ending": "😢 Ending: Meanie"
            },
            "b_reveal": {
                "text": "Isaac looks down at his shoes and whispers: Ok... I have to reveal something. I'm actually... a nerd.",
                "choices": [
                    ("Well nerd, it's not like I like you or anything... 😳", "b_tsundere"),
                    ("HAHAHA!!!! YOU'RE A STUPID NERD!!!!!!!", "b_yell"),
                ]
            },
            "b_tsundere": {
                "text": "Isaac stares at you with disgust. He says: who TALKS like that?! He naruto-runs away at full speed... and explodes.",
                "choices": [],
                "ending": "🌸 Ending: Good Ending (somehow)"
            },
            "b_yell": {
                "text": "Isaac starts blushing furiously, as if he liked being yelled at. He says: STEP ON ME!!",
                "choices": [
                    ("...What???", "end_backflip"),
                    ("Bet, nerd!! 👟", "end_nsfw"),
                ]
            },
            "end_leave": {
                "text": "You turn around and walk away without a word. Isaac watches you leave, heart quietly breaking.",
                "choices": [],
                "ending": "🚪 Ending: Silent Exit"
            },
            "end_explode_kiss": {
                "text": "You lean in for the kiss... and you explode. Just like that. No explanation.",
                "choices": [],
                "ending": "💥 Ending: Explode"
            },
            "end_milk_explode": {
                "text": "You both raise your glasses. You both drink your milk. You both explode simultaneously.",
                "choices": [],
                "ending": "🥛💥 Ending: Milk Explosion"
            },
            "end_married": {
                "text": f"You get on one knee and ask: Isaac, will you be the love of my life? Isaac replies: YES!! You get married on the spot. Turns out Isaac was secretly rich. {name} gains +1,000,000 💰",
                "choices": [],
                "ending": "💍 Ending: RICH MARRIED ENDING",
                "IsMarried": True
            },
            "end_jail": {
                "text": 'You get arrested on the spot for pulling "it" out in a public establishment.',
                "choices": [],
                "ending": "🚔 Ending: Jail Time"
            },
            "end_backflip": {
                "text": "You do a backflip in confusion... and explode.",
                "choices": [],
                "ending": "🤸💥 Ending: That Backflip Though"
                
            },
            "end_nsfw": {
                "text": "The following events cannot be shown as they violate school district guidelines.",
                "choices": [],
                "ending": "🔞 Ending: [REDACTED BY SCHOOL BOARD]"
            },
        }

    def enter_state(self, new_key):
        if new_key not in self.story: return
        self.state = new_key
        self.fade_alpha = 180
        self.full_text = self.story[self.state]["text"]
        self.current_text = ""
        self.reveal_index = 0
        self.reveal_timer = 0
        self.ending_delay = 0.0
        
        anim = self.ANIM_MAP.get(new_key, "")
        if anim == "shake": self.shake_timer = 0.5
        elif anim == "spin": self.spin_timer = 0.8
        elif anim == "pop": self.pop_timer = 0.4

    def handle_events(self, events):
        node = self.story.get(self.state, {})
        choices = node.get("choices", [])
        text_done = self.reveal_index >= len(self.full_text)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "HUB"
                if event.key == pygame.K_SPACE and not text_done:
                    self.reveal_index = len(self.full_text)
                    self.current_text = self.full_text

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not text_done:
                    self.reveal_index = len(self.full_text)
                    self.current_text = self.full_text
                elif self.in_ending:
                    self.in_ending = False
                    return "HUB"
                elif text_done and choices:
                    for rect, key in self.buttons:
                        if rect.collidepoint(event.pos):
                            self.enter_state(key)
        return None

    def update(self):
        dt = 1/60.0
        self.anim_time += dt
        
        # Text Reveal
        if self.reveal_index < len(self.full_text):
            self.reveal_timer += (dt * 1000)
            if self.reveal_timer >= self.REVEAL_DELAY:
                self.current_text += self.full_text[self.reveal_index]
                self.reveal_index += 1
                self.reveal_timer = 0

        # Shake logic
        if self.shake_timer > 0:
            self.shake_timer -= dt
            amp = max(1, int(10 * (self.shake_timer / 0.5)))
            self.shake_xy = (random.randint(-amp, amp), random.randint(-amp, amp))
        else: self.shake_xy = (0, 0)

        # Spin logic
        if self.spin_timer > 0:
            self.spin_timer -= dt
            self.spin_angle = (1 - self.spin_timer / 0.8) * 360
        else: self.spin_angle = 0
            
        # Pop logic
        if self.pop_timer > 0:
            self.pop_timer -= dt
            t = 1 - (self.pop_timer / 0.4)
            self.pop_scale = 1.0 + 0.35 * math.sin(t * math.pi)
        else: self.pop_scale = 1.0

        # Ending Transition
        node = self.story.get(self.state, {})
        choices = node.get("choices", [])

        if self.reveal_index >= len(self.full_text) and "ending" in node and not choices and not self.in_ending:
            self.ending_delay += dt
            if self.ending_delay >= 2.5:
                self.in_ending = True
                self.ending_text = node["ending"]
                if node.get("IsMarried"):
                    self.IsMarried = True
                    self.isMarriedNumOfTimes += 1
        if self.IsMarried and self.isMarriedNumOfTimes == 1:
            self.isMarriedNumOfTimes += 1
            economy.add_funds(1000000)

    def draw(self, screen):
        if self.in_ending:
            screen.fill((30, 30, 40))
            lines = textwrap.wrap(self.ending_text, width=30)
            for i, line in enumerate(lines):
                end_surf = font_large.render(line, True, (255, 215, 0))
                screen.blit(end_surf, (Constants.ScreenSize[0]//2 - end_surf.get_width()//2, 400 + i*50))
            return

        # Background
        if self.bg_image: screen.blit(self.bg_image, (0,0))
        else: screen.fill((20, 20, 35))
        
        # Portrait (Blush Check)
        blush_words = ["blushes", "tomato", "pretty", "blushing", "love", "marry"]
        highlight = any(w in self.full_text.lower() for w in blush_words)
        bounce = math.sin(self.anim_time * 2.5) * 6
        self.draw_isaac(screen, bounce, highlight)
            
        # Dialogue Box
        box_rect = pygame.Rect(20, 700, Constants.ScreenSize[0] - 40, 160)
        pygame.draw.rect(screen, (15, 10, 35, 210), box_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 180, 255), box_rect, 2, border_radius=12)
        
        # Speaker
        speaker = "Isaac" if "isaac" in self.full_text.lower()[:15] or "isaac says" in self.full_text.lower() else "Narrator"
        spk_surf = font_med.render(speaker, True, (255, 150, 180))
        screen.blit(spk_surf, (box_rect.x + 20, box_rect.y + 10))

        wrapped = textwrap.wrap(self.current_text, width=72)
        for i, line in enumerate(wrapped[:4]):
            line_surf = font_small.render(line, True, (255, 255, 255))
            screen.blit(line_surf, (box_rect.x + 20, box_rect.y + 45 + i * 26))

        # Buttons
        if self.reveal_index >= len(self.full_text):
            choices = self.story[self.state].get("choices", [])
            self.draw_buttons(screen, choices)

        # Fade Overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface(Constants.ScreenSize)
            fade_surf.set_alpha(self.fade_alpha)
            fade_surf.fill((0,0,0))
            screen.blit(fade_surf, (0,0))
            self.fade_alpha = max(0, self.fade_alpha - 8)

    def draw_isaac(self, screen, bounce, highlight):
        x = 330 + self.shake_xy[0]
        y = 180 + int(bounce) + self.shake_xy[1]
        
        if self.isaac_image:
            img = self.isaac_image
            if self.spin_angle != 0: img = pygame.transform.rotate(img, self.spin_angle)
            if self.pop_scale != 1.0:
                new_size = (int(340 * self.pop_scale), int(500 * self.pop_scale))
                img = pygame.transform.smoothscale(img, new_size)
            
            rect = img.get_rect(center=(330 + 170 + self.shake_xy[0], 180 + 250 + bounce + self.shake_xy[1]))
            screen.blit(img, rect)
        else:
            color = (180, 100, 120) if highlight else (140, 80, 100)
            pygame.draw.rect(screen, color, (x, y, 340, 500), border_radius=20)

    def draw_buttons(self, screen, choices):
        self.buttons = []
        m_pos = pygame.mouse.get_pos()
        btn_h = 48
        btn_gap = 10
        total_h = len(choices) * (btn_h + btn_gap) - btn_gap
        start_y = 690 - total_h
        
        for i, (label, key) in enumerate(choices):
            rect = pygame.Rect(60, start_y + i * (btn_h + btn_gap), Constants.ScreenSize[0] - 120, btn_h)
            color = (100, 100, 160) if rect.collidepoint(m_pos) else (60, 60, 100)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (180, 180, 255), rect, 2, border_radius=10)
            
            letter = chr(65 + i)
            txt = font_small.render(f"[{letter}] {label}", True, (255, 255, 255))
            screen.blit(txt, (rect.x + 20, rect.y + (btn_h - txt.get_height()) // 2))
            self.buttons.append((rect, key))
            
    def getMarriedNum(self):
        return self.isMarriedNumOfTimes

    def reset_game(self):
        """Resets the dating sim to its original state."""
        self.state = "start"
        self.in_ending = False
        self.ending_text = ""
        self.fade_alpha = 255
        self.reveal_index = 0
        self.reveal_timer = 0
        self.current_text = ""
        self.full_text = self.story["start"]["text"]
        self.ending_delay = 0.0