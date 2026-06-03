from dataclasses import dataclass
from enum import Enum

class MessageType(str, Enum):
    OFFER = "O"
    REQUEST = "R"
    TRANSFER = "T"
    ACKNOWLEDGMENT = "A"

@dataclass
class FileOfferMessage:
    peer_id: int
    file_name: str
    message_type: MessageType = MessageType.OFFER

@dataclass
class FileRequestMessage:
    file_data: bytes
    message_type: MessageType = MessageType.REQUEST

@dataclass
class FileTransferMessage:
    file_data: bytes
    chunk_number: int
    message_type: MessageType = MessageType.TRANSFER

@dataclass
class AcknowledgmentMessage:
    peer_id: int
    message_type: MessageType = MessageType.ACKNOWLEDGMENT