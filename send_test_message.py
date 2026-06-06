import socket

from models import FileRequestMessage
from wire import send_message


HOST = "127.0.0.1"
PORT = 9001


message = FileRequestMessage(file_name="hello.txt")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

send_message(client_socket, message)

client_socket.close()