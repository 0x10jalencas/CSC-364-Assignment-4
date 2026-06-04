from dataclasses import dataclass
from models import (
    FileOfferMessage,
    FileRequestMessage,
    FileTransferMessage,
    AcknowledgmentMessage,
)

import random

@dataclass
class PeerRegistration:
    peer_id: int
    shared_files: list[str]

    def create_offer_messages(self) -> list[FileOfferMessage]:
        messages = []

        for file_name in self.shared_files:
            message = FileOfferMessage(
                peer_id=self.peer_id,
                file_name=file_name
            )
            messages.append(message)

        return messages


@dataclass
class FileLookup:
    file_name: str

    def create_request_message(self) -> FileRequestMessage:
        return FileRequestMessage(file_name=self.file_name)

@dataclass
class FileTransfer:
    file_name: str
    chunk_size: int = 1024

    def create_transfer_messages(self, file_data: bytes) -> list[FileTransferMessage]:
        messages = []
        chunk_number = 0


        for chunk_start in range(0, len(file_data), self.chunk_size):
            chunk_end = chunk_start + self.chunk_size
            chunk = file_data[chunk_start:chunk_end]

            message = FileTransferMessage(
                chunk_number=chunk_number,
                file_data=chunk
            )
            messages.append(message)
            chunk_number += 1
        
        return messages


@dataclass
class ErrorHandling:
    peer_id: int
    timeout_seconds: int = 5
    max_retries: int = 3

    def create_acknowledgment_message(self, chunk_number: int) -> AcknowledgmentMessage:
        return AcknowledgmentMessage(
            peer_id=self.peer_id,
            chunk_number=chunk_number
        )
    
    def should_retransmit(self, ack_received: bool, retries_so_far: int) -> bool:
        return not ack_received and retries_so_far < self.max_retries
    

def generate_peer_id() -> int:
    return random.randint(1, 2**32-1)