import pygame
import random
import math

def remove_white_bg(img):
    img = img.copy()
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            r, g, b, a = img.get_at((x, y))
            if r > 240 and g > 240 and b > 240:
                img.set_at((x, y), (10, 10, 15, a))
    return img
#
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 120

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = max(0, min(255, self.lifetime * 2))
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (4, 4), 4)
            surface.blit(s, (int(self.x) - 4, int(self.y) - 4))

class Reel:
    def __init__(self, x):
        self.x = x
        self.symbols = [random.randint(0, 5) for _ in range(5)]
        self.offset = 0
        self.spinning = False
        self.speed = 0
        self.stopping = False
        self.stop_timer = 0

    def spin(self, start_speed, delay):
        self.spinning = True
        self.stopping = False
        self.speed = start_speed
        self.stop_timer = delay

    def update(self):
        if self.spinning:
            self.offset += self.speed
            if self.offset >= 150:
                self.offset = 0
                self.symbols.insert(0, random.randint(0, 5))
                self.symbols.pop()

            if self.stopping:
                self.speed -= 0.4
                if self.speed <= 4:
                    self.speed = 4
                    if self.offset == 0:
                        self.spinning = False
                        self.speed = 0
            else:
                if self.stop_timer > 0:
                    self.stop_timer -= 1
                else:
                    self.speed *= 0.985
                    if self.speed < 15:
                        self.stopping = True

    def draw(self, surface, images):
        for i, sym_idx in enumerate(self.symbols):
            draw_y = 350 + (i - 1) * 150 + self.offset
            surface.blit(images[sym_idx], (self.x, draw_y))

def game():
    pygame.init()
    SCREEN_W, SCREEN_H = 1000, 1000
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Slots Jackpot Edition")
    clock = pygame.time.Clock()

    SYM_SIZE = 150
    COL_SPACING = 200
    REEL_Y = 350
    REEL_HEIGHT = SYM_SIZE * 3
    TOTAL_WIDTH = COL_SPACING * 3
    START_X = (SCREEN_W - TOTAL_WIDTH) // 2 + 25
    SCALE_FACTOR = 2.3
    LEVIER_X, LEVIER_Y = 670, 420

    raw_haut = pygame.image.load("levier_haut.png").convert_alpha()
    raw_haut = remove_white_bg(raw_haut)
    up_lever = pygame.transform.smoothscale(raw_haut, (int(raw_haut.get_width() * SCALE_FACTOR),
                                                          int(raw_haut.get_height() * SCALE_FACTOR)))

    raw_bas = pygame.image.load("levier_bas.png").convert_alpha()
    raw_bas = remove_white_bg(raw_bas)
    down_lever = pygame.transform.smoothscale(raw_bas, (int(raw_bas.get_width() * SCALE_FACTOR),
                                                        int(raw_bas.get_height() * SCALE_FACTOR)))

    sym = [
        pygame.transform.smoothscale(pygame.image.load(f"symbole_{i}.png").convert_alpha(), (SYM_SIZE, SYM_SIZE)) for i
        in range(6)]

    img_super = pygame.image.load('jackpot.png').convert_alpha()
    img_win = pygame.image.load('super_win.png').convert_alpha()
    rect_win_pos = img_super.get_rect(center=(SCREEN_W // 2, 220))

    reels = [Reel(START_X + i * COL_SPACING) for i in range(3)]
    score = 100
    fireworks = []
    win_type = None
    win_timer = 0
    levier_timer = 0
    checking_result = False

    font = pygame.font.SysFont("Arial", 40, bold=True)
    score_font = pygame.font.SysFont("Arial", 60, bold=True)

    running = True
    while running:
        screen.fill((10, 10, 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not any(r.spinning for r in reels) and score >= 10:
                    score -= 10
                    win_type = None
                    win_timer = 0
                    levier_timer = 150
                    fireworks = []
                    checking_result = True
                    for i, r in enumerate(reels):
                        r.spin(40, i * 60)

        if levier_timer > 0:
            levier_timer -= 1
            screen.blit(down_lever, (LEVIER_X, LEVIER_Y))
        else:
            screen.blit(up_lever, (LEVIER_X, LEVIER_Y))

        for r in reels:
            r.update()

        if checking_result and not any(r.spinning for r in reels):
            line = [reels[0].symbols[2], reels[1].symbols[2], reels[2].symbols[2]]
            if line[0] == line[1] == line[2]:
                colors = [(255, 50, 50), (255, 215, 0), (50, 255, 50), (0, 191, 255), (255, 255, 255)]
                if line[0] == 1:
                    win_type = "JACKPOT"
                    score += 500
                    win_timer = 300
                    for _ in range(500):
                        fireworks.append(Particle(SCREEN_W // 2, SCREEN_H // 2, random.choice(colors)))
                else:
                    win_type = "SUPER"
                    score += 150
                    win_timer = 180
            checking_result = False

        status_txt = "PRESS SPACE (Cost: 10)" if score >= 10 else "GAME OVER"
        title = font.render(status_txt, True, (255, 215, 0))
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 100))

        score_display = score_font.render(f"CREDITS: {score}", True, (255, 255, 255))
        screen.blit(score_display, (SCREEN_W // 2 - score_display.get_width() // 2, 850))

        clip_rect = pygame.Rect(0, REEL_Y, SCREEN_W, REEL_HEIGHT)
        screen.set_clip(clip_rect)
        for r in reels:
            r.draw(screen, sym)
        screen.set_clip(None)

        pygame.draw.rect(screen, (255, 0, 0), (START_X - 10, REEL_Y + SYM_SIZE, TOTAL_WIDTH - 20, SYM_SIZE), 5)

        for p in fireworks[:]:
            p.update()
            p.draw(screen)
            if p.lifetime <= 0:
                fireworks.remove(p)

        if win_timer > 0:
            win_timer -= 1
            if win_timer % 20 < 15:
                img = img_super if win_type == "JACKPOT" else img_win
                screen.blit(img, rect_win_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    game()