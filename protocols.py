from dataclasses import dataclass
from models import (
    MessageType,
    FileOfferMessage,
    FileRequestMessage,
    FileTransferMessage,
    AcknowledgmentMessage,
)

from enum import Enum
import random


@dataclass
class PeerRegistration:
    peer_id: int
    shared_files: list[str]

    def create_offer_message(self) -> list[FileOfferMessage]:
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

        for start in range(0, len(file_data), self.chunk_size):
            chunk = file_data[start:start + self.chunk_size]

            message = FileTransferMessage(
                file_data=chunk
            )
            messages.append(message)


@dataclass
class ErrorHandling:
    pass

# Peer Registration
PeerRegistration = []
peer_uid = random.randint(1, 2**32-1)
peer_uid = FileOfferMessage("Message")
