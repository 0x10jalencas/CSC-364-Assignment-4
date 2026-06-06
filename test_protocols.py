from models import (
    FileOfferMessage,
    FileRequestMessage,
    FileTransferMessage,
    AcknowledgmentMessage,
)

from wire import encode_message, decode_message


messages = [
    FileOfferMessage(peer_id=1234, file_name="hello.txt"),
    FileRequestMessage(file_name="hello.txt"),
    FileTransferMessage(file_data=b"hello world", chunk_number=0),
    AcknowledgmentMessage(peer_id=5678, chunk_number=0),
]


for message in messages:
    packet = encode_message(message)
    decoded = decode_message(packet)

    print("Original:", message)
    print("Encoded: ", packet)
    print("Decoded: ", decoded)
    print()