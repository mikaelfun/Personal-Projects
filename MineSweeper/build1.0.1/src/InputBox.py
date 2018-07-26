import pygame as pg
import sys

COLOR_INACTIVE = (170, 20, 30)
COLOR_ACTIVE = (215, 218, 251)
COLOR_BG = (0,0, 0)
pg.font.init()
FONT = pg.font.SysFont('cambria', 40)

class InputBox:
    def __init__(self, x, y, w, h, text='', modify = True):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        a, b = FONT.size(self.text)
        #a = w - a
        b = h - b
        # print (a,b)
        #self.rect.x -= a
        self.rect.y += b
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.tileSize =h
        self.selectAll = False
        self.modify = modify

    def handle_event(self, event):
        if not self.modify:
            return None
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.selectAll = True
            else:
                self.selectAll = False
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    pass
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.selectAll:
                        self.text = event.unicode
                        self.selectAll = False
                    elif len(self.text) < 2:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(self.tileSize, self.txt_surface.get_width())
        self.rect.w = width
        # print (self.rect.w, self.rect.h)

    def draw(self, screen):
        # Blit the text.
        if self.active:
            pg.draw.rect(screen, COLOR_BG, self.rect)
        self.txt_surface = FONT.render(self.text, True, self.color)
        screen.blit(self.txt_surface, (self.rect.x, self.rect.y))
        # Blit the rect.

