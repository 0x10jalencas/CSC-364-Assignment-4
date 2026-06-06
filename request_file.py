import argparse
import hashlib
import os
import socket

from protocols import ErrorHandling, generate_peer_id
from models import (
    FileLookupMessage,
    FileRequestMessage,
    FileTransferMessage,
    PeerListMessage
)
from wire import send_message, receive_message


def lookup_file(file_name: str, tracker_host: str, tracker_port: int) -> list[dict]:
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.connect((tracker_host, tracker_port))

    lookup_message = FileLookupMessage(file_name=file_name)
    send_message(tracker_socket, lookup_message)

    response = receive_message(tracker_socket)
    tracker_socket.close()

    if isinstance(response, PeerListMessage):
        return response.peers

    return []


def download_file(peer: dict, file_name: str, download_folder: str) -> None:
    peer_id = generate_peer_id()
    error_handler = ErrorHandling(peer_id=peer_id)

    os.makedirs(download_folder, exist_ok=True)

    download_path = os.path.join(download_folder, file_name)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((peer["host"], peer["port"]))

    request_message = FileRequestMessage(file_name=file_name)
    send_message(client_socket, request_message)

    with open(download_path, "wb") as file:
        while True:
            try:
                message = receive_message(client_socket)

                if isinstance(message, FileTransferMessage):
                    actual_checksum = hashlib.sha256(message.file_data).hexdigest()

                    if actual_checksum != message.checksum:
                        print(f"Checksum failed for chunk {message.chunk_number}")
                        continue

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--download-folder", default="downloads")
    parser.add_argument("--tracker-host", default="127.0.0.1")
    parser.add_argument("--tracker-port", type=int, default=8000)
    args = parser.parse_args()

    peers = lookup_file(
        file_name=args.file,
        tracker_host=args.tracker_host,
        tracker_port=args.tracker_port
    )

    if not peers:
        print(f"No peers found with {args.file}")
    else:
        download_file(
            peer=peers[0],
            file_name=args.file,
            download_folder=args.download_folder
        )