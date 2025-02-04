# so first we're just gonna make a simple pygame game
# the game will be a simple tank game!!!

import pygame
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
fps = 60

class Grid():
    def __init__(self):
        self.grid =["########",
                    "#      #",
                    "#      #",
                    "#      #",
                    "#      #",
                    "#      #",
                    "#      #",
                    "########"]
        
    def draw(self):
        for y, row in enumerate(self.grid):
            for x, col in enumerate(row):
                if col == "#":
                    pygame.draw.rect(screen, (0, 0, 0), (x * 50, y * 50, 50, 50))

class Player():
    def __init__(self, x, y, rotation, speed):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.bullets = []
        self.speed = speed
        
    def move(self, grid):
        keys = pygame.key.get_pressed()
        wall_collision = self.wall_collision(grid)
        
        self.stuck(grid) # jsut in case the player gets stuck 
        
        if keys[pygame.K_LEFT]: self.rotation += self.speed
        if keys[pygame.K_RIGHT]: self.rotation -= self.speed
        
        if keys[pygame.K_UP]:
            dx = self.speed * math.cos(math.radians(self.rotation))
            dy = self.speed * math.sin(math.radians(self.rotation))
            
            if "right" in wall_collision and dx > 0:
                dx = 0
            if "left" in wall_collision and dx < 0:
                dx = 0
            if "up" in wall_collision and dy < 0:
                dy = 0
            if "down" in wall_collision and dy > 0:
                dy = 0
        if keys[pygame.K_DOWN]: 
            dx = -self.speed * math.cos(math.radians(self.rotation))
            dy = -self.speed * math.sin(math.radians(self.rotation))
            
            if "right" in wall_collision and dx < 0:
                dx = 0
            if "left" in wall_collision and dx > 0:
                dx = 0
            if "up" in wall_collision and dy > 0:
                dy = 0
            if "down" in wall_collision and dy < 0:
                dy = 0
                       
    def stuck(self, grid):
        if len(self.wall_collision(grid)) > 2:
            if "left" in self.wall_collision(grid):
                self.x += 5
            if "right" in self.wall_collision(grid):
                self.x -= 5
            if "up" in self.wall_collision(grid):
                self.y += 5
            if "down" in self.wall_collision(grid):
                self.y -= 5

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 50, 50))
        
    def shoot(self):
        bullet = Bullet(self.x + (self.speed * math.cos(math.radians(self.rotation))), self.y + (self.speed * math.sin(math.radians(self.rotation))), self.rotation)
        self.bullets.append(bullet)
                
    def wall_collision(self, grid):
            try:
                hitbox_width, hitbox_height = 50, 50
                
                which_walls = []
                
                points = [
                    (self.x - hitbox_width // 2, self.y),
                    (self.x + hitbox_width // 2, self.y),
                    (self.x, self.y - hitbox_height // 2),
                    (self.x, self.y + hitbox_height // 2)
                ]
                
                order = ["left", "right", "down", "up"]
                
                for idx, point in enumerate(points):
                    x, y = point
                    grid_x, grid_y = x // 50, y // 50
                    if grid.grid[grid_y - 1][grid_x - 1] == "#":
                        which_walls.append(order[idx])
                        
                return which_walls
            except:
                print(points)
                print(grid_x, grid_y)
                return []
                    
    def update(self):
        for bullet in self.bullets:
            bullet.update()
            
        self.move(grid)
        self.draw()

class Bullet():
    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        
    def move(self):
        self.x += 10 * math.cos(math.radians(self.rotation))
        self.y += 10 * math.sin(math.radians(self.rotation))
        
    def draw(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 5)

    def update(self):
        self.move()
        self.draw()

# Initialize game objects
grid = Grid()
player = Player(200, 200, 0, 5)


def update():
    screen.fill((255, 255, 255))
    grid.draw()
    player.update()
    pygame.display.flip()
    
# Game loop
running = True

while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
                
    update()
    
pygame.quit()