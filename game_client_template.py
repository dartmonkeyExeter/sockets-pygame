import pygame
import socket
import threading

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Networking setup
HOST = "127.0.0.1"
PORT = 5555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

class Client():
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.x -= 5
        if keys[pygame.K_RIGHT]: self.x += 5
        if keys[pygame.K_UP]: self.y -= 5
        if keys[pygame.K_DOWN]: self.y += 5

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
       
class OtherClient():
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)        

color = input("Enter your color (red, blue, green): ").lower()

if color == "red":
    player = Client(250, 250, RED, "test")
elif color == "blue":
    player = Client(250, 250, BLUE, "test")
elif color == "green":
    player = Client(250, 250, GREEN, "test")
else:
    player = Client(250, 250, (255,255,255), "test")

other_players = {}  # Stores other players' classes
running = True

def receive_data():
    """Handles receiving data from the server."""
    global other_players
    while running:
        try:
            data = client.recv(1024).decode()
            if not data:
                continue  # Skip empty messages

            parts = data.split(": ")
            if len(parts) != 2:
                print("Received malformed data:", data)
                continue  # Ignore incorrectly formatted data

            addr, info = parts
            x, y, color, name = info.split("; ")
            r, g, b = color.split(", ")
            r = r [1:]
            b = b[:-1]

            other_players[addr] = OtherClient(int(x), int(y), (int(r), int(g), int(b)), name)
        except Exception as e:
            print("Error receiving data:", e)


# Start receiving data in a separate thread
threading.Thread(target=receive_data, daemon=True).start()

while running:
    screen.fill((30, 30, 30))  # Background color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.move()
    player.draw()

    # Send player position to server
    data = f"{player.x}; {player.y}; {player.color}; {player.name}"
    client.send(data.encode())

    # Draw other players
    for other_player in other_players.values():
        other_player.draw()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
client.close()
