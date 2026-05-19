import pygame
import random
import math

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
FPS = 60
WHITE, BLACK, RED, GREEN, GRAY = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 150, 0), (100, 100, 100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("Arial Bold", 20)
pygame.display.set_caption("Roulette")
clock = pygame.time.Clock()

try:
    wheel_img = pygame.image.load("Screenshot 2026-05-01 080828.png").convert_alpha()
    wheel_img = pygame.transform.smoothscale(wheel_img, (400, 400))

    board_img = pygame.image.load("Screenshot 2026-05-01 081141.png").convert_alpha()
    board_img = pygame.transform.smoothscale(board_img, (800, 300))

    red_chip_img = pygame.image.load("Screenshot 2026-05-01 083414.png").convert_alpha()
    red_chip_img = pygame.transform.smoothscale(red_chip_img, (40, 40))

    black_chip_img = pygame.image.load("Screenshot 2026-05-01 083436.png").convert_alpha()
    black_chip_img = pygame.transform.smoothscale(black_chip_img, (40, 40))
except:
    wheel_img = pygame.Surface((400, 400))
    board_img = pygame.Surface((800, 300))
    red_chip_img = pygame.Surface((40, 40))
    black_chip_img = pygame.Surface((40, 40))

WHEEL_ORDER = ["0", "28", "9", "26", "30", "11", "7", "20", "32", "17", "5", "22", "34", "15", "3", "24", "36", "13",
               "1", "00", "27", "10", "25", "29", "12", "8", "19", "31", "18", "6", "21", "33", "16", "4", "23", "35",
               "14", "2"]
RED_NUMS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]

btn_red = pygame.Rect(100, 590, 140, 40)
btn_black = pygame.Rect(260, 590, 140, 40)
btn_odd = pygame.Rect(420, 590, 140, 40)
btn_even = pygame.Rect(580, 590, 140, 40)

btn_minus_10 = pygame.Rect(50, 150, 40, 40)
btn_minus_100 = pygame.Rect(100, 150, 45, 40)
btn_minus_1000 = pygame.Rect(155, 150, 55, 40)
btn_plus_10 = pygame.Rect(350, 150, 40, 40)
btn_plus_100 = pygame.Rect(400, 150, 45, 40)
btn_plus_1000 = pygame.Rect(455, 150, 55, 40)

BOARD_X, BOARD_Y = 100, 650
board_rects = {}
board_rects["0"] = pygame.Rect(BOARD_X, BOARD_Y, 80, 150)
board_rects["00"] = pygame.Rect(BOARD_X, BOARD_Y + 150, 80, 150)
for i in range(1, 37):
    col = (i - 1) // 3
    row = 2 - ((i - 1) % 3)
    board_rects[str(i)] = pygame.Rect(BOARD_X + 80 + (col * 60), BOARD_Y + (row * 100), 60, 100)


class RouletteGame:
    def __init__(self):
        self.bankroll = 10000
        self.current_bet = 100
        self.last_bet_type = None
        self.status_message = "Welcome! Spin to win."
        self.angle = 0
        self.spinning = False
        self.target_result = "0"
        self.pockets = WHEEL_ORDER

    def spin(self, bet_type):
        if self.bankroll < self.current_bet or self.spinning:
            return

        self.last_bet_type = bet_type
        self.target_result = random.choice(self.pockets)
        self.spinning = True

        target_idx = self.pockets.index(self.target_result)
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
        won = False
        multiplier = 1
        result = self.target_result


        if self.last_bet_type == result:
            won = True
            multiplier = 35
        elif result not in ["0", "00"]:
            res_int = int(result)
            if self.last_bet_type == "RED" and res_int in RED_NUMS:
                won = True
            elif self.last_bet_type == "BLACK" and res_int not in RED_NUMS:
                won = True
            elif self.last_bet_type == "ODD" and res_int % 2 != 0:
                won = True
            elif self.last_bet_type == "EVEN" and res_int % 2 == 0:
                won = True

        if won:
            winnings = self.current_bet * multiplier
            self.bankroll += winnings
            self.status_message = f"Winner! Landed on {result}. Gained ${winnings}!"
        else:
            self.bankroll -= self.current_bet
            self.status_message = f"HAHA LOSER! Landed on {result}. Lost ${self.current_bet}."


def draw_ui(game):
    screen.fill(GREEN)
    screen.blit(board_img, (BOARD_X, BOARD_Y))


    rotated_wheel = pygame.transform.rotate(wheel_img, game.angle)
    wheel_rect = rotated_wheel.get_rect(center=(700, 300))
    screen.blit(rotated_wheel, wheel_rect)


    pygame.draw.polygon(screen, WHITE, [(700, 110), (680, 80), (720, 80)])


    screen.blit(font.render(f"BANKROLL: ${game.bankroll}", True, WHITE), (20, 20))
    screen.blit(font.render(f"BET: ${game.current_bet}", True, WHITE), (230, 155))
    screen.blit(font.render(game.status_message, True, WHITE), (20, 80))

    def draw_button(rect, text, color=GRAY):
        pygame.draw.rect(screen, color, rect)
        label = font.render(text, True, WHITE)
        screen.blit(label, (rect.x + 5, rect.y + 10))


    draw_button(btn_minus_1000, "-1k")
    draw_button(btn_minus_100, "-100")
    draw_button(btn_minus_10, "-10")
    draw_button(btn_plus_10, "+10")
    draw_button(btn_plus_100, "+100")
    draw_button(btn_plus_1000, "+1k")


    draw_button(btn_red, "RED", RED)
    draw_button(btn_black, "BLACK", BLACK)
    draw_button(btn_odd, "ODD")
    draw_button(btn_even, "EVEN")


    if game.last_bet_type:
        pos = None
        if game.last_bet_type in board_rects:
            pos = board_rects[game.last_bet_type].center
        elif game.last_bet_type == "RED":
            pos = btn_red.center
        elif game.last_bet_type == "BLACK":
            pos = btn_black.center
        elif game.last_bet_type == "ODD":
            pos = btn_odd.center
        elif game.last_bet_type == "EVEN":
            pos = btn_even.center

        if pos:
            chip = black_chip_img if game.last_bet_type == "RED" else red_chip_img
            screen.blit(chip, chip.get_rect(center=pos))
            txt = font.render(str(game.current_bet), True, WHITE)
            screen.blit(txt, txt.get_rect(center=pos))


def main():
    game = RouletteGame()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if btn_minus_10.collidepoint(pos):
                    game.current_bet = max(0, game.current_bet - 10)
                elif btn_minus_100.collidepoint(pos):
                    game.current_bet = max(0, game.current_bet - 100)
                elif btn_minus_1000.collidepoint(pos):
                    game.current_bet = max(0, game.current_bet - 1000)
                elif btn_plus_10.collidepoint(pos):
                    game.current_bet += 10
                elif btn_plus_100.collidepoint(pos):
                    game.current_bet += 100
                elif btn_plus_1000.collidepoint(pos):
                    game.current_bet += 1000


                for num, rect in board_rects.items():
                    if rect.collidepoint(pos): game.spin(num)


                if btn_red.collidepoint(pos): game.spin("RED")
                if btn_black.collidepoint(pos): game.spin("BLACK")
                if btn_odd.collidepoint(pos): game.spin("ODD")
                if btn_even.collidepoint(pos): game.spin("EVEN")

        game.update()
        draw_ui(game)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()