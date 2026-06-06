from dataclasses import dataclass
from enum import Enum


class MessageType(str, Enum):
    OFFER = "O"
    REQUEST = "R"
    TRANSFER = "T"
    ACKNOWLEDGMENT = "A"
    LOOKUP = "L"
    PEER_LIST = "P"
    ERROR = "E"


@dataclass
class FileOfferMessage:
    peer_id: int
    file_name: str
    host: str
    port: int
    message_type: MessageType = MessageType.OFFER


@dataclass
class FileRequestMessage:
    file_name: str
    message_type: MessageType = MessageType.REQUEST


@dataclass
class FileTransferMessage:
    file_data: bytes
    chunk_number: int
    checksum: str
    message_type: MessageType = MessageType.TRANSFER


@dataclass
class AcknowledgmentMessage:
    peer_id: int
    chunk_number: int
    message_type: MessageType = MessageType.ACKNOWLEDGMENT


@dataclass
class FileLookupMessage:
    file_name: str
    message_type: MessageType = MessageType.LOOKUP


@dataclass
class PeerListMessage:
    file_name: str
    peers: list[dict]
    message_type: MessageType = MessageType.PEER_LIST


@dataclass
class ErrorMessage:
    error: str
    message_type: MessageType = MessageType.ERROR