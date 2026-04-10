import pygame
import sys
import textwrap

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
W, H = 1000, 1000
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Isaac Dating Sim")
clock = pygame.time.Clock()

# ── Colours ───────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
DARK_GREY  = (30,  30,  40)
PANEL_BG   = (20,  20,  35, 220)   # semi-transparent dialogue box
BTN_NORMAL = (60,  60,  100)
BTN_HOVER  = (100, 100, 160)
BTN_BORDER = (180, 180, 255)
NAME_BG    = (15,  15,  30)
PINK       = (255, 150, 180)
GOLD       = (255, 215, 0)
RED        = (200, 60,  60)

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_large  = pygame.font.SysFont("segoeuisymbol", 32, bold=True)
font_med    = pygame.font.SysFont("segoeuisymbol", 24)
font_small  = pygame.font.SysFont("segoeuisymbol", 20)
font_tiny   = pygame.font.SysFont("segoeuisymbol", 17)

# ── Asset loading helpers ─────────────────────────────────────────────────────
def load_image(path, size=None):
    """Try to load an image; return None on failure."""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

# ── SWAP YOUR IMAGES IN HERE ──────────────────────────────────────────────────
bg_image      = load_image("background.png", (W, H))
isaac_image   = load_image("isaac.png", (340, 500))
# bar_image     = load_image("bar_bg.png", (W, H))  # optional bar scene bg

# ─────────────────────────────────────────────────────────────────────────────

# ── Story data ────────────────────────────────────────────────────────────────
# Each node: { "text": str, "choices": [(label, next_key), ...] }
# A node with no choices is an ending.

def build_story(name):
    return {
        "start": {
            "text": "You walk up to the big man. He smiles and says... Hello.",
            "choices": [
                ("Hey big guy, what's your name?",          "a_greet"),
                ("Shut up nerd! What's your name?",         "b_greet"),
                ("Leave without saying a word",             "end_leave"),
            ]
        },
        # ── Branch A ──────────────────────────────────────────────────────────
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
                ("Go in for a kiss 💋",                      "end_explode_kiss"),
                ("Thank you! Want to get a drink with me? (milk 🥛)", "a_milk_ask"),
            ]
        },
        "a_milk_ask": {
            "text": "Isaac, still tomato-red, says: Yes I do!!",
            "choices": [
                ("Great!! Let's go!",                        "a_bar"),
                ("*you pull out a bazooka* 🪖",              "end_jail"),
            ]
        },
        "a_bar": {
            "text": "You both walk up to the bar and order a tall glass of milk.",
            "choices": [
                ("Drink your milk 🥛",                       "end_milk_explode"),
                ("Get down on one knee and propose 💍",      "end_married"),
            ]
        },
        "a_rude": {
            "text": "You push Isaac away and sprint out the door. He watches you go, confused.",
            "choices": [],   # ending
            "ending": "💨 Ending: Not Interested"
        },
        # ── Branch B ──────────────────────────────────────────────────────────
        "b_greet": {
            "text": "Isaac looks confused. He says: Nerd?! My name's Isaac and I'm NO nerd!",
            "choices": [
                ("That's EXACTLY what a nerd would say, NERD!!",  "b_meanie"),
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
                ("HAHAHA!!!! YOU'RE A STUPID NERD!!!!!!!",               "b_yell"),
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
                ("...What???",       "end_backflip"),
                ("Bet, nerd!! 👟",   "end_nsfw"),
            ]
        },
        # ── Endings ───────────────────────────────────────────────────────────
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
            "text": f"You get on one knee and ask: Isaac, will you be the love of my life? Isaac replies with almost no hesitation: YES!! You get married on the spot. Turns out Isaac was secretly rich. {name} gains +1,000,000,000 💰",
            "choices": [],
            "ending": "💍 Ending: RICH MARRIED ENDING"
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

# ── Drawing helpers ───────────────────────────────────────────────────────────
def draw_background():
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        # Placeholder gradient-style background
        for y in range(H):
            t = y / H
            r = int(10 + 30 * t)
            g = int(5  + 15 * t)
            b = int(40 + 60 * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (W, y))

