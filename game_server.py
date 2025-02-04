import socket
import sys
import _thread

server = "192.0.0.1"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(5)
print("Waiting for a connection, Server Started")

def threaded_client(conn):
    reply = ""
    while True:
        try:
            data = conn.recv0(2048)
            reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                print("Received:", reply)
                print("Sending:", reply)

            conn.sendall(str.encode(reply))
        except:
            break

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    _thread.start_new_thread(threaded_client, (conn,))