import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []  # List to store connected clients

print("Server is listening...")

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    clients.append(conn)

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Received from {addr}: {data}")

            # Broadcast the received data to all clients
            for client in clients:
                if client != conn:
                    client.send(f"{addr}: {data}".encode())

        except:
            break

    print(f"Connection closed: {addr}")
    clients.remove(conn)
    conn.close()

# Accept multiple clients
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
