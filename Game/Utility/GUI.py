import sys

import pygame

class Button:
    """
    Syntax: 
    Button(x, y, width, height, color, hover_color, text, textSize, text_color)
    """
    def __init__(self,  x, y, width, height, color, hover_color, text, textSize, text_color=(255, 255, 255)):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', textSize)
        self.is_hovered = False

    def draw(self, surface):
        # Change color if hovered for visual feedback
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)

        # Center text on the button
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        # Update hover state based on current mouse position
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        # Check for a left-click while hovering
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
class ExitButton(Button):
    """
    Syntax: 
    Button(x, y, width, height, color, hover_color, text, textSize, text_color)
    """
    def __init__(self,  x, y, width, height, color, hover_color, text, textSize, text_color=(255, 255, 255)):
        super().__init__(x, y, width, height, color, hover_color, text, textSize, text_color)
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', textSize)
        self.is_hovered = False

    def handle_event(self, event):
        # Check for a left-click while hovering
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                pygame.quit()
                sys.exit()
        return False