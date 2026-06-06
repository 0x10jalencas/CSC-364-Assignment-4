# CSC-364 Assignment 4: P2P NFS

Simple peer-to-peer file sharing system in Python. Peers register shared files with a tracker, look up files, and download files directly from other peers using TCP sockets.

## Files

- `tracker.py`: file discovery server
- `peer.py`: shares files from `shared/`
- `request_file.py`: downloads files into `downloads/`
- `models.py`, `protocols.py`, `wire.py`: messages, protocol helpers, and socket encoding

## Run

Start the tracker:

```bash
python3 tracker.py
```

Start a peer:

```bash
python3 peer.py --port 9002
```

Request a file:

```bash
python3 request_file.py --file hello.txt
```

## Verify

```bash
python3 -c "print('A' * 5000)" > shared/big.txt
python3 request_file.py --file big.txt
diff shared/big.txt downloads/big.txt
```

If `diff` prints nothing, the transfer was successful.

## Notes

Files are transferred in 1024-byte chunks. Each chunk is acknowledged and checked with a SHA-256 checksum.
