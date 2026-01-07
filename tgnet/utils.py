import struct
from hashlib import sha1


def make_auth_key_id(key: bytes | None) -> int:
    if not key:
        return 0

    sha = sha1(key).digest()
    return struct.unpack("q", sha[-8:])[0]
