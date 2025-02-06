import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

# player class for storing player data
class Player():
    def __init__(self, x, y, color, rotation):
        self.x = x
        self.y = y
        self.color = color
        self.rotation = rotation

clients = {} # stores client connections
players = {} # stores player classes

# not gonna program this yet
synced_bullets = [] # for syncing bullets between clients

print("Server is listening...")

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    clients[addr] = conn

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            if len(clients) != 2: # check if there are 2 clients connected
                continue

            if data[0] == "start":
                idx = 0
                for client_addr, client_conn in clients.items():
                    if idx == 0:
                        players[client_addr] = Player(100, 175, (255, 0, 0), 0)
                    else:
                        players[client_addr] = Player(300, 175, (0, 0, 255), 0)
                    idx += 1

                for client_addr, client_conn in clients.items():
                    if client_addr == addr:
                        other = list(clients.keys())
                        other.remove(addr)
                        other = other[0]

                        # this assumes data is "start;x;y;rotation;r;g;b;x;y;rotation;r;g;b"
                        

                        

            data = data.split(";")

            if data[0] == "update":
                # update data is in the format "update;x;y;rotation;bullets"
                players[addr].x = int(data[1])
                players[addr].y = int(data[2])
                players[addr].rotation = int(data[3])

                # ignoring bullets for now

                # Broadcast the received data to all clients
                for client_addr, client_conn in clients.items():
                    if client_addr != addr:
                        client_conn.send(f"update;{players[addr].x};{players[addr].y};{players[addr].rotation}".encode())
        except:
            break

    print(f"Connection closed: {addr}")
    del clients[addr]
    conn.close()

# Accept multiple clients
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()