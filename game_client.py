import pygame

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game Client")
running = True
clientNumber = 0

class Player():
    def __init__(self, x, y, name, colour):
        self.x = x
        self.y = y
        self.name = name
        self.colour = colour

    def draw(self, win):
        pygame.draw.circle(win, self.colour, (self.x, self.y), 10)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= 1
        if keys[pygame.K_RIGHT]:
            self.x += 1
        if keys[pygame.K_UP]:
            self.y -= 1
        if keys[pygame.K_DOWN]:
            self.y += 1

    def chat(self):