def draw_isaac(highlight=False, bounce_y=0, shake_xy=(0,0), spin_angle=0.0, pop_scale=1.0):
    """Draw Isaac with optional bounce, shake, spin and pop animations."""
    base_x = 330 + shake_xy[0]
    base_y = 180 + int(bounce_y) + shake_xy[1]
    portrait_rect = pygame.Rect(base_x, base_y, 340, 500)

    # Build Isaac onto a temp surface so we can rotate/scale the whole thing
    surf_w, surf_h = 340, 500
    isaac_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

    if isaac_image:
        isaac_surf.blit(isaac_image, (0, 0))
    else:
        color = (180, 100, 120) if highlight else (140, 80, 100)
        pygame.draw.rect(isaac_surf, color, (0, 0, surf_w, surf_h), border_radius=20)
        cx, cy = surf_w // 2, 120
        pygame.draw.circle(isaac_surf, (240, 190, 160), (cx, cy), 70)
        pygame.draw.circle(isaac_surf, (60, 40, 30),   (cx - 22, cy - 10), 10)
        pygame.draw.circle(isaac_surf, (60, 40, 30),   (cx + 22, cy - 10), 10)
        if highlight:
            pygame.draw.circle(isaac_surf, PINK, (cx - 30, cy + 10), 14)
            pygame.draw.circle(isaac_surf, PINK, (cx + 30, cy + 10), 14)
        smile = pygame.Rect(cx - 25, cy + 20, 50, 28)
        pygame.draw.arc(isaac_surf, (180, 80, 80), smile, 3.6, 6.3, 4)
        body = pygame.Rect(surf_w // 2 - 110, cy + 70, 220, 280)
        pygame.draw.rect(isaac_surf, (80, 60, 120), body, border_radius=15)
        label = font_small.render("Isaac", True, WHITE)
        isaac_surf.blit(label, (surf_w // 2 - label.get_width() // 2, surf_h - 30))

    # Apply spin (rotate around centre)
    if spin_angle != 0.0:
        isaac_surf = pygame.transform.rotate(isaac_surf, spin_angle)

    # Apply pop scale
    if pop_scale != 1.0:
        new_w = max(1, int(surf_w * pop_scale))
        new_h = max(1, int(surf_h * pop_scale))
        isaac_surf = pygame.transform.smoothscale(isaac_surf, (new_w, new_h))

    # Centre the (possibly resized) surface on where Isaac normally sits
    draw_x = base_x + surf_w // 2 - isaac_surf.get_width() // 2
    draw_y = base_y + surf_h // 2 - isaac_surf.get_height() // 2
    screen.blit(isaac_surf, (draw_x, draw_y))

def draw_dialogue_box(text, speaker="Narrator"):
    box_rect = pygame.Rect(20, 700, W - 40, 160)
    # Semi-transparent panel
    surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    surf.fill((15, 10, 35, 210))
    screen.blit(surf, box_rect.topleft)
    pygame.draw.rect(screen, BTN_BORDER, box_rect, 2, border_radius=12)

    # Speaker label
    spk = font_med.render(speaker, True, PINK)
    screen.blit(spk, (box_rect.x + 18, box_rect.y + 10))

    # Wrapped dialogue text
    wrapped = textwrap.wrap(text, width=72)
    for i, line in enumerate(wrapped[:4]):
        surf_line = font_small.render(line, True, WHITE)
        screen.blit(surf_line, (box_rect.x + 18, box_rect.y + 44 + i * 26))

def draw_buttons(choices, mouse_pos):
    """Draw choice buttons; return list of (rect, key) pairs."""
    btn_h   = 48
    btn_gap = 10
    total   = len(choices) * (btn_h + btn_gap) - btn_gap
    start_y = 695 - total - 10
    buttons = []
    for i, (label, key) in enumerate(choices):
        bx = 60
        by = start_y + i * (btn_h + btn_gap)
        bw = W - 120
        rect = pygame.Rect(bx, by, bw, btn_h)
        color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_NORMAL
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=10)
        letter = chr(65 + i)   # A, B, C …
        txt = font_med.render(f"[{letter}]  {label}", True, WHITE)
        screen.blit(txt, (rect.x + 16, rect.y + (btn_h - txt.get_height()) // 2))
        buttons.append((rect, key))
    return buttons

def draw_ending_screen(ending_text):
    screen.fill(DARK_GREY)
    lines = textwrap.wrap(ending_text, width=40)
    y = H // 2 - len(lines) * 24
    for line in lines:
        surf = font_large.render(line, True, GOLD)
        screen.blit(surf, (W // 2 - surf.get_width() // 2, y))
        y += 50
    hint = font_small.render("Press ENTER or click to play again", True, WHITE)
    screen.blit(hint, (W // 2 - hint.get_width() // 2, y + 30))

# ── Name entry screen ─────────────────────────────────────────────────────────
def name_entry_screen():
    name = ""
    cursor_timer = 0
    show_cursor  = True

    while True:
        dt = clock.tick(60)
        cursor_timer += dt
        if cursor_timer > 500:
            show_cursor  = not show_cursor
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 20 and event.unicode.isprintable():
                    name += event.unicode

        screen.fill(NAME_BG)

        # Title
        title = font_large.render("💕  Isaac Dating Sim  💕", True, PINK)
        screen.blit(title, (W//2 - title.get_width()//2, 200))

        prompt = font_med.render("Enter your name:", True, WHITE)
        screen.blit(prompt, (W//2 - prompt.get_width()//2, 340))

        # Input box
        box = pygame.Rect(W//2 - 200, 390, 400, 55)
        pygame.draw.rect(screen, NAME_BG, box, border_radius=8)
        pygame.draw.rect(screen, BTN_BORDER, box, 2, border_radius=8)
        display = name + ("|" if show_cursor else " ")
        txt_surf = font_med.render(display, True, WHITE)
        screen.blit(txt_surf, (box.x + 12, box.y + 12))

        hint = font_small.render("Press ENTER to start", True, (160, 160, 200))
        screen.blit(hint, (W//2 - hint.get_width()//2, 460))

        pygame.display.flip()

# ── Main game loop ─────────────────────────────────────────────────────────────
def main():
    player_name = name_entry_screen()
    story       = build_story(player_name)
    state       = "start"
    fade_alpha  = 255          # fade-in on new node
    in_ending   = False
    ending_text = ""

    # Text-reveal animation
    reveal_index  = 0
    reveal_timer  = 0
    REVEAL_DELAY  = 22          # ms per character

    current_text  = ""
    full_text     = ""

    # ── Isaac animation state ─────────────────────────────────────────────────
    import math, random
    anim_time    = 0.0      # total elapsed seconds (drives idle bounce)
    shake_timer  = 0.0      # countdown for shake (seconds)
    spin_angle   = 0.0      # current rotation degrees
    spin_timer   = 0.0      # countdown for spin
    pop_scale    = 1.0      # current scale for pop
    pop_timer    = 0.0      # countdown for pop
    ending_delay = 0.0      # wait before showing ending screen
    # which animations to trigger on each story state
    ANIM_MAP = {
        "a_pretty":        "pop",
        "end_explode_kiss":"spin",
        "end_milk_explode":"spin",
        "end_backflip":    "spin",
        "b_yell":          "shake",
        "b_meanie":        "shake",
        "end_married":     "pop",
        "end_jail":        "shake",
    }

    def enter_state(new_state):
        nonlocal state, fade_alpha, reveal_index, reveal_timer, full_text, current_text
        nonlocal shake_timer, spin_timer, spin_angle, pop_timer, pop_scale, ending_delay
        state         = new_state
        fade_alpha    = 180
        full_text     = story[state]["text"]
        current_text  = ""
        reveal_index  = 0
        reveal_timer  = 0
        ending_delay  = 0.0
        # trigger animation for this state
        anim = ANIM_MAP.get(new_state, "")
        if anim == "shake":
            shake_timer = 0.5
        elif anim == "spin":
            spin_timer  = 0.8
            spin_angle  = 0.0
        elif anim == "pop":
            pop_timer   = 0.4
            pop_scale   = 1.0

    enter_state("start")

    while True:
        dt          = clock.tick(60)
        dt_s        = dt / 1000.0          # delta-time in seconds
        anim_time  += dt_s
        mouse_pos   = pygame.mouse.get_pos()
        node        = story.get(state, {})
        choices     = node.get("choices", [])
        text_done   = reveal_index >= len(full_text)

        # ── Update Isaac animations ────────────────────────────────────────────
        # Idle bounce: gentle sine wave
        bounce_y = math.sin(anim_time * 2.5) * 6

        # Shake — clamp amp to at least 1 to avoid randint(0,0) crash
        if shake_timer > 0:
            shake_timer -= dt_s
            amp = max(1, int(10 * (shake_timer / 0.5)))
            shake_xy = (random.randint(-amp, amp),
                        random.randint(-(amp // 2 + 1), amp // 2 + 1))
        else:
            shake_xy = (0, 0)

        # Spin
        if spin_timer > 0:
            spin_timer -= dt_s
            spin_angle = (1 - spin_timer / 0.8) * 360
        else:
            spin_angle = 0.0

        # Pop (scale up then back)
        if pop_timer > 0:
            pop_timer -= dt_s
            t = 1 - (pop_timer / 0.4)
            pop_scale = 1.0 + 0.35 * math.sin(t * math.pi)
        else:
            pop_scale = 1.0

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                # Skip text reveal
                if not text_done and event.key == pygame.K_SPACE:
                    current_text = full_text
                    reveal_index = len(full_text)
                # Restart from ending
                if in_ending and event.key == pygame.K_RETURN:
                    in_ending = False
                    story     = build_story(player_name)
                    enter_state("start")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Skip text reveal on click
                if not text_done:
                    current_text = full_text
                    reveal_index = len(full_text)
                elif in_ending:
                    in_ending = False
                    story     = build_story(player_name)
                    enter_state("start")
                elif text_done and choices:
                    buttons = draw_buttons(choices, mouse_pos)
                    for rect, key in buttons:
                        if rect.collidepoint(event.pos):
                            next_node = story.get(key, {})
                            if not next_node.get("choices") and "ending" in next_node:
                                # It's a terminal node — show ending after its text
                                enter_state(key)
                                # We'll catch the ending after text finishes
                            else:
                                enter_state(key)

        # ── Text reveal ───────────────────────────────────────────────────────
        if not text_done:
            reveal_timer += dt
            while reveal_timer >= REVEAL_DELAY and reveal_index < len(full_text):
                current_text  += full_text[reveal_index]
                reveal_index  += 1
                reveal_timer  -= REVEAL_DELAY

        # After text finishes on an ending node, count down then show ending screen
        if text_done and "ending" in node and not choices and not in_ending:
            ending_delay += dt_s
            if ending_delay >= 2.5:          # 2.5 second pause so player can read
                in_ending   = True
                ending_text = node["ending"]
                ending_delay = 0.0

        # ── Draw ──────────────────────────────────────────────────────────────
        if in_ending:
            draw_ending_screen(ending_text)
        else:
            draw_background()

            # Isaac portrait (blush if "blush" words in text)
            blush_words = ["blushes", "tomato", "pretty", "blushing", "love", "marry"]
            highlight   = any(w in full_text.lower() for w in blush_words)
            draw_isaac(highlight, bounce_y=bounce_y, shake_xy=shake_xy,
                       spin_angle=spin_angle, pop_scale=pop_scale)

            # Speaker detection
            speaker = "Isaac" if full_text.lower().startswith("isaac") or \
                                  "isaac says" in full_text.lower() or \
                                  full_text.lower().startswith("ok i guess") else "Narrator"

            draw_dialogue_box(current_text, speaker)

            if text_done and choices:
                draw_buttons(choices, mouse_pos)

            # Show a gentle "..." hint while waiting to transition to ending
            if text_done and "ending" in node and not choices and not in_ending:
                dots = "." * (int(ending_delay * 2) % 4)
                hint_surf = font_small.render(f"ending incoming{dots}", True, (160, 160, 200))
                screen.blit(hint_surf, (W // 2 - hint_surf.get_width() // 2, 670))

            # Fade overlay
            if fade_alpha > 0:
                fade_surf = pygame.Surface((W, H))
                fade_surf.set_alpha(fade_alpha)
                fade_surf.fill(BLACK)
                screen.blit(fade_surf, (0, 0))
                fade_alpha = max(0, fade_alpha - 8)

        pygame.display.flip()

if __name__ == "__main__":
    main()