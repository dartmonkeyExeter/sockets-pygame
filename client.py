# so first we're just gonna make a simple pygame game
# the game will be a simple tank game!!!

import pygame, math, socket, threading

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
fps = 60

# network setup
HOST = "127.0.0.1"
PORT = 25565
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Grid():
    def __init__(self):
        self.grid =["########",
                    "#      #",
                    "#   #  #",
                    "#  #   #",
                    "#   #  #",
                    "#  #   #",
                    "#      #",
                    "########"]
        
    def draw(self):
        for y, row in enumerate(self.grid):
            for x, col in enumerate(row):
                if col == "#":
                    pygame.draw.rect(screen, (0, 0, 0), (x * 50, y * 50, 50, 50)) 

class Player():
    def __init__(self, x, y, rotation, color, speed):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.speed = speed
        self.color = color
        self.bullet_cooldown = 0.25
        self.time_elapsed = 0
        self.size = 30
        
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

        # we should also check the players rect hit box, in addition to the vertices
        # this is to account for outward-facing corners

        half_size = (self.size / 2) + 2 # add for a buffer
        rect_left   = x - half_size
        rect_top    = y - half_size
        rect_right  = x + half_size
        rect_bottom = y + half_size

        # Convert the hitbox boundaries to grid indices. 
        # (Assuming each grid cell is 50x50 pixels.)
        grid_left   = int(rect_left / 50)
        grid_right  = int(rect_right / 50)
        grid_top    = int(rect_top / 50)
        grid_bottom = int(rect_bottom / 50)

        # Iterate over all grid cells covered by the hitbox.
        for grid_y in range(grid_top, grid_bottom + 1):
            for grid_x in range(grid_left, grid_right + 1):
                # Make sure we don't go out of bounds on the grid.
                if 0 <= grid_y < len(grid.grid) and 0 <= grid_x < len(grid.grid[0]):
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
        pygame.draw.polygon(screen, self.color, vertices, 4)
        # draw a little black box as turret
        width = 5
        height = 25
        offset = 10

        # Define the vertices of the square relative to the center
        vertices = [
            ((-width / 2), (-height / 2) - offset),
            ((width / 2), (-height / 2) - offset),
            ((width / 2), (height / 2) - offset),
            ((-width / 2), (height / 2) - offset)
        ]

        angle = math.radians(self.rotation + 90)
        rotated_vertices = []
        for x, y in vertices:
            new_x = x * math.cos(angle) - y * math.sin(angle)
            new_y = x * math.sin(angle) + y * math.cos(angle)
            rotated_vertices.append((new_x + self.x, new_y + self.y))
        
        pygame.draw.polygon(screen, (0, 0, 0), rotated_vertices)
        
    def calculate_polygon(self, rot, x_calc, y_calc):
        # Calculate the half-size of the square
        half_size = self.size / 2

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
        bullets.append(bullet)

    def update(self, grid):
        self.move(grid)
        self.draw()

def gen_id():
    # uuid isnt working, get the lowest number that isnt in the list
    id = 0
    for bullet in bullets:
        if bullet.id == id:
            id += 1
    return id

class Bullet():
    def __init__(self, x, y, rotation, id=gen_id()):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.id = id
        
    def move(self, grid):
        self.x += 10 * math.cos(math.radians(self.rotation))
        self.y += 10 * math.sin(math.radians(self.rotation))

        if self.x < 0 or self.x > 400 or self.y < 0 or self.y > 400 or self.check_collision(grid):
            bullets.remove(self)
        
    def draw(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 5)

    def check_collision(self, grid):
        grid_x, grid_y = int(self.x / 50), int(self.y / 50)
        if grid.grid[grid_y][grid_x] == "#":
            return True

    def update(self, grid):
        self.move(grid)
        self.draw()



class OtherPlayer():
    def __init__(self, x, y, rotation, color):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.color = color
        self.size = 30

    def draw(self):
        vertices = self.calculate_polygon(self.rotation, self.x, self.y)

        # Draw the rotated polygon
        pygame.draw.polygon(screen, self.color, vertices, 4)

                # draw a little black box as turret
        width = 5
        height = 25
        offset = 10

        # Define the vertices of the square relative to the center
        vertices = [
            ((-width / 2), (-height / 2) - offset),
            ((width / 2), (-height / 2) - offset),
            ((width / 2), (height / 2) - offset),
            ((-width / 2), (height / 2) - offset)
        ]

        angle = math.radians(self.rotation + 90)
        rotated_vertices = []
        for x, y in vertices:
            new_x = x * math.cos(angle) - y * math.sin(angle)
            new_y = x * math.sin(angle) + y * math.cos(angle)
            rotated_vertices.append((new_x + self.x, new_y + self.y))
        
        pygame.draw.polygon(screen, (0, 0, 0), rotated_vertices)

    def calculate_polygon(self, rot, x_calc, y_calc):
        # Calculate the half-size of the square
        half_size = self.size / 2

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

    def update(self):
        self.draw()

