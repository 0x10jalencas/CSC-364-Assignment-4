import socket
import threading

from models import (
    FileOfferMessage,
    FileLookupMessage,
    PeerListMessage,
    AcknowledgmentMessage,
    ErrorMessage
)
from wire import receive_message, send_message


HOST = "127.0.0.1"
PORT = 8000

file_registry = {}
registry_lock = threading.Lock()


def register_file(message: FileOfferMessage) -> None:
    peer_info = {
        "peer_id": message.peer_id,
        "host": message.host,
        "port": message.port,
    }

    with registry_lock:
        if message.file_name not in file_registry:
            file_registry[message.file_name] = []

        already_registered = False

        for peer in file_registry[message.file_name]:
            if peer["host"] == message.host and peer["port"] == message.port:
                already_registered = True

        if not already_registered:
            file_registry[message.file_name].append(peer_info)


def lookup_file(file_name: str) -> list[dict]:
    with registry_lock:
        return file_registry.get(file_name, [])


def handle_connection(connection: socket.socket) -> None:
    try:
        message = receive_message(connection)

        if isinstance(message, FileOfferMessage):
            register_file(message)

            response = AcknowledgmentMessage(
                peer_id=message.peer_id,
                chunk_number=0
            )

            send_message(connection, response)
            print(f"Registered {message.file_name} from peer {message.peer_id}")

        elif isinstance(message, FileLookupMessage):
            peers = lookup_file(message.file_name)

            response = PeerListMessage(
                file_name=message.file_name,
                peers=peers
            )

            send_message(connection, response)
            print(f"Lookup for {message.file_name}: {peers}")

        else:
            response = ErrorMessage(error="Unsupported message type")
            send_message(connection, response)

    finally:
        connection.close()


def start_tracker() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Tracker listening on {HOST}:{PORT}")

    while True:
        connection, address = server_socket.accept()

        thread = threading.Thread(
            target=handle_connection,
            args=(connection,)
        )

        thread.start()


if __name__ == "__main__":
    start_tracker()