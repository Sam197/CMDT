import socket
import select
from serverConfig import *

global running 
running = True

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

global sockets_list
sockets_list = [server_socket]

global clients
clients = {}

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = message_header.decode(protocol)
        message_length.strip()
        message_length = int(message_length)
        #message_length = int(pickle.loads(message_header).strip())
        return client_socket.recv(message_length).decode(protocol)

    except:
        return False

def send_message_all(message, clients, active_socket):
    message_headder = f"{len(message):<{HEADER_LENGTH}}".encode(protocol)
    for client_socket in clients:
        if client_socket != active_socket:
            client_socket.send(message_headder + bytes(message, protocol))

def main():

    print("WHOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

    while running:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        if not running:
            break

        for active_socket in read_sockets:
            if active_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                
                user = recieve_message(client_socket)

                if user is False:
                    continue

                sockets_list.append(client_socket)

                clients[client_socket] = user
                
                print(f"Accepted connection from {client_address[0]} : {client_address[1]}, username {user}")
                #send_message_all(f"Server: {user} has joined the chat", clients, active_socket)
            
            else:

                message = recieve_message(active_socket)

                if message is False:
                    print(f"Closed connection from {clients[active_socket]}")
                    #send_message_all(f"Server: {clients[active_socket]} has left the chat", clients, client_socket)

                    sockets_list.remove(active_socket)
                    del clients[active_socket]
                    continue

                #print(f"Recv {clients[active_socket]} > {message}")
                send_message_all(f"{message}", clients, active_socket)

if __name__=='__main__':
    main()