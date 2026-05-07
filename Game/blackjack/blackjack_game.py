import pygame
import sys
import os

# Absolute imports based on your root folder structure
from Utility.Fonts import font_small, font_med
from Utility.Constants import *
from blackjack.blackjack_deck import Deck, Hand
from SceneManager import Scene
from Utility.EconManager import economy, GamblingBox

class BlackjackScene(Scene):
    def __init__(self, screen):
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.screen = screen
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize the persistent Betting Box
        self.bet_box = GamblingBox(30, 30, 150, 50, font_small)
        self.current_bet = 0
        
        try:
            back_path = os.path.join(self.current_dir, 'img', 'back.png')
            self.card_back = pygame.image.load(back_path).convert()
        except FileNotFoundError:
            self.card_back = pygame.Surface((70, 100))
            self.card_back.fill((100, 0, 0))

        self.reset_game()

    def reset_game(self):
        """Resets the deck, hands, and game state variables"""
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer = Hand()
        self.player = Hand()
        self.game_over = False
        self.message = "Type Bet and Press Enter"
        self.message_color = black 
        self.dealer_images = []
        self.player_images = []
        self.current_bet = 0

    def load_card_image(self, card_str):
        """Helper to load card images from the local img folder"""
        try:
            card_path = os.path.join(self.current_dir, 'img', f'{card_str}.png')
            return pygame.image.load(card_path).convert()
        except FileNotFoundError:
            surf = pygame.Surface((70, 100))
            surf.fill((255, 255, 255))
            text = self.font.render(card_str, True, (0,0,0))
            surf.blit(text, (10, 10))
            return surf

    def deal(self):
        """Starts a new round if a bet has been placed"""
        if self.game_over:
            self.reset_game()
            
        if len(self.player.cards) > 0:
            return 

        for _ in range(2):
            self.dealer.add_card(self.deck.deal())
            self.player.add_card(self.deck.deal())
            
        # RESTORED: Must call display_cards to populate Hand.card_img[cite: 14]
        self.dealer.display_cards()
        self.player.display_cards()
        
        self.dealer_images = [self.load_card_image(c) for c in self.dealer.card_img]
        self.player_images = [self.load_card_image(c) for c in self.player.card_img]

        self.message = ""
        self.check_blackjack()

    def handle_events(self, events):
        """Processes user input with strict betting requirements"""
        for event in events:
            bet_submitted = self.bet_box.handle_event(event)
            if bet_submitted is not None:
                if economy.place_bet(bet_submitted):
                    self.current_bet = bet_submitted
                    self.message = f"Bet: ${self.current_bet}. Click Deal."
                else:
                    self.message = "Insufficient Funds!"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "HUB"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                
                if 30 <= mouse[0] <= 180:
                    # DEAL BUTTON
                    if 100 <= mouse[1] <= 150:
                        if self.current_bet > 0 or self.game_over:
                            self.deal()
                        else:
                            self.message = "You must bet first!"
                    
                    # HIT BUTTON
                    elif 170 <= mouse[1] <= 220:
                        if self.current_bet > 0 and not self.game_over:
                            self.hit()
                        elif not self.game_over:
                            self.message = "Bet and Deal first!"
                    
                    # STAND BUTTON
                    elif 240 <= mouse[1] <= 290:
                        if self.current_bet > 0 and not self.game_over:
                            self.stand()
                        elif not self.game_over:
                            self.message = "Bet and Deal first!"
                            
                    elif 310 <= mouse[1] <= 360:
                        self.reset_game()
                        return "HUB"
        return None

    def draw(self, screen):
        """Renders visual elements to the screen"""
        screen.fill(background_color)
        pygame.draw.rect(screen, grey, pygame.Rect(0, 0, 250, 700))
        economy.draw_balance(screen)
        self.bet_box.draw(screen)
        
        self.draw_button(screen, "Deal", 30, 100, 150, 50, light_slat, dark_slat)
        self.draw_button(screen, "Hit", 30, 170, 150, 50, light_slat, dark_slat)
        self.draw_button(screen, "Stand", 30, 240, 150, 50, light_slat, dark_slat)
        self.draw_button(screen, "EXIT", 30, 310, 150, 50, light_slat, dark_slat)

        # Card Display logic
        if len(self.player.cards) > 0:
            # Dealer Cards
            for i, img in enumerate(self.dealer_images):
                x_offset = 400 + (i * 110)
                # Hide second card unless game is over
                if i == 1 and not self.game_over:
                    screen.blit(self.card_back, (x_offset, 200))
                else:
                    screen.blit(img, (x_offset, 200))

            # Player Cards
            for i, img in enumerate(self.player_images):
                x_offset = 300 + (i * 110)
                screen.blit(img, (x_offset, 450))

        if self.message:
            msg_surf = self.title_font.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(center=(550, 350))
            bg_rect = msg_rect.inflate(20, 20)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)
            screen.blit(msg_surf, msg_rect)

    def draw_button(self, screen, msg, x, y, w, h, ic, ac):
        mouse = pygame.mouse.get_pos()
        color = ac if x + w > mouse[0] > x and y + h > mouse[1] > y else ic
        pygame.draw.rect(screen, color, (x, y, w, h))
        text_surf = self.font.render(msg, True, black)
        text_rect = text_surf.get_rect(center=(x + w/2, y + h/2))
        screen.blit(text_surf, text_rect)

    def check_blackjack(self):
        """Checks for initial 21 and pays out"""
        self.dealer.calc_hand()
        self.player.calc_hand()
        if self.player.value == 21:
            economy.add_funds(int(2.5 * self.current_bet)) 
            self.end_game("Blackjack!", green)

    def hit(self):
        """Adds a card and updates player visuals"""
        if self.game_over or not self.player.cards:
            return
        self.player.add_card(self.deck.deal())
        
        # RESTORED: Update the list of card strings[cite: 14]
        self.player.display_cards()
        self.player_images = [self.load_card_image(c) for c in self.player.card_img]
        
        self.player.calc_hand()
        if self.player.value > 21:
            self.end_game("Busted!", red)

    def stand(self):
        """Ends player turn, runs Dealer AI, and calculates results"""
        if self.game_over or not self.player.cards:
            return
        
        self.dealer.calc_hand()
        self.player.calc_hand()
        
        # Dealer AI: hit until 17
        while self.dealer.value < 17:
            self.dealer.add_card(self.deck.deal())
            self.dealer.calc_hand()
            
        # RESTORED: Update dealer image strings for final reveal[cite: 14]
        self.dealer.display_cards()
        self.dealer_images = [self.load_card_image(c) for c in self.dealer.card_img]

        # Victory/Loss/Push logic
        if self.dealer.value > 21 or self.player.value > self.dealer.value:
            economy.add_funds(2 * self.current_bet)
            self.end_game("You Won!", green)
        elif self.player.value == self.dealer.value:
            economy.add_funds(self.current_bet)
            self.end_game("Push!", grey)
        else:
            self.end_game("Dealer Wins!", red)

    def end_game(self, msg, color):
        self.message = msg
        self.message_color = color
        self.game_over = True
        
    def update(self):
        pass