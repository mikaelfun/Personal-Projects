import pygame, time
from pygame.locals import *
import os.path

done = False

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1920,1010))
fontobject = pygame.font.SysFont(None ,24)
all_fonts = pygame.font.get_fonts()
print(all_fonts)
# Try to play around with other fonts, it failed for me :(
#fontobject = pygame.font.Font("gillsans" ,24)

message = "Hi Kun, 12345"

# Make screen black
screen.fill((255, 255, 255))
i = 0
fontobject = pygame.font.SysFont(str(all_fonts[i]) ,24)
# Endless loop until clicked on window X or Keyboard ESC
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
           done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
           done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # Actually draw the stuff to the screen
            screen.blit(fontobject.render(str(all_fonts[i])+": "+message, True, (0,0,0)), (0 , i*30 ))
            pygame.display.flip()
            i+=1
            if i == len(all_fonts):
                done = True
            else:
                fontobject = pygame.font.SysFont(str(all_fonts[i]) ,24)
