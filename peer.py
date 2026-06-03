import os
from dataclasses import dataclass

from protocols import PeerRegistration, generate_peer_id
from models import FileOfferMessage

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
            shared_files=shared_files
        )

        return registration.create_offer_messages()
    
