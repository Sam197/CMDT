import socket
from clientConfig import *        # pylint: disable=W0614
from config import SERVER_CLIENT_ENABLED
from tkinter import messagebox
import errno
from classes import Line, TiledAtom, Tile

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

def recv_msg(msg, grid, entities):
    if msg[0] == "T":
        curObj = msg
        newObj = TiledAtom(int(curObj[1]), int(curObj[2]), curObj[3])
        grid[newObj.gridY][newObj.gridX] = newObj
    elif msg[0] == "L":
        entities.append(Line((int(msg[1]),int(msg[2])), (int(msg[3]),int(msg[4])), int(msg[5])))
    elif msg[0] == "TE":
        newObj = Tile(int(msg[1]), int(msg[2]))
        grid[newObj.gridY][newObj.gridX] = newObj
    elif msg[0] == "LE" or "LB":
        for obj in entities:
            sPos = (int(msg[1]), int(msg[2]))
            ePos = (int(msg[3]), int(msg[4]))
            if obj.startPos == sPos and obj.endPos == ePos:
                if msg[0] == "LE":
                    entities.remove(obj)
                elif msg[0] == "LB":
                    obj.update_Bond_Number()
                break

    return grid, entities

def bulk_send(outList):
    pass

# def msg_to_list(msg):
#     return msg.split("/")

def update():
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
            print("Connection closed by sever")
        message_length = int(message_header.decode(protocol).strip())
        message = client_socket.recv(message_length).decode(protocol)
        return message.split("-")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            if e.errno == errno.ECONNRESET:
                print("Server closed connection")
            print("Reading Error", str(e))
        return None

    except Exception as e:
        print("Genral Error", str(e))
        return None