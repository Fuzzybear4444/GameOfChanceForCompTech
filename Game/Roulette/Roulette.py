import pygame
import random
import math
import os
from Utility.EconManager import economy
from SceneManager import Scene

# --- CONSTANTS ---
WHITE, BLACK, RED, GREEN, GRAY = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 150, 0), (100, 100, 100)
WHEEL_ORDER = ["0", "28", "9", "26", "30", "11", "7", "20", "32", "17", "5", "22", "34", "15", "3", "24", "36", "13",
               "1", "00", "27", "10", "25", "29", "12", "8", "19", "31", "18", "6", "21", "33", "16", "4", "23", "35",
               "14", "2"]
RED_NUMS = [1, 3, 5, 7, 9, 12, 13, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BOARD_X, BOARD_Y = 100, 650

class RouletteScene(Scene):
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.SysFont("Arial Bold", 20)
        
        # Game State
        self.current_bet = 0
        self.angle = 0
        self.target_angle = 0
        self.spinning = False
        self.target_result = None
        self.last_bet_type = None
        self.status_message = "Place your bet and select a space!"
        
        self._load_assets()
        self._setup_rects()

    def _load_assets(self):
        try:
            self.wheel_img = pygame.transform.smoothscale(pygame.image.load("Roulette/Screenshot 2026-05-01 080828.png").convert_alpha(), (400, 400))
            self.board_img = pygame.transform.smoothscale(pygame.image.load("Roulette/Screenshot 2026-05-01 081141.png").convert_alpha(), (800, 300))
            self.red_chip_img = pygame.transform.smoothscale(pygame.image.load("Roulette/Screenshot 2026-05-01 083414.png").convert_alpha(), (40, 40))
            self.black_chip_img = pygame.transform.smoothscale(pygame.image.load("Roulette/Screenshot 2026-05-01 083436.png").convert_alpha(), (40, 40))
        except Exception as e:
            print(f"Error loading images: {e}")
            self.wheel_img, self.board_img = pygame.Surface((400, 400)), pygame.Surface((800, 300))
            self.red_chip_img, self.black_chip_img = pygame.Surface((40, 40)), pygame.Surface((40, 40))

    def _setup_rects(self):
        self.btn_red = pygame.Rect(100, 590, 140, 40)
        self.btn_black = pygame.Rect(260, 590, 140, 40)
        self.btn_odd = pygame.Rect(420, 590, 140, 40)
        self.btn_even = pygame.Rect(580, 590, 140, 40)
        
        self.btn_minus_10 = pygame.Rect(50, 150, 40, 40)
        self.btn_minus_100 = pygame.Rect(100, 150, 45, 40)
        self.btn_minus_1000 = pygame.Rect(155, 150, 55, 40)
        self.btn_plus_10 = pygame.Rect(350, 150, 40, 40)
        self.btn_plus_100 = pygame.Rect(400, 150, 45, 40)
        self.btn_plus_1000 = pygame.Rect(455, 150, 55, 40)
        
        self.btn_exit = pygame.Rect(800, 20, 150, 50) # Exit Button

        self.board_rects = {}
        self.board_rects["0"] = pygame.Rect(BOARD_X, BOARD_Y, 80, 150)
        self.board_rects["00"] = pygame.Rect(BOARD_X, BOARD_Y + 150, 80, 150)
        for i in range(1, 37):
            col, row = (i - 1) // 3, 2 - ((i - 1) % 3)
            self.board_rects[str(i)] = pygame.Rect(BOARD_X + 80 + (col * 60), BOARD_Y + (row * 100), 60, 100)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "HUB"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                
                # Check Exit
                if self.btn_exit.collidepoint(pos):
                    return "HUB"

                # If spinning, block other inputs
                if self.spinning: continue

                # Bet adjustments
                if self.btn_minus_10.collidepoint(pos): self.current_bet = max(0, self.current_bet - 10)
                elif self.btn_minus_100.collidepoint(pos): self.current_bet = max(0, self.current_bet - 100)
                elif self.btn_minus_1000.collidepoint(pos): self.current_bet = max(0, self.current_bet - 1000)
                elif self.btn_plus_10.collidepoint(pos): self.current_bet += 10
                elif self.btn_plus_100.collidepoint(pos): self.current_bet += 100
                elif self.btn_plus_1000.collidepoint(pos): self.current_bet += 1000

                # Check board clicks to SPIN
                for num, rect in self.board_rects.items():
                    if rect.collidepoint(pos): self.spin(num)

                if self.btn_red.collidepoint(pos): self.spin("RED")
                if self.btn_black.collidepoint(pos): self.spin("BLACK")
                if self.btn_odd.collidepoint(pos): self.spin("ODD")
                if self.btn_even.collidepoint(pos): self.spin("EVEN")
                
        return None

    def spin(self, bet_type):
        if economy.get_balance() < self.current_bet or self.current_bet == 0 or self.spinning:
            self.status_message = "Invalid Bet or Insufficient Funds!"
            return

        # Deduct money immediately upon spinning
        economy.balance -= self.current_bet
        
        self.last_bet_type = bet_type
        self.target_result = random.choice(WHEEL_ORDER)
        self.spinning = True

        target_idx = WHEEL_ORDER.index(self.target_result)
        self.target_angle = (target_idx * (360 / 38)) + (360 * 5)

    def update(self):
        if self.spinning:
            if self.angle < self.target_angle:
                self.angle += (self.target_angle - self.angle) * 0.05 + 1
            else:
                self.angle = self.target_angle  # Snap to final
                self.spinning = False
                self.resolve_bet()

    def resolve_bet(self):
        won, multiplier = False, 1
        result = self.target_result

        if self.last_bet_type == result:
            won, multiplier = True, 36
        elif result not in ["0", "00"]:
            res_int = int(result)
            if self.last_bet_type == "RED" and res_int in RED_NUMS: won, multiplier = True, 2
            elif self.last_bet_type == "BLACK" and res_int not in RED_NUMS: won, multiplier = True, 2
            elif self.last_bet_type == "ODD" and res_int % 2 != 0: won, multiplier = True, 2
            elif self.last_bet_type == "EVEN" and res_int % 2 == 0: won, multiplier = True, 2

        if won:
            winnings = self.current_bet * multiplier
            economy.balance += winnings
            self.status_message = f"Winner! Landed on {result}. Gained ${winnings}!"
        else:
            self.status_message = f"Landed on {result}. Lost ${self.current_bet}."
            
        # Reset angle for next spin
        self.angle = self.angle % 360
        self.target_angle = self.angle

    def draw_button(self, rect, text, color=GRAY):
        pygame.draw.rect(self.screen, color, rect)
        label = self.font.render(text, True, WHITE)
        self.screen.blit(label, (rect.x + 5, rect.y + 10))

    def draw(self, screen):
        screen.fill(GREEN)
        screen.blit(self.board_img, (BOARD_X, BOARD_Y))

        # Rotate and draw wheel
        rotated_wheel = pygame.transform.rotate(self.wheel_img, self.angle)
        wheel_rect = rotated_wheel.get_rect(center=(700, 300))
        screen.blit(rotated_wheel, wheel_rect)

        # Draw wheel pointer
        pygame.draw.polygon(screen, WHITE, [(700, 110), (680, 80), (720, 80)])

        # Draw UI text
        screen.blit(self.font.render(f"BANKROLL: ${economy.get_balance()}", True, WHITE), (20, 20))
        screen.blit(self.font.render(f"BET: ${self.current_bet}", True, WHITE), (230, 155))
        screen.blit(self.font.render(self.status_message, True, WHITE), (20, 80))

        # Draw Bet controls
        self.draw_button(self.btn_minus_1000, "-1k")
        self.draw_button(self.btn_minus_100, "-100")
        self.draw_button(self.btn_minus_10, "-10")
        self.draw_button(self.btn_plus_10, "+10")
        self.draw_button(self.btn_plus_100, "+100")
        self.draw_button(self.btn_plus_1000, "+1k")

        # Draw special board buttons
        self.draw_button(self.btn_red, "RED", RED)
        self.draw_button(self.btn_black, "BLACK", BLACK)
        self.draw_button(self.btn_odd, "ODD")
        self.draw_button(self.btn_even, "EVEN")
        
        # Draw Exit Button
        self.draw_button(self.btn_exit, "  EXIT HUB", RED)

        # Draw the chip on the last bet location
        if self.last_bet_type:
            pos = None
            if self.last_bet_type in self.board_rects: pos = self.board_rects[self.last_bet_type].center
            elif self.last_bet_type == "RED": pos = self.btn_red.center
            elif self.last_bet_type == "BLACK": pos = self.btn_black.center
            elif self.last_bet_type == "ODD": pos = self.btn_odd.center
            elif self.last_bet_type == "EVEN": pos = self.btn_even.center

            if pos:
                chip = self.black_chip_img if self.last_bet_type == "RED" else self.red_chip_img
                screen.blit(chip, chip.get_rect(center=pos))
                txt = self.font.render(str(self.current_bet), True, WHITE)
                screen.blit(txt, txt.get_rect(center=pos))