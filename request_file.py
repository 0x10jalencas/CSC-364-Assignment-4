import os
import socket


import argparse
from protocols import ErrorHandling, generate_peer_id
from models import FileLookupMessage, FileRequestMessage, FileTransferMessage, PeerListMessage
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
peers = lookup_file(FILE_NAME)

if not peers:
    print(f"No peers found with {FILE_NAME}")
    exit()
client_socket.connect((HOST, PORT))

request_message = FileRequestMessage(file_name=FILE_NAME)
send_message(client_socket, request_message)

def lookup_file(file_name: str) -> list[dict]:
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.connect((TRACKER_HOST, TRACKER_PORT))

    lookup_message = FileLookupMessage(file_name=file_name)
    send_message(tracker_socket, lookup_message)

    response = receive_message(tracker_socket)
    tracker_socket.close()

    if isinstance(response, PeerListMessage):
        return response.peers

    return []


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