import socket
from clientConfig import *        # pylint: disable=W0614
from config import SERVER_CLIENT_ENABLED
from tkinter import messagebox
import errno

def connect():

    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TARGET_IP, TARGET_PORT))
        client_socket.setblocking(False)
    except IOError as e:
        if e.errno == errno.ECONNREFUSED:
            messagebox.showerror('Connect', 'Could not connect')
            print("No connection")

connect()
username = input("Username>")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode(protocol)
client_socket.send(username_header + username.encode(protocol))

def send(message):
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode(protocol)
    client_socket.send(message_header + message.encode(protocol))

def send_string(inList):
    string = ""
    for i in inList:
        string += i
        string += "/"
    send(string[:-1])

def msg_to_list(msg):
    return msg.split("/")

def update():
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
            print("Connection closed by sever")
        message_length = int(message_header.decode(protocol).strip())
        message = client_socket.recv(message_length).decode(protocol)
        return msg_to_list(message) 

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            if e.errno == errno.ECONNRESET:
                print("Server closed connection")
            print("Reading Error", str(e))
        return None

    except Exception as e:
        print("Genral Error", str(e))
        return None