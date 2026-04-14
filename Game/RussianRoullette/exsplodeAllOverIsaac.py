"""
explosion_roulette.py  —  UPGRADED EDITION
-------------------------------------------
Russian Roulette with BOMBS and MONEY.
Now with:
  • Overhauled neon-noir visual design
  • Configurable bullet count (1–5 bullets in the cylinder)
  • Glowing UI panels, animated gradient title
  • Improved HUD layout with risk meter
  • Smooth spin + shake polish
  • All original gameplay intact

Usage as module:
    from explosion_roulette import run_explosion_roulette
    result = run_explosion_roulette(screen, clock, starting_cash=500)
    # returns dict: {"outcome": "survived"|"exploded"|"cashed_out", "cash": int}

Usage standalone:
    python explosion_roulette.py
"""

import pygame
import random
import math
import sys

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 1000

# ── Neon-Noir Palette ──
BLACK        = (0,    0,    0)
WHITE        = (255,  255,  255)
BG_DARK      = (8,    10,   18)
BG_MID       = (14,   17,   30)
PANEL_BG     = (16,   20,   38)
PANEL_BORDER = (40,   50,   90)
PANEL_GLOW   = (60,   80,   180)

NEON_RED     = (255,  40,   60)
NEON_ORANGE  = (255,  140,  0)
NEON_YELLOW  = (255,  230,  30)
NEON_GREEN   = (30,   255,  120)
NEON_CYAN    = (0,    220,  255)
NEON_PINK    = (255,  50,   180)
NEON_GOLD    = (255,  200,  50)
DIM_GOLD     = (130,  100,  20)

DARK_RED     = (160,  20,   30)
DARK_GREEN   = (10,   80,   40)
DARK_GRAY    = (35,   38,   50)
MID_GRAY     = (80,   85,   110)
LIGHT_GRAY   = (180,  185,  210)
GHOST_WHITE  = (210,  215,  255)

BOMB_BODY    = (18,   20,   28)
FUSE_COL     = (160,  100,  40)
SPARK_COL    = (255,  230,  60)

# ── Layout ──
CYLINDER_RADIUS = 90
CHAMBER_RADIUS  = 18

# ── Gambling ──
STARTING_CASH     = 500
MIN_BET           = 10
MAX_BET           = 999_999_999
BET_STEP          = 10
ROUND_MULTIPLIERS = [1.2, 1.5, 2.0, 2.75, 4.0, 6.0, 10.0]

# ── Timings (60 fps) ──
SPIN_DURATION_FRAMES = 80
RESULT_SHOW_FRAMES   = 220

# ── Bullet config ──
DEFAULT_BULLETS = 1
MIN_BULLETS     = 1
MAX_BULLETS     = 5
NUM_CHAMBERS    = 6

# ─────────────────────────────────────────────
#  QUIPS
# ─────────────────────────────────────────────
SURVIVAL_QUIPS = [
    "isaac farted on the bomb, it died",
    "lucky fat boy",
    "you gooned and made the bomb not blow up",
    "The house is sweating bullets",
    "Fortune favors the stupid",
    "Money = life. You still have both.",
    "JACKPOTTTTTT",
    "Your sigma rizz deflected the explosion",
    "Walk away?? yeah right",
    "The bomb filed a complaint. Denied.",
]

DEATH_MESSAGES = [
    "isaac made you explode",
    "dying does not affect a real gambler",
    "the bomb exploded all over you",
    "The house always wins. TODAY it won HARD.",
    "you saw isaac naked and combusted",
    "Error 404: Money and player not found",
    "ai pictures of Donald Trump killed you",
    "Scientists will study this decision for years",
    "Your financial advisor has left the chat",
    "Next time try: NOT pulling the lever",
]

CASHOUT_LINES = [
    "you cashed out not like a real gambler",
    "you are gonna use this money to do more gambling",
    "i hope you go explode",
    "Greed. But smart greed.",
    "The bomb is disappointed in you",
    "bad boy",
]

# ─────────────────────────────────────────────
#  STATE MACHINE
# ─────────────────────────────────────────────
class GS:
    SETUP    = "SETUP"
    BETTING  = "BETTING"
    IDLE     = "IDLE"
    SPINNING = "SPINNING"
    RESULT   = "RESULT"
    CASHOUT  = "CASHOUT"
    GAMEOVER = "GAMEOVER"


# ─────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def glow_circle(surf, color, pos, radius, glow_radius, alpha=80):
    """Draw a soft glowing halo behind a circle."""
    for r in range(glow_radius, radius, -2):
        a = int(alpha * (1 - (r - radius) / (glow_radius - radius + 1)))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (r, r), r)
        surf.blit(s, (pos[0] - r, pos[1] - r))


def draw_bg(surface, frame):
    """Animated dark scanline background."""
    surface.fill(BG_DARK)
    # subtle horizontal scanlines
    for y in range(0, HEIGHT, 4):
        shade = 5 + int(math.sin(y * 0.05 + frame * 0.01) * 3)
        pygame.draw.line(surface, (shade, shade + 2, shade + 8), (0, y), (WIDTH, y))
    # corner vignette suggestion
    for i in range(6):
        r = pygame.Rect(i * 2, i * 2, WIDTH - i * 4, HEIGHT - i * 4)
        pygame.draw.rect(surface, (0, 0, 0), r, 1)


