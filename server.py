import socket
import threading
import queue

HOST = "127.0.0.1"
PORT = 25565

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

data_queue = queue.Queue()
clients = {}  # stores client connections
players = {}  # stores player classes
synced_bullets = []  # for syncing bullets between clients

# Player class
class Player():
    def __init__(self, x, y, color, rotation):
        self.x = x
        self.y = y
        self.color = color
        self.rotation = rotation

# Bullet class
class Bullet():
    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation

print("Server is listening...")

def process_data():
    while True:
        addr, data = data_queue.get()
        if not data:
            continue
        
        if len(clients) != 2:  # Ensure two clients are connected before processing
            continue
        
        dtype = data.split("[")[0]
        
        if dtype == "start" and len(clients) == 2:
            idx = 0
            for client_addr in clients.keys():
                if idx == 0:
                    players[client_addr] = Player(100, 175, (255, 0, 0), 0)
                else:
                    players[client_addr] = Player(300, 175, (0, 0, 255), 0)
                idx += 1
            
            for client_addr, client_conn in clients.items():
                other = list(clients.keys())
                other.remove(client_addr)
                other = other[0]
                
                start_data_send = f"start[{players[client_addr].x};{players[client_addr].y};{players[client_addr].rotation};{players[client_addr].color[0]};{players[client_addr].color[1]};{players[client_addr].color[2]};"
                start_data_send += f"{players[other].x};{players[other].y};{players[other].rotation};{players[other].color[0]};{players[other].color[1]};{players[other].color[2]};"
                client_conn.send(start_data_send.encode())
            
            print("Game started")
        
        elif dtype == "playerupdate":
            data = data.split("[")[1].split(";")[:-1]
            players[addr].x = float(data[0])
            players[addr].y = float(data[1])
            players[addr].rotation = int(data[2])
            
            for client_addr, client_conn in clients.items():
                if client_addr != addr:
                    client_conn.send(f"playerupdate[{players[addr].x};{players[addr].y};{players[addr].rotation};]".encode())
        
        elif dtype == "bulletupdate":
            data = data.split("[")[1].split(";")[:-1]
            synced_bullets.append(Bullet(float(data[0]), float(data[1]), int(data[2])))
            
            for client_conn in clients.values():
                for bullet in synced_bullets:
                    client_conn.send(f"bulletupdate[{bullet.x};{bullet.y};{bullet.rotation};]".encode())

# Start the data processing thread
threading.Thread(target=process_data, daemon=True).start()

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    clients[addr] = conn

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            
            data_queue.put((addr, data))  # Add received data to the queue
        except:
            break

    print(f"Connection closed: {addr}")
    del clients[addr]
    conn.close()

# Accept multiple clients
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
