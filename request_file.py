import os
import socket


import argparse
from protocols import ErrorHandling, generate_peer_id
from models import FileRequestMessage, FileTransferMessage
from wire import send_message, receive_message


parser = argparse.ArgumentParser()
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--file", required=True)
parser.add_argument("--download-folder", default="downloads")
args = parser.parse_args()

HOST = args.host
PORT = args.port
FILE_NAME = args.file
DOWNLOAD_FOLDER = args.download_folder

peer_id = generate_peer_id()
error_handler = ErrorHandling(peer_id=peer_id)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_path = os.path.join(DOWNLOAD_FOLDER, FILE_NAME)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

request_message = FileRequestMessage(file_name=FILE_NAME)
send_message(client_socket, request_message)

with open(download_path, "wb") as file:
    while True:
        try:
            message = receive_message(client_socket)

            if isinstance(message, FileTransferMessage):
                file.write(message.file_data)

                ack_message = error_handler.create_acknowledgment_message(
                    chunk_number=message.chunk_number
                )

                send_message(client_socket, ack_message)

                print(f"Received chunk {message.chunk_number}")

        except ConnectionError:
            break

client_socket.close()

print(f"Downloaded file saved to {download_path}")