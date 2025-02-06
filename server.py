import socket
import threading

HOST = "127.0.0.1"
PORT = 25565

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

dtype = "" # data type

# player class for storing player data
class Player():
    def __init__(self, x, y, color, rotation):
        self.x = x
        self.y = y
        self.color = color
        self.rotation = rotation

class Bullet():
    def __init__(self, x, y, rotation, id):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.id = id

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

            if data == "start" and len(clients) == 2:
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
                        start_data_send = f"start[{players[addr].x};{players[addr].y};{players[addr].rotation};{players[addr].color[0]};{players[addr].color[1]};{players[addr].color[2]};{players[other].x};{players[other].y};{players[other].rotation};{players[other].color[0]};{players[other].color[1]};{players[other].color[2]};"
                        client_conn.send(start_data_send.encode())
                    else:
                        # since we're using two threads, we dont need to send the start data to the other client in this thread
                        pass

                print("game started (hopefully)")

            try: 
                dtype = data.split("[")[0]
            except:
                dtype = "PLACEHOLDER"
                continue # data isn't typed, usually means we haven't started

            
            if dtype == "update":
                # update data is in the format "update;x;y;rotation;bullets"
                
                print("data:", data)

                recv_bullets = data.split(":")[1] # split the bullets
                recv_bullets = recv_bullets.split("#") # split the bullets

                data = data.split("[")[1] # using ; as a delimiter
                data = data.split(";") # split the data

                print("data:", data)

                players[addr].x = float(data[0])
                players[addr].y = float(data[1])
                players[addr].rotation = int(data[2])


                # ok bullets time
                for rb in recv_bullets:
                    if rb != "":
                        rb = rb.split(";")
                        id = rb[0]

                        found = False

                        for i in range(len(synced_bullets) - 1):
                            sb = synced_bullets[i]
                            
                            if sb.id == id:
                                sb.x = float(rb[1])
                                sb.y = float(rb[2])
                                sb.rotation = int(rb[3])
                                found = True
                                break
                        
                        if not found:
                            bullet = Bullet(float(rb[1]), float(rb[2]), int(rb[3]), id)
                            synced_bullets.append(bullet)

                # Broadcast the received data to all clients
                for client_addr, client_conn in clients.items():
                    if client_addr != addr:
                        bullet_data = ""
                        for bullet in synced_bullets:
                            bullet_data += f"{bullet.id};{bullet.x};{bullet.y};{bullet.rotation};#"

                        client_conn.send(f"update;{players[addr].x};{players[addr].y};{players[addr].rotation};:{bullet_data}:;".encode())
                        # adding the semicolon at the end is important for the client to know when to stop reading data

        except:
            break

    print(f"Connection closed: {addr}")
    del clients[addr]
    conn.close()

# Accept multiple clients
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()