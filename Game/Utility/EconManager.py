import pygame
from Utility import Constants
from Utility.Fonts import font_med, font_small, font_large

class GamblingBox:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = ''
        self.font = font
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.text.isdigit():
                    val = int(self.text)
                    self.text = ''
                    return val
                self.text = ''
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
class EconomyManager:
    def __init__(self, starting_balance):
        self.balance = starting_balance
       

    def add_funds(self, amount):
        self.balance += amount

    def spend_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Purchase successful! Remaining balance: {self.balance}")
            
            return True  # Purchase successful
        print("Not enough funds to complete the purchase.")
        
        return False     # Not enough money
    def get_balance(self):
        return self.balance
    
    def place_bet(self, amount):
        """Returns True if bet is valid and subtracted, else False."""
        if amount is not None and 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False
    
    def draw_balance(self, screen):
        balance_text = f"Balance: ${self.balance}"
        balance_surf = font_med.render(balance_text, True, (255, 255, 255))
        screen.blit(balance_surf, (Constants.Screen_Size[0] - balance_surf.get_width() - 20, 20))

economy = EconomyManager(100)