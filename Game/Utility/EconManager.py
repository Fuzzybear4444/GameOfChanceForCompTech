import pygame
from Utility import Constants
from Utility.Fonts import font_med, font_small, font_large
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
    
    def draw_balance(self, screen):
        balance_text = f"Balance: ${self.balance}"
        balance_surf = font_med.render(balance_text, True, (255, 255, 255))
        screen.blit(balance_surf, (Constants.ScreenSize[0] - balance_surf.get_width() - 20, 20))

economy = EconomyManager(100)