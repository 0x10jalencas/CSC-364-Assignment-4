import json
import socket
import struct

from models import (
    FileOfferMessage,
    FileRequestMessage,
    FileTransferMessage,
    AcknowledgmentMessage,
    FileLookupMessage,
    PeerListMessage,
    ErrorMessage,
    MessageType
)


def encode_message(message) -> bytes:
    message_type = message.message_type.value.encode("utf-8")

    if isinstance(message, FileOfferMessage):
        header = {
            "peer_id": message.peer_id,
            "file_name": message.file_name,
            "host": message.host,
            "port": message.port
        }
        payload = b""
    
    elif isinstance(message, FileRequestMessage):
        header = {
            "file_name": message.file_name
        }
        payload = b""

    elif isinstance(message, FileTransferMessage):
        header = {
            "chunk_number": message.chunk_number,
            "checksum": message.checksum
        }
        payload = message.file_data
    
    elif isinstance(message, AcknowledgmentMessage):
        header = {
            "peer_id": message.peer_id,
            "chunk_number": message.chunk_number
        }
        payload = b""

    elif isinstance(message, FileLookupMessage):
        header = {
            "file_name": message.file_name
        }
        payload = b""

    elif isinstance(message, PeerListMessage):
        header = {
            "file_name": message.file_name,
            "peers": message.peers
        }
        payload = b""

    elif isinstance(message, ErrorMessage):
        header = {
            "error": message.error
        }
        payload = b""
    
    else:
        raise ValueError(f"Unsupported message type: {type(message)}")

    header["payload_size"] = len(payload)

    header_bytes = json.dumps(header).encode("utf-8")
    header_size = struct.pack("!I", len(header_bytes))

    return message_type + header_size + header_bytes + payload


def decode_message(packet: bytes):
    message_type = packet[0:1].decode("utf-8")

    header_size = struct.unpack("!I", packet[1:5])[0]

    header_start = 5
    header_end = header_start + header_size

    header_bytes = packet[header_start:header_end]
    header = json.loads(header_bytes.decode("utf-8"))

    payload = packet[header_end:]

    if message_type == MessageType.OFFER.value:
        return FileOfferMessage(
            peer_id=header["peer_id"],
            file_name=header["file_name"],
            host=header["host"],
            port=header["port"],
        )
    
    if message_type == MessageType.REQUEST.value:
        return FileRequestMessage(
            file_name=header["file_name"],
        )

    if message_type == MessageType.TRANSFER.value:
        return FileTransferMessage(
            file_data=payload,
            chunk_number=header["chunk_number"],
            checksum=header["checksum"],
        )

    if message_type == MessageType.ACKNOWLEDGMENT.value:
        return AcknowledgmentMessage(
            peer_id=header["peer_id"],
            chunk_number=header["chunk_number"],
        )
    
    if message_type == MessageType.LOOKUP.value:
        return FileLookupMessage(
            file_name=header["file_name"],
        )

    if message_type == MessageType.PEER_LIST.value:
        return PeerListMessage(
            file_name=header["file_name"],
            peers=header["peers"],
        )

    if message_type == MessageType.ERROR.value:
        return ErrorMessage(
            error=header["error"],
        )

    raise ValueError(f"Unknown message type: {message_type}")


def receive_exactly(sock: socket.socket, num_bytes: int) -> bytes:
    data = b""

    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))

        if not chunk:
            raise ConnectionError("Socket closed before enough data was received.")

        data += chunk

    return data


def send_message(sock: socket.socket, message) -> None:
    packet = encode_message(message)
    sock.sendall(packet)


def receive_message(sock: socket.socket):
    message_type = receive_exactly(sock, 1)

    header_size_bytes = receive_exactly(sock, 4)
    header_size = struct.unpack("!I", header_size_bytes)[0]

    header_bytes = receive_exactly(sock, header_size)
    header = json.loads(header_bytes.decode("utf-8"))

    payload_size = header.get("payload_size", 0)
    payload = receive_exactly(sock, payload_size) if payload_size > 0 else b""

    packet = message_type + header_size_bytes + header_bytes + payload

    return decode_message(packet)