# Initialize game objects
grid = Grid()
player = None
other_player = None
bullets = []

def update():
    screen.fill((255, 255, 255))
    player.update(grid)
    other_player.update()
    for bullet in bullets:
        bullet.update(grid)
    grid.draw()
    pygame.display.flip()

start = False # only start the game when the server says to
# Game loop
running = True

def send_start_data(): # send the message to the server that the player is ready
    global start
    while not start:
        data = f'start'
        client.send(data.encode()) # send the message to the server that the player is ready

def receive_start_data(): # assigning players color and position
    global start, player, other_player

    while not start:
        try:
            data = client.recv(1024).decode()
            dtype = data.split("[")[0]
            data = data.split("[")[1] # using ; as a delimiter
            data = data.split(";") # split the data


            if dtype == "start":
                # this assumes data is "start;x;y;rotation;r;g;b;x;y;rotation;r;g;b"
                player = Player(int(data[0]), int(data[1]), int(data[2]), (int(data[3]), int(data[4]), int(data[5])), 2)
                other_player = OtherPlayer(int(data[6]), int(data[7]), int(data[8]), (int(data[9]), int(data[10]), int(data[11])))
                start = True # this should end this thread
                print("players created game start")
        except Exception as e:
            print(e)
            print("error line 350")
            break

def receive_game_data(): # when the game is started, recieve the other player's data and update the game
    global bullets, other_player, start
    while True:
        if start:
            try:
                data = client.recv(1024).decode()
                dtype = data.split("[")[0]

                print("data:", data)

                if dtype == "update":
                    data = data.split("[")[1] # using ; as a delimiter
                    recv_bullets = data.split(":")[0] # split the bullets from the main data
                    recv_bullets = recv_bullets.split("#") # split the bullets individually
                    data = data.split(";") # split the data

                    print("data:", data)

                    other_player.x = float(data[0])
                    other_player.y = float(data[1])
                    other_player.rotation = int(data[2])


                    for rb in recv_bullets:
                        if rb != "":
                            rb = rb.split(";")
                            id = rb[0]

                            found = False

                            for i in range(len(bullets) - 1):
                                b = bullets[i]
                                if b.id == id:
                                    b.x = float(rb[1])
                                    b.y = float(rb[2])
                                    b.rotation = int(rb[3])
                                    found = True
                                    break
                            
                            if not found:
                                bullet = Bullet(float(rb[1]), float(rb[2]), int(rb[3]))
                                bullets.append(bullet)
                    
            except Exception as e:
                print("Error receiving data...")
                print("data:", data)
                print(e)

                break

def send_data():
    global player, bullets, start
    while True:
        if start:
            try:
                bullet_data = ""
                for bullet in bullets:
                    # bullet data is in the format "id;x;y;rotation"
                    bullet_data += f"{bullet.id};{bullet.x};{bullet.y};{bullet.rotation};#"
                data = f"update[{player.x};{player.y};{player.rotation};:{bullet_data}:]"
                client.send(data.encode())
            except Exception as e:
                print("Error sending data:", e)
                break


client.connect((HOST, PORT)) # connect to the server

# start threads
threading.Thread(target=send_start_data, daemon=True).start()
threading.Thread(target=receive_start_data, daemon=True).start()
threading.Thread(target=receive_game_data, daemon=True).start()
threading.Thread(target=send_data, daemon=True).start()

while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                
    if not start:
        # display text that we're waiting for another player
        font = pygame.font.Font(None, 36)
        text = font.render("Waiting for another player...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(200, 200))
        screen.blit(text, text_rect)
        pygame.display.flip()
        
    if start:
        keys = pygame.key.get_pressed()
        
        player.time_elapsed += 1 / fps

        if keys[pygame.K_SPACE] and player.time_elapsed >= player.bullet_cooldown:
            player.shoot()
            player.time_elapsed = 0

        update()
    
pygame.quit()