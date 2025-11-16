import pygame

# INIT PYGAME
pygame.init()

# CREATE DISPLAY SURFACE
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('TEST KNIGHT')

#DEFINE COLORS AS RGB TUPLSE

#THE MAIN GAME LOOP
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False




#END THE GAME
pygame.quit()