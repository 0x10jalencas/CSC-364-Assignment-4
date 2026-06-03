from dataclasses import dataclass
from enum import Enum

@dataclass
class MessageType(str, Enum):
    OFFER = "O"
    REQUEST = "R"
    TRANSFER = "T"
    ACKNOWLEDGMENT = "A"

@dataclass
class FileOfferMessage:
    message_type: MessageType = MessageType.OFFER
    peer_id: int
    file_name: str

@dataclass
class FileRequestMessage:
    message_type: MessageType = MessageType.REQUEST
    file_data: bytes

@dataclass
class FileTransferMessage:
    message_type: MessageType = MessageType.TRANSFER
    file_data: bytes

@dataclass
class AcknowledgementMessage:
    message_type: MessageType = MessageType.ACKNOWLEDGMENT
    peer_id: int