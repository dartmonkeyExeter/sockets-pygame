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

        dx, dy = 0, 0
        moving = False

        # Handle Forward and Backward Movement
        if keys[pygame.K_UP]:
            dx += self.speed * math.cos(math.radians(self.rotation))
            dy += self.speed * math.sin(math.radians(self.rotation))
            moving = True

        if keys[pygame.K_DOWN]:
            dx -= self.speed * math.cos(math.radians(self.rotation))
            dy -= self.speed * math.sin(math.radians(self.rotation))
            moving = True

        # Check movement separately for X and Y to allow sliding
        if not self.check_collision(grid, self.x + dx, self.y):
            self.x += dx
        if not self.check_collision(grid, self.x, self.y + dy):
            self.y += dy

        # Prevent turning while moving forward/backward
        if not moving:
            if keys[pygame.K_LEFT]:
                self.handle_rotation(grid, -1)
                    
            if keys[pygame.K_RIGHT]:
                self.handle_rotation(grid, 1)
                
    def check_collision(self, grid, x, y, rotation=None):
        """Check if the given position (and optional rotation) collides with a wall."""
        if rotation is None:
            rotation = self.rotation  # Default to current rotation

        potential_collides = self.calculate_polygon(rotation, x, y)
        for vertex in potential_collides:
            grid_x, grid_y = int(vertex[0] / 50), int(vertex[1] / 50)
            if grid.grid[grid_y][grid_x] == "#":
                return True  # Collision detected
        return False  # No collision

    def handle_rotation(self, grid, direction):
        # Determine the new rotation based on the direction
        new_rotation = self.rotation + (direction * self.speed)
        
        # Check for collision with the new rotation
        check_collision = self.check_collision(grid, self.x, self.y, new_rotation)
        if not check_collision:
            self.rotation = new_rotation
            return
        
        # Calculate the vertices for the new rotation
        vertices = self.calculate_polygon(new_rotation, self.x, self.y)
        colliding_vert = None
        
        # Find the colliding vertex
        for vertex in vertices:
            grid_x, grid_y = int(vertex[0] / 50), int(vertex[1] / 50)
            if grid.grid[grid_y][grid_x] == "#":
                colliding_vert = vertex
                break
        
        if colliding_vert is not None:
            # Sort vertices to determine which side is colliding
            x_sorted = sorted(vertices, key=lambda x: x[0])
            y_sorted = sorted(vertices, key=lambda x: x[1])
            
            # Adjust position based on the colliding side
            if colliding_vert[0] == x_sorted[0][0]:
                # Colliding with the left side
                self.x += self.speed
            elif colliding_vert[0] == x_sorted[-1][0]:
                # Colliding with the right side
                self.x -= self.speed
            if colliding_vert[1] == y_sorted[0][1]:
                # Colliding with the top side
                self.y += self.speed
            elif colliding_vert[1] == y_sorted[-1][1]:
                # Colliding with the bottom side
                self.y -= self.speed
        
        # Update the rotation
        self.rotation = new_rotation

    def draw(self):
        vertices = self.calculate_polygon(self.rotation, self.x, self.y)

        # Draw the rotated polygon
        pygame.draw.polygon(screen, (255, 0, 0), vertices)
        
    def calculate_polygon(self, rot, x_calc, y_calc):
        # Calculate the half-size of the square
        half_size = 50 / 2

        # Define the vertices of the square relative to the center
        vertices = [
            (-half_size, -half_size),
            (half_size, -half_size),
            (half_size, half_size),
            (-half_size, half_size)
        ]

        # Convert rotation angle from degrees to radians
        angle = math.radians(rot)

        # Rotate each vertex around the center (0, 0)
        rotated_vertices = []
        for x, y in vertices:
            # Apply rotation transformation
            new_x = x * math.cos(angle) - y * math.sin(angle)
            new_y = x * math.sin(angle) + y * math.cos(angle)
            # Translate to the square's position
            rotated_vertices.append((new_x + x_calc, new_y + y_calc))

        return rotated_vertices
        
    def shoot(self):
        bullet = Bullet(self.x + (self.speed * math.cos(math.radians(self.rotation))), self.y + (self.speed * math.sin(math.radians(self.rotation))), self.rotation)
        self.bullets.append(bullet)

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
player = Player(200, 200, 270, 2)


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