def draw_panel(surface, rect, title=None, font=None, glow=False):
    """Dark card panel with neon border."""
    pygame.draw.rect(surface, PANEL_BG, rect, border_radius=16)
    border_col = NEON_CYAN if glow else PANEL_BORDER
    pygame.draw.rect(surface, border_col, rect, 2, border_radius=16)
    if glow:
        g = pygame.Surface((rect.w + 12, rect.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(g, (*NEON_CYAN, 30), (0, 0, rect.w + 12, rect.h + 12),
                         border_radius=18)
        surface.blit(g, (rect.x - 6, rect.y - 6))
    if title and font:
        t = font.render(title, True, NEON_CYAN)
        surface.blit(t, t.get_rect(centerx=rect.centerx, y=rect.y + 10))


def draw_neon_text(surface, text, font, color, pos, center=True, glow=True):
    """Render text with an optional soft glow."""
    if glow:
        glow_surf = font.render(text, True, lerp_color(color, BLACK, 0.3))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            r = glow_surf.get_rect()
            if center:
                r.center = pos
            else:
                r.topleft = pos
            surface.blit(glow_surf, r.move(dx, dy))
    lbl = font.render(text, True, color)
    r = lbl.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surface.blit(lbl, r)


def draw_bomb(surface, cx, cy, scale=1.0, fuse_lit=False, frame=0):
    """Sleek neon-outlined cartoon bomb."""
    r = int(44 * scale)
    # shadow
    shadow = pygame.Surface((r * 2 + 20, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 80), (0, 0, r * 2 + 20, 18))
    surface.blit(shadow, (cx - r - 10, cy + r - 4))

    # body glow
    if fuse_lit:
        glow_circle(surface, NEON_ORANGE, (cx, cy), r, r + 28, 50)

    # body
    pygame.draw.circle(surface, BOMB_BODY, (cx, cy), r)
    pygame.draw.circle(surface, DARK_GRAY, (cx, cy), r, 3)
    # highlight
    pygame.draw.circle(surface, (55, 60, 80), (cx - r // 3, cy - r // 3), r // 5)

    # neck
    pygame.draw.rect(surface, MID_GRAY,
                     pygame.Rect(cx - 5, cy - r - 12, 10, 16), border_radius=3)

    # fuse
    fuse_pts = []
    for i in range(26):
        t  = i / 25
        fx = cx + int(math.sin(t * math.pi * 2.6) * 12)
        fy = cy - r - 12 - int(t * 36)
        fuse_pts.append((fx, fy))
    if len(fuse_pts) > 1:
        pygame.draw.lines(surface, FUSE_COL, False, fuse_pts, 3)

    tip = fuse_pts[-1]
    if fuse_lit:
        flicker = random.random()
        spark_col = NEON_YELLOW if flicker > 0.3 else NEON_ORANGE
        for ang in range(0, 360, 40):
            rad = math.radians(ang + frame * 15)
            length = random.randint(5, 12)
            pygame.draw.line(surface, spark_col, tip,
                             (tip[0] + int(math.cos(rad) * length),
                              tip[1] + int(math.sin(rad) * length)), 2)
        pygame.draw.circle(surface, NEON_YELLOW, tip, 5)
    else:
        pygame.draw.circle(surface, MID_GRAY, tip, 4)


def draw_cylinder(surface, cx, cy, loaded_chambers, revealed=False, spin_angle=0.0):
    """
    6-chamber cylinder. loaded_chambers = list of chamber indices that are loaded.
    """
    # outer ring glow
    glow_circle(surface, NEON_CYAN, (cx, cy), CYLINDER_RADIUS + 10, CYLINDER_RADIUS + 30, 40)
    pygame.draw.circle(surface, DARK_GRAY, (cx, cy), CYLINDER_RADIUS + 10)
    pygame.draw.circle(surface, NEON_CYAN, (cx, cy), CYLINDER_RADIUS + 10, 2)

    for i in range(NUM_CHAMBERS):
        angle = spin_angle + (2 * math.pi / NUM_CHAMBERS) * i
        ch_x  = cx + int(math.cos(angle) * CYLINDER_RADIUS)
        ch_y  = cy + int(math.sin(angle) * CYLINDER_RADIUS)
        is_loaded = (i in loaded_chambers)

        if revealed and is_loaded:
            glow_circle(surface, NEON_RED, (ch_x, ch_y), CHAMBER_RADIUS, CHAMBER_RADIUS + 16, 80)
            pygame.draw.circle(surface, NEON_RED,    (ch_x, ch_y), CHAMBER_RADIUS)
            pygame.draw.circle(surface, NEON_YELLOW, (ch_x, ch_y), CHAMBER_RADIUS // 2)
            pygame.draw.circle(surface, WHITE,       (ch_x, ch_y), CHAMBER_RADIUS // 4)
        elif revealed and not is_loaded:
            pygame.draw.circle(surface, DARK_GRAY, (ch_x, ch_y), CHAMBER_RADIUS)
            pygame.draw.circle(surface, NEON_GREEN,(ch_x, ch_y), CHAMBER_RADIUS, 2)
            pygame.draw.circle(surface, BLACK,     (ch_x, ch_y), CHAMBER_RADIUS // 2)
        else:
            pygame.draw.circle(surface, DARK_GRAY, (ch_x, ch_y), CHAMBER_RADIUS)
            pygame.draw.circle(surface, MID_GRAY,  (ch_x, ch_y), CHAMBER_RADIUS, 2)
            pygame.draw.circle(surface, BLACK,     (ch_x, ch_y), CHAMBER_RADIUS // 2)

    # center pin
    pygame.draw.circle(surface, MID_GRAY, (cx, cy), 12)
    pygame.draw.circle(surface, BLACK,    (cx, cy), 6)


def draw_character(surface, cx, cy, state, frame, survived=True):
    """Simple expressive blob character."""
    skin = (255, 210, 170)
    bob  = int(math.sin(frame * 0.14) * 4)

    if state in (GS.BETTING, GS.IDLE, GS.SPINNING, GS.SETUP):
        pygame.draw.ellipse(surface, (40, 80, 200), (cx-22, cy-30+bob, 44, 50))
        pygame.draw.circle(surface, skin,  (cx, cy-44+bob), 20)
        pygame.draw.circle(surface, WHITE, (cx-7, cy-47+bob), 6)
        pygame.draw.circle(surface, WHITE, (cx+7, cy-47+bob), 6)
        pygame.draw.circle(surface, BLACK, (cx-7, cy-47+bob), 3)
        pygame.draw.circle(surface, BLACK, (cx+7, cy-47+bob), 3)
        # money bag
        pygame.draw.circle(surface, NEON_GOLD, (cx-32, cy-12+bob), 12)
        pygame.draw.line(surface, DIM_GOLD,
                         (cx-32, cy-24+bob), (cx-32, cy-12+bob), 4)
        lbl = pygame.font.SysFont("impact", 11).render("$", True, BLACK)
        surface.blit(lbl, (cx-36, cy-19+bob))

    elif state == GS.RESULT and survived:
        jump = int(abs(math.sin(frame * 0.22)) * 24)
        pygame.draw.ellipse(surface, NEON_GREEN, (cx-22, cy-30-jump, 44, 50))
        pygame.draw.circle(surface, skin, (cx, cy-44-jump), 20)
        pygame.draw.arc(surface, BLACK,
                        (cx-13, cy-52-jump, 12, 8), 0, math.pi, 2)
        pygame.draw.arc(surface, BLACK,
                        (cx+1,  cy-52-jump, 12, 8), 0, math.pi, 2)
        pygame.draw.arc(surface, NEON_RED,
                        (cx-10, cy-38-jump, 20, 12), math.pi, 2*math.pi, 3)
        pygame.draw.line(surface, skin, (cx-22, cy-20-jump), (cx-38, cy-42-jump), 4)
        pygame.draw.line(surface, skin, (cx+22, cy-20-jump), (cx+38, cy-42-jump), 4)

    elif state == GS.CASHOUT:
        run_x = int(math.sin(frame * 0.3) * 3)
        pygame.draw.ellipse(surface, NEON_GOLD, (cx-22+run_x, cy-30, 44, 50))
        pygame.draw.circle(surface, skin, (cx+run_x, cy-44), 20)
        pygame.draw.circle(surface, WHITE, (cx-4+run_x, cy-47), 6)
        pygame.draw.circle(surface, WHITE, (cx+8+run_x, cy-47), 6)
        pygame.draw.circle(surface, BLACK, (cx-2+run_x, cy-47), 3)
        pygame.draw.circle(surface, BLACK, (cx+10+run_x, cy-47), 3)
        pygame.draw.circle(surface, NEON_GOLD, (cx-36+run_x, cy-8), 16)
        pygame.draw.line(surface, DIM_GOLD,
                         (cx-36+run_x, cy-24), (cx-36+run_x, cy-8), 4)

    elif state in (GS.RESULT, GS.GAMEOVER) and not survived:
        random.seed(99)
        colors = [(40, 80, 200), skin, NEON_RED, NEON_GREEN, NEON_YELLOW, NEON_ORANGE]
        dist = min(frame * 2.8, 90)
        for i in range(10):
            ang = (i / 10) * 2 * math.pi
            px  = cx + int(math.cos(ang) * dist)
            py  = cy + int(math.sin(ang) * dist) - frame
            pygame.draw.circle(surface, colors[i % len(colors)],
                               (px, max(0, py)), random.randint(4, 12))


def draw_explosion(surface, cx, cy, progress):
    """Expanding layered explosion rings. progress: 0.0–1.0"""
    layers = [
        (NEON_YELLOW, 0.00, 320),
        (NEON_ORANGE, 0.10, 290),
        (NEON_RED,    0.24, 260),
        (DARK_GRAY,   0.42, 230),
    ]
    for color, offset, max_r in layers:
        p = max(0.0, progress - offset)
        if p <= 0:
            continue
        r     = int(p * max_r)
        alpha = max(0, 255 - int(p * 320))
        ring  = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*color, alpha), (r+2, r+2), r)
        surface.blit(ring, (cx - r - 2, cy - r - 2))


def draw_ghost(surface, cx, cy, frame):
    """Ghost floats up after death."""
    rise  = min(frame * 1.4, 150)
    gx    = cx + int(math.sin(frame * 0.09) * 16)
    gy    = cy - int(rise)
    alpha = max(0, 255 - int(rise * 2.0))
    g     = pygame.Surface((50, 65), pygame.SRCALPHA)
    pygame.draw.ellipse(g, (*GHOST_WHITE, alpha), (2, 2, 46, 36))
    pygame.draw.rect(g,   (*GHOST_WHITE, alpha), (2, 24, 46, 22))
    for i in range(4):
        pygame.draw.circle(g, (*BG_DARK, alpha), (7 + i * 12, 46), 9)
    pygame.draw.circle(g, (*BLACK, alpha), (17, 20), 5)
    pygame.draw.circle(g, (*BLACK, alpha), (33, 20), 5)
    pygame.draw.arc(g, (*BLACK, alpha), (16, 27, 18, 9), math.pi, 2*math.pi, 2)
    pygame.draw.circle(g, (*DIM_GOLD, alpha), (25, 56), 7)
    surface.blit(g, (gx - 25, gy - 32))


def draw_flying_money(surface, particles):
    font = pygame.font.SysFont("impact", 18)
    for p in particles:
        alpha = max(0, 255 - int(p["life"] * 3))
        label = font.render(p["sym"], True, NEON_GOLD)
        label.set_alpha(alpha)
        surface.blit(label, (int(p["x"]), int(p["y"])))


def draw_button(surface, rect, text, font, hovered=False,
                col_on=NEON_GREEN, col_off=DARK_GREEN, disabled=False):
    """Neon arcade button."""
    if disabled:
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=12)
        pygame.draw.rect(surface, MID_GRAY,  rect, 2, border_radius=12)
        lbl = font.render(text, True, MID_GRAY)
        surface.blit(lbl, lbl.get_rect(center=rect.center))
        return
    shadow_rect = rect.move(0, 5)
    shadow_col  = tuple(max(0, c - 80) for c in col_off)
    pygame.draw.rect(surface, shadow_col, shadow_rect, border_radius=12)
    fill_col = col_on if hovered else col_off
    pygame.draw.rect(surface, fill_col, rect, border_radius=12)
    if hovered:
        glow_s = pygame.Surface((rect.w + 14, rect.h + 14), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, (*col_on, 50), (0, 0, rect.w+14, rect.h+14), border_radius=14)
        surface.blit(glow_s, (rect.x - 7, rect.y - 7))
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=12)
    lbl = font.render(text, True, WHITE)
    surface.blit(lbl, lbl.get_rect(center=rect.center))


def draw_risk_meter(surface, rect, num_bullets, frame):
    """Visual risk meter showing loaded bullet ratio."""
    risk = num_bullets / NUM_CHAMBERS
    bg = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
    pygame.draw.rect(surface, DARK_GRAY, bg, border_radius=8)
    fill_w = int(rect.w * risk)
    if fill_w > 0:
        pulse = 0.7 + 0.3 * math.sin(frame * 0.12)
        r_col = lerp_color(NEON_GREEN, NEON_RED, risk)
        r_col = tuple(int(c * pulse) for c in r_col)
        fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.h)
        pygame.draw.rect(surface, r_col, fill_rect, border_radius=8)
    pygame.draw.rect(surface, MID_GRAY, bg, 2, border_radius=8)


def draw_chamber_dots(surface, cx, y, num_bullets):
    """Row of 6 chamber dots showing loaded vs empty."""
    spacing = 28
    total_w = 5 * spacing
    x0 = cx - total_w // 2
    for i in range(NUM_CHAMBERS):
        x = x0 + i * spacing
        if i < num_bullets:
            glow_circle(surface, NEON_RED, (x, y), 8, 18, 60)
            pygame.draw.circle(surface, NEON_RED, (x, y), 8)
        else:
            pygame.draw.circle(surface, DARK_GRAY, (x, y), 8)
            pygame.draw.circle(surface, MID_GRAY,  (x, y), 8, 2)


# ─────────────────────────────────────────────
#  SETUP SCREEN
# ─────────────────────────────────────────────

def draw_setup_screen(surface, num_bullets, frame,
                      font_large, font_medium, font_small, font_tiny, mouse):
    """Pre-game bullet count selector."""
    surface.fill(BG_DARK)

    # Animated title
    cycle = (math.sin(frame * 0.05) + 1) / 2
    title_col = lerp_color(NEON_GOLD, NEON_ORANGE, cycle)
    draw_neon_text(surface, "EXPLOSION ROULETTE", font_large,
                   title_col, (WIDTH // 2, 90))

    draw_neon_text(surface, "HIGH STAKES EDITION", font_small,
                   NEON_CYAN, (WIDTH // 2, 142))

    # Panel
    panel = pygame.Rect(WIDTH // 2 - 280, 180, 560, 480)
    draw_panel(surface, panel, glow=True)

    draw_neon_text(surface, "LOAD THE CYLINDER", font_medium,
                   NEON_CYAN, (WIDTH // 2, 218))

    draw_neon_text(surface, "How many bullets?", font_small,
                   LIGHT_GRAY, (WIDTH // 2, 268))

    # Bullet count display
    draw_neon_text(surface, str(num_bullets), font_large,
                   NEON_RED if num_bullets > 1 else NEON_GREEN,
                   (WIDTH // 2, 330))

    # Chamber dots
    draw_chamber_dots(surface, WIDTH // 2, 390, num_bullets)

    # Odds display
    survive_pct = (NUM_CHAMBERS - num_bullets) / NUM_CHAMBERS * 100
    odds_col = lerp_color(NEON_GREEN, NEON_RED, num_bullets / NUM_CHAMBERS)
    draw_neon_text(surface, f"Survival chance per pull: {survive_pct:.0f}%",
                   font_small, odds_col, (WIDTH // 2, 424))

    # Risk label
    risk_labels = ["COZY", "SPICY", "DANGEROUS", "CRAZY", "SUICIDAL"]
    rlabel = risk_labels[num_bullets - 1]
    draw_neon_text(surface, rlabel, font_medium,
                   odds_col, (WIDTH // 2, 460))

    # Risk meter
    meter = pygame.Rect(WIDTH // 2 - 180, 492, 360, 20)
    draw_risk_meter(surface, meter, num_bullets, frame)

    # Bullet +/- buttons
    btn_minus = pygame.Rect(WIDTH // 2 - 200, 310, 60, 60)
    btn_plus  = pygame.Rect(WIDTH // 2 + 140, 310, 60, 60)
    draw_button(surface, btn_minus, "-", font_large,
                btn_minus.collidepoint(mouse),
                NEON_RED, DARK_RED, disabled=(num_bullets <= MIN_BULLETS))
    draw_button(surface, btn_plus,  "+", font_large,
                btn_plus.collidepoint(mouse),
                NEON_GREEN, DARK_GREEN, disabled=(num_bullets >= MAX_BULLETS))

    # Start button
    start_btn = pygame.Rect(WIDTH // 2 - 150, 546, 300, 56)
    draw_button(surface, start_btn, "ENTER THE CASINO",
                font_medium, start_btn.collidepoint(mouse),
                NEON_GOLD, DIM_GOLD)

    draw_neon_text(surface, "Arrow keys to adjust  |  ENTER to start",
                   font_tiny, MID_GRAY, (WIDTH // 2, 626), glow=False)

    return btn_minus, btn_plus, start_btn


# ─────────────────────────────────────────────
#  MAIN MINIGAME FUNCTION
# ─────────────────────────────────────────────

def run_explosion_roulette(screen, clock,
                           starting_cash: int = STARTING_CASH,
                           num_bullets: int = DEFAULT_BULLETS) -> dict:
    """
    Run the Explosion Roulette gambling minigame.

    Parameters:
        screen        : pygame.Surface
        clock         : pygame.time.Clock
        starting_cash : int — cash the player enters with
        num_bullets   : int — bullets pre-loaded (1–5); if 0, shows setup screen

    Returns:
        dict with keys:
            "outcome" : "survived" | "exploded" | "cashed_out"
            "cash"    : int — player's cash after the minigame
    """
    pygame.font.init()

    try:
        font_large  = pygame.font.SysFont("impact",     52)
        font_medium = pygame.font.SysFont("impact",     34)
        font_small  = pygame.font.SysFont("impact",     24)
        font_tiny   = pygame.font.SysFont("couriernew", 17)
    except Exception:
        font_large  = pygame.font.SysFont(None, 52)
        font_medium = pygame.font.SysFont(None, 34)
        font_small  = pygame.font.SysFont(None, 24)
        font_tiny   = pygame.font.SysFont(None, 17)

    # ── Layout constants ──
    cx, cy       = WIDTH // 2 + 80, HEIGHT // 2 + 10
    bomb_pos     = (cx, cy - 120)
    cyl_pos      = (cx - 20, cy + 60)
    char_pos     = (cx + 230, cy - 20)
    lever_rect   = pygame.Rect(cx - 160, HEIGHT - 80, 270, 52)
    cashout_rect = pygame.Rect(cx + 120, HEIGHT - 80, 190, 52)

    # Bet panel (left)
    bet_panel    = pygame.Rect(12,  85, 235, 580)
    # Info panel (right)
    info_panel   = pygame.Rect(WIDTH - 230, 85, 218, 340)

    bet_up_r   = pygame.Rect(bet_panel.x + 150, bet_panel.y + 128, 44, 34)
    bet_dn_r   = pygame.Rect(bet_panel.x + 12,  bet_panel.y + 128, 44, 34)
    bet_max_r  = pygame.Rect(bet_panel.x + 130, bet_panel.y + 172, 68, 26)
    bet_min_r  = pygame.Rect(bet_panel.x + 12,  bet_panel.y + 172, 68, 26)
    confirm_r  = pygame.Rect(bet_panel.x + 12,  bet_panel.bottom - 58,
                              bet_panel.w - 24, 44)
    bullet_r   = pygame.Rect(bet_panel.x + 12,  bet_panel.bottom - 110,
                              bet_panel.w - 24, 40)

    # ── Game state ──
    showing_setup   = (num_bullets == 0)
    setup_bullets   = DEFAULT_BULLETS
    cash            = starting_cash
    bet             = min(50, cash)
    state           = GS.SETUP if showing_setup else GS.BETTING
    loaded_chambers = []
    exploded        = False
    quip            = ""
    streak          = 0
    frame           = 0
    spin_angle      = 0.0
    spin_start      = 0
    result_timer    = 0
    explosion_prog  = 0.0
    ghost_frame     = 0
    shake_frames    = 0
    shake_offset    = (0, 0)
    money_particles = []
    session_profit  = 0
    outcome         = "survived"
    active_bullets  = num_bullets if num_bullets > 0 else DEFAULT_BULLETS

    def pick_loaded_chambers():
        chambers = random.sample(range(NUM_CHAMBERS), active_bullets)
        return chambers

    def current_multiplier():
        idx = min(streak, len(ROUND_MULTIPLIERS) - 1)
        return ROUND_MULTIPLIERS[idx]

    def survive_chance():
        return (NUM_CHAMBERS - active_bullets) / NUM_CHAMBERS

    def spawn_money(px, py, count=14):
        syms = ["$", "+$", "$$", "$$$", "CA-CHING", "PROFIT"]
        for _ in range(count):
            money_particles.append({
                "x":   px + random.randint(-60, 60),
                "y":   py,
                "vy":  random.uniform(-4.5, -1.5),
                "vx":  random.uniform(-2.0, 2.0),
                "sym": random.choice(syms),
                "life": 0,
            })

    def reset_round():
        nonlocal loaded_chambers, exploded, quip, explosion_prog, ghost_frame
        loaded_chambers = pick_loaded_chambers()
        exploded        = False
        quip            = ""
        explosion_prog  = 0.0
        ghost_frame     = 0
        money_particles.clear()

    if not showing_setup:
        reset_round()

    while True:
        clock.tick(60)
        frame += 1
        mouse  = pygame.mouse.get_pos()

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return {"outcome": "cashed_out", "cash": cash}

                if state == GS.SETUP:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_UP:
                        setup_bullets = min(setup_bullets + 1, MAX_BULLETS)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_DOWN:
                        setup_bullets = max(setup_bullets - 1, MIN_BULLETS)
                    if event.key == pygame.K_RETURN:
                        active_bullets = setup_bullets
                        state = GS.BETTING
                        reset_round()

                elif state == GS.BETTING:
                    if event.key == pygame.K_RIGHT:
                        bet = min(bet + BET_STEP, min(MAX_BET, cash))
                    if event.key == pygame.K_LEFT:
                        bet = max(bet - BET_STEP, MIN_BET)
                    if event.key == pygame.K_UP:
                        bet = min(bet + 100, min(MAX_BET, cash))
                    if event.key == pygame.K_DOWN:
                        bet = max(bet - 100, MIN_BET)
                    if event.key == pygame.K_RETURN and bet <= cash:
                        state = GS.IDLE

                elif state == GS.IDLE:
                    if event.key == pygame.K_SPACE:
                        state      = GS.SPINNING
                        spin_start = frame
                    if event.key == pygame.K_c and streak > 0:
                        state   = GS.CASHOUT
                        quip    = random.choice(CASHOUT_LINES)
                        outcome = "cashed_out"

                elif state in (GS.GAMEOVER, GS.CASHOUT):
                    if event.key == pygame.K_r and cash >= MIN_BET:
                        return run_explosion_roulette(screen, clock, cash, 0)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == GS.SETUP:
                    btn_minus, btn_plus, start_btn = draw_setup_screen(
                        screen, setup_bullets, frame,
                        font_large, font_medium, font_small, font_tiny, mouse)
                    if btn_minus.collidepoint(mouse) and setup_bullets > MIN_BULLETS:
                        setup_bullets -= 1
                    if btn_plus.collidepoint(mouse) and setup_bullets < MAX_BULLETS:
                        setup_bullets += 1
                    if start_btn.collidepoint(mouse):
                        active_bullets = setup_bullets
                        state = GS.BETTING
                        reset_round()

                elif state == GS.BETTING:
                    if bet_up_r.collidepoint(mouse):
                        bet = min(bet + BET_STEP, min(MAX_BET, cash))
                    if bet_dn_r.collidepoint(mouse):
                        bet = max(bet - BET_STEP, MIN_BET)
                    if bet_max_r.collidepoint(mouse):
                        bet = min(MAX_BET, cash)
                    if bet_min_r.collidepoint(mouse):
                        bet = MIN_BET
                    if confirm_r.collidepoint(mouse) and bet <= cash:
                        state = GS.IDLE

                elif state == GS.IDLE:
                    if lever_rect.collidepoint(mouse):
                        state      = GS.SPINNING
                        spin_start = frame
                    if cashout_rect.collidepoint(mouse) and streak > 0:
                        state   = GS.CASHOUT
                        quip    = random.choice(CASHOUT_LINES)
                        outcome = "cashed_out"

                elif state in (GS.GAMEOVER, GS.CASHOUT):
                    again_r = pygame.Rect(cx - 170, HEIGHT // 2 + 100, 340, 54)
                    leave_r = pygame.Rect(cx - 170, HEIGHT // 2 + 164, 340, 46)
                    if again_r.collidepoint(mouse) and cash >= MIN_BET:
                        return run_explosion_roulette(screen, clock, cash, 0)
                    if leave_r.collidepoint(mouse):
                        return {"outcome": outcome, "cash": cash}

        # ── State transitions ──
        if state == GS.SPINNING:
            spin_angle += 0.22 + 0.08 * math.sin(frame * 0.3)
            if frame - spin_start >= SPIN_DURATION_FRAMES:
                # Determine outcome: pick a random firing chamber
                fired    = random.randint(0, NUM_CHAMBERS - 1)
                exploded = (fired in loaded_chambers)
                state    = GS.RESULT
                result_timer = frame

                if exploded:
                    quip            = random.choice(DEATH_MESSAGES)
                    shake_frames    = 60
                    outcome         = "exploded"
                    cash           -= bet
                    session_profit -= bet
                else:
                    payout          = int(bet * current_multiplier())
                    profit          = payout - bet
                    cash           += profit
                    session_profit += profit
                    quip            = random.choice(SURVIVAL_QUIPS)
                    streak         += 1
                    outcome         = "survived"
                    spawn_money(cx, cy, 18)

        if state == GS.RESULT and exploded:
            explosion_prog = min(1.0, explosion_prog + 0.015)
            ghost_frame   += 1

        if state == GS.RESULT:
            if frame - result_timer >= RESULT_SHOW_FRAMES:
                if exploded or cash < MIN_BET:
                    state = GS.GAMEOVER
                else:
                    bet   = min(bet, cash)
                    state = GS.BETTING
                    reset_round()

        # Money particles
        for p in money_particles:
            p["x"]   += p["vx"]
            p["y"]   += p["vy"]
            p["vy"]  += 0.06
            p["life"] += 1
        money_particles[:] = [p for p in money_particles if p["life"] < 95]

        # Screen shake
        if shake_frames > 0:
            shake_frames -= 1
            intensity     = shake_frames // 5 + 1
            shake_offset  = (random.randint(-intensity, intensity),
                             random.randint(-intensity, intensity))
        else:
            shake_offset = (0, 0)
        ox, oy = shake_offset

        # ─────────────────────────────────────────────
        #  DRAW
        # ─────────────────────────────────────────────

        # Setup screen is fully handled separately
        if state == GS.SETUP:
            draw_setup_screen(screen, setup_bullets, frame,
                              font_large, font_medium, font_small, font_tiny, mouse)
            pygame.display.flip()
            continue

        draw_bg(screen, frame)

        # ── Animated Title ──
        cycle     = (math.sin(frame * 0.045) + 1) / 2
        title_col = lerp_color(NEON_GOLD, NEON_ORANGE, cycle)
        draw_neon_text(screen, "💣  EXPLOSION ROULETTE  💣",
                       font_large, title_col, (WIDTH // 2, 38))

        # ── Left Bet Panel ──
        draw_panel(screen, bet_panel, glow=(state == GS.BETTING))
        mid = bet_panel.centerx

        draw_neon_text(screen, "PLACE YOUR BET", font_tiny, NEON_CYAN,
                       (mid, bet_panel.y + 16))

        draw_neon_text(screen, "YOUR CASH", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 46))
        cash_col = NEON_GREEN if cash > starting_cash else (NEON_RED if cash < starting_cash else NEON_GOLD)
        draw_neon_text(screen, f"${cash:,}", font_medium, cash_col,
                       (mid, bet_panel.y + 70))

        pygame.draw.line(screen, PANEL_BORDER,
                         (bet_panel.x + 14, bet_panel.y + 104),
                         (bet_panel.right - 14, bet_panel.y + 104))

        draw_neon_text(screen, "YOUR BET", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 112))
        bet_col = NEON_RED if bet > cash else NEON_YELLOW
        draw_neon_text(screen, f"${bet:,}", font_medium, bet_col,
                       (mid, bet_panel.y + 136))

        payout = int(bet * current_multiplier())
        draw_neon_text(screen, "POTENTIAL PAYOUT", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 176))
        draw_neon_text(screen, f"${payout:,}", font_small, NEON_GREEN,
                       (mid, bet_panel.y + 198))
        draw_neon_text(screen, f"{current_multiplier():.2f}x multiplier",
                       font_tiny, NEON_CYAN, (mid, bet_panel.y + 224))

        pygame.draw.line(screen, PANEL_BORDER,
                         (bet_panel.x + 14, bet_panel.y + 248),
                         (bet_panel.right - 14, bet_panel.y + 248))

        draw_neon_text(screen, "SURVIVAL STREAK", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 258))
        streak_col = NEON_ORANGE if streak >= 3 else (NEON_YELLOW if streak > 0 else MID_GRAY)
        draw_neon_text(screen, f"{streak} round(s)", font_medium, streak_col,
                       (mid, bet_panel.y + 282))

        pygame.draw.line(screen, PANEL_BORDER,
                         (bet_panel.x + 14, bet_panel.y + 316),
                         (bet_panel.right - 14, bet_panel.y + 316))

        # Bullet config display
        draw_neon_text(screen, "BULLETS IN CYLINDER", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 326))
        b_col = lerp_color(NEON_GREEN, NEON_RED, active_bullets / NUM_CHAMBERS)
        draw_neon_text(screen, f"{active_bullets} / {NUM_CHAMBERS}", font_medium, b_col,
                       (mid, bet_panel.y + 350))
        surv_pct = int(survive_chance() * 100)
        draw_neon_text(screen, f"{surv_pct}% survive chance", font_tiny, b_col,
                       (mid, bet_panel.y + 378))
        meter_r = pygame.Rect(bet_panel.x + 14, bet_panel.y + 402, bet_panel.w - 28, 16)
        draw_risk_meter(screen, meter_r, active_bullets, frame)

        # Session profit
        pygame.draw.line(screen, PANEL_BORDER,
                         (bet_panel.x + 14, bet_panel.y + 430),
                         (bet_panel.right - 14, bet_panel.y + 430))
        draw_neon_text(screen, "SESSION P&L", font_tiny, MID_GRAY,
                       (mid, bet_panel.y + 440))
        sp_col = NEON_GREEN if session_profit >= 0 else NEON_RED
        sp_str = f"{'+'if session_profit>=0 else ''}${session_profit:,}"
        draw_neon_text(screen, sp_str, font_small, sp_col,
                       (mid, bet_panel.y + 462))

        # Bet buttons when in BETTING state
        if state == GS.BETTING:
            draw_button(screen, bet_up_r,  "+$10", font_tiny,
                        bet_up_r.collidepoint(mouse), NEON_GREEN, DARK_GREEN)
            draw_button(screen, bet_dn_r,  "-$10", font_tiny,
                        bet_dn_r.collidepoint(mouse), NEON_RED, DARK_RED)
            draw_button(screen, bet_max_r, "MAX",  font_tiny,
                        bet_max_r.collidepoint(mouse),
                        NEON_GOLD, DIM_GOLD)
            draw_button(screen, bet_min_r, "MIN",  font_tiny,
                        bet_min_r.collidepoint(mouse),
                        NEON_CYAN, (0, 60, 90))
            ready = (bet <= cash)
            draw_button(screen, confirm_r,
                        "LET'S GO!" if ready else "TOO BROKE",
                        font_medium,
                        confirm_r.collidepoint(mouse) and ready,
                        (NEON_GREEN if ready else NEON_RED),
                        (DARK_GREEN if ready else DARK_RED),
                        disabled=not ready)
            hint = font_tiny.render("← → adjust  |  ENTER to confirm", True, MID_GRAY)
            screen.blit(hint, hint.get_rect(centerx=mid, y=bet_panel.bottom + 6))

        # ── Cylinder ──
        revealed = state in (GS.RESULT, GS.GAMEOVER)
        draw_cylinder(screen, cyl_pos[0] + ox, cyl_pos[1] + oy,
                      loaded_chambers, revealed=revealed, spin_angle=spin_angle)
        cyl_lbl = font_tiny.render("CYLINDER", True, MID_GRAY)
        screen.blit(cyl_lbl, cyl_lbl.get_rect(
            centerx=cyl_pos[0], y=cyl_pos[1] + CYLINDER_RADIUS + 16))

        # ── Character ──
        draw_character(screen, char_pos[0] + ox, char_pos[1] + oy,
                       state, frame, survived=not exploded)

        # ── Bomb ──
        if not (state == GS.RESULT and exploded):
            draw_bomb(screen, bomb_pos[0] + ox, bomb_pos[1] + oy,
                      fuse_lit=(state == GS.SPINNING), frame=frame)

        # ── Explosion + ghost ──
        if state in (GS.RESULT, GS.GAMEOVER) and exploded:
            draw_explosion(screen, bomb_pos[0] + ox, bomb_pos[1] + oy,
                           explosion_prog)
            draw_ghost(screen, bomb_pos[0] + ox, bomb_pos[1] + oy, ghost_frame)

        draw_flying_money(screen, money_particles)

        # ── Spinning label ──
        if state == GS.SPINNING:
            dots  = "." * ((frame // 10) % 4)
            draw_neon_text(screen, f"Spinning{dots}", font_medium,
                           NEON_YELLOW, (cx + ox, cy + 175 + oy))

        # ── Result banner ──
        if state == GS.RESULT:
            if exploded:
                draw_neon_text(screen, "💥  BOOM — YOU LOSE  💥",
                               font_large, NEON_RED,
                               (cx + ox, cy + 168 + oy))
                draw_neon_text(screen, f"-${bet:,}  gone forever.",
                               font_small, DARK_RED,
                               (cx + ox, cy + 216 + oy))
            else:
                prev_mul = ROUND_MULTIPLIERS[min(streak - 1, len(ROUND_MULTIPLIERS) - 1)]
                profit   = int(bet * prev_mul) - bet
                draw_neon_text(screen, f"SAFE!  +${profit:,}",
                               font_large, NEON_GREEN,
                               (cx + ox, cy + 168 + oy))
                draw_neon_text(screen, f"{prev_mul:.2f}x multiplier!",
                               font_small, NEON_GOLD,
                               (cx + ox, cy + 216 + oy))

            words = quip.split()
            mid_i = max(1, len(words) // 2)
            for i, line in enumerate([" ".join(words[:mid_i]),
                                      " ".join(words[mid_i:])]):
                qt = font_tiny.render(line, True, LIGHT_GRAY)
                screen.blit(qt, qt.get_rect(
                    centerx=cx + ox, y=cy + 248 + oy + i * 22))

        # ── IDLE action buttons ──
        if state == GS.IDLE:
            draw_button(screen, lever_rect, "PULL LEVER  [SPACE]",
                        font_small, lever_rect.collidepoint(mouse),
                        NEON_GREEN, DARK_GREEN)
            can_cash = streak > 0
            draw_button(screen, cashout_rect, "CASH OUT  [C]",
                        font_small, cashout_rect.collidepoint(mouse) and can_cash,
                        NEON_GOLD, DIM_GOLD, disabled=not can_cash)

            hint2 = font_tiny.render(
                f"Next pull pays {current_multiplier():.2f}x  |  "
                f"Streak: {streak}  |  C = cash out  |  "
                f"Odds: {surv_pct}% survive",
                True, MID_GRAY)
            screen.blit(hint2, hint2.get_rect(centerx=cx, y=HEIGHT - 26))

        # ── CASHOUT overlay ──
        if state == GS.CASHOUT:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 185))
            screen.blit(ov, (0, 0))

            draw_neon_text(screen, "💰  CASHED OUT!  💰",
                           font_large, NEON_GOLD, (cx, HEIGHT // 2 - 110))
            sp_col = NEON_GREEN if session_profit >= 0 else NEON_RED
            sp_str = f"Session profit:  {'+'if session_profit>=0 else ''}${session_profit:,}"
            draw_neon_text(screen, sp_str, font_medium, sp_col, (cx, HEIGHT // 2 - 52))
            draw_neon_text(screen, f"Walking away with  ${cash:,}",
                           font_medium, WHITE, (cx, HEIGHT // 2 + 6))
            draw_neon_text(screen, quip, font_tiny, LIGHT_GRAY, (cx, HEIGHT // 2 + 60))

            again_r = pygame.Rect(cx - 170, HEIGHT // 2 + 100, 340, 54)
            leave_r = pygame.Rect(cx - 170, HEIGHT // 2 + 164, 340, 46)
            draw_button(screen, again_r, "PLAY AGAIN  [R]",
                        font_medium, again_r.collidepoint(mouse),
                        NEON_GREEN, DARK_GREEN)
            draw_button(screen, leave_r, "LEAVE TABLE  [ESC]",
                        font_medium, leave_r.collidepoint(mouse),
                        NEON_RED, DARK_RED)

        # ── GAME OVER overlay ──
        if state == GS.GAMEOVER:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 190))
            screen.blit(ov, (0, 0))

            go_text = "BROKE AND DEAD" if cash <= 0 else "YOU  EXPLODED"
            draw_neon_text(screen, go_text, font_large, NEON_RED, (cx, HEIGHT // 2 - 120))

            sp_col = NEON_GREEN if session_profit >= 0 else NEON_RED
            sp_str = f"Session:  {'+'if session_profit>=0 else ''}${session_profit:,}"
            draw_neon_text(screen, sp_str, font_medium, sp_col, (cx, HEIGHT // 2 - 60))
            draw_neon_text(screen, f"Cash remaining:  ${max(0,cash):,}",
                           font_medium, WHITE, (cx, HEIGHT // 2 - 4))
            draw_neon_text(screen, f"Best streak: {streak} round(s)",
                           font_small, NEON_ORANGE, (cx, HEIGHT // 2 + 44))
            draw_neon_text(screen, quip, font_tiny, LIGHT_GRAY, (cx, HEIGHT // 2 + 82))

            again_r = pygame.Rect(cx - 170, HEIGHT // 2 + 110, 340, 54)
            leave_r = pygame.Rect(cx - 170, HEIGHT // 2 + 174, 340, 46)

            if cash >= MIN_BET:
                draw_button(screen, again_r, "PLAY AGAIN  [R]",
                            font_medium, again_r.collidepoint(mouse),
                            NEON_GREEN, DARK_GREEN)
                draw_button(screen, leave_r, "LEAVE TABLE  [ESC]",
                            font_medium, leave_r.collidepoint(mouse),
                            NEON_RED, DARK_RED)
            else:
                draw_neon_text(screen, "COMPLETELY BUSTED.  Yikes.",
                               font_medium, NEON_RED, (cx, HEIGHT // 2 + 126))
                draw_button(screen, leave_r, "WALK OF SHAME  [ESC]",
                            font_medium, leave_r.collidepoint(mouse),
                            NEON_RED, DARK_RED)

        pygame.display.flip()


# ─────────────────────────────────────────────
#  STANDALONE ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("💣 Explosion Roulette — High Stakes Edition")
    clock  = pygame.time.Clock()

    # Pass num_bullets=0 to show the bullet-selector setup screen
    result = run_explosion_roulette(screen, clock,
                                    starting_cash=STARTING_CASH,
                                    num_bullets=0)
    print(f"\n[Explosion Roulette]  outcome={result['outcome']}  "
          f"cash=${result['cash']:,}")

    pygame.quit()
    sys.exit()