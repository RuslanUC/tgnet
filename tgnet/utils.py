import struct
from hashlib import sha1
from typing import Optional


def calcKeyId(key: Optional[bytes]) -> int:
    if not key:
        return 0

    sha = sha1(key).digest()
    return struct.unpack("q", sha[-8:])[0]
