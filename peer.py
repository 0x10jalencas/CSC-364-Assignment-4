import os
import socket
from dataclasses import dataclass

from protocols import PeerRegistration, generate_peer_id, FileTransfer, ErrorHandling
from models import FileOfferMessage, FileRequestMessage, AcknowledgmentMessage
from wire import receive_message, send_message

@dataclass
class Peer:
    host: str
    port: int
    peer_id: int
    shared_folder: str = "shared"
    download_folder: str = "downloads"

    def setup_folders(self) -> None:
        os.makedirs(self.shared_folder, exist_ok=True)
        os.makedirs(self.download_folder, exist_ok=True)

    def get_shared_files(self) -> list[str]:
        shared_files = []

        for file_name in os.listdir(self.shared_folder):
            file_path = os.path.join(self.shared_folder, file_name)

            if os.path.isfile(file_path):
                shared_files.append(file_name)

        return shared_files

    def create_registration_messages(self) -> list[FileOfferMessage]:
        shared_files = self.get_shared_files()

        registration = PeerRegistration(
            peer_id=self.peer_id,
            host=self.host,
            port=self.port,
            shared_files=shared_files
        )
    
        return registration.create_offer_messages()

    def register_with_tracker(self, tracker_host: str = "127.0.0.1", tracker_port: int = 8000) -> None:
        registration_messages = self.create_registration_messages()

        for message in registration_messages:
            tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tracker_socket.connect((tracker_host, tracker_port))

            send_message(tracker_socket, message)

            response = receive_message(tracker_socket)
            print("Tracker response:", response)

            tracker_socket.close()
    
    def handle_connection(self, connection: socket.socket) -> None:
        message = receive_message(connection)
        print("Received message:", message)

        if isinstance(message, FileRequestMessage):
            self.send_requested_file(connection, message.file_name)

    def send_requested_file(self, connection: socket.socket, file_name: str) -> None:
        file_path = os.path.join(self.shared_folder, file_name)

        if not os.path.isfile(file_path):
            print(f"File not found: {file_name}")
            return

        with open(file_path, "rb") as file:
            file_data = file.read()

        transfer = FileTransfer(file_name=file_name)
        transfer_messages = transfer.create_transfer_messages(file_data)

        error_handler = ErrorHandling(peer_id=self.peer_id)
        connection.settimeout(error_handler.timeout_seconds)

        for transfer_message in transfer_messages:
            ack_received = False
            retries_so_far = 0

            while not ack_received and retries_so_far < error_handler.max_retries:
                send_message(connection, transfer_message)

                try:
                    ack_message = receive_message(connection)

                    if (
                        isinstance(ack_message, AcknowledgmentMessage)
                        and ack_message.chunk_number == transfer_message.chunk_number
                    ):
                        ack_received = True
                        print(f"Chunk {transfer_message.chunk_number} acknowledged")

                    else:
                        retries_so_far += 1
                        print(f"Bad ACK for chunk {transfer_message.chunk_number}")

                except socket.timeout:
                    retries_so_far += 1
                    print(f"Timeout waiting for ACK for chunk {transfer_message.chunk_number}")

            if not ack_received:
                print(f"Failed to send chunk {transfer_message.chunk_number}")
                return

        print(f"Finished sending {file_name}")

    def start_server(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"Peer {self.peer_id} listening on {self.host}:{self.port}")

        while True:
            connection, address = server_socket.accept()

            print(f"Connection from {address}")

            try:
                self.handle_connection(connection)
            finally:
                connection.close()


# Testing
if __name__ == "__main__":
    peer = Peer(
        host="127.0.0.1",
        port=9001,
        peer_id=generate_peer_id()
    )

    peer.setup_folders()
    
    print("Peer ID:", peer.peer_id)
    print("Host:", peer.host)
    print("Port:", peer.port)
    print("Shared files:", peer.get_shared_files())
    print("Registration messages:", peer.create_registration_messages())

    peer.register_with_tracker()

    peer.start_server()