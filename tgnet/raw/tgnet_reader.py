import struct
from io import BytesIO
from os import PathLike
from typing import BinaryIO


class TgnetReader:
    def __init__(self, bytes_: bytes | bytearray | str | PathLike | BinaryIO):
        self.buffer = BytesIO(bytes_) if isinstance(bytes_, (bytes, bytearray)) else bytes_

    def _write_raw_bytes(self, b: bytes) -> None:
        self.buffer.write(b)

    def write_int32(self, x: int) -> None:
        self._write_raw_bytes(struct.pack("<i", x))

    def write_int64(self, x: int) -> None:
        self._write_raw_bytes(struct.pack("q", x))

    def write_bool(self, value: bool) -> None:
        constructor = bytearray(b"\xb5ur\x99") if value else bytearray(b"7\x97y\xbc")
        self._write_raw_bytes(constructor)

    def write_raw_bytes(self, b: bytes) -> None:
        self._write_raw_bytes(b)

    def write_byte(self, i: int) -> None:
        self.buffer.write(bytes([i]))

    def writeString(self, s: str) -> None:
        s = s.encode("utf-8")
        if len(s) <= 253:
            self.write_byte(len(s))
        else:
            self.write_byte(254)
            self.write_byte(len(s) % 256)
            self.write_byte(len(s) >> 8)
            self.write_byte(len(s) >> 16)

        self._write_raw_bytes(s)

        padding = (len(s) + (1 if len(s) <= 253 else 4)) % 4
        if padding != 0:
            padding = 4 - padding

        for a in range(padding):
            self.write_byte(0)

    def write_uint32(self, x: int) -> None:
        value = struct.pack("<I", x)
        self._write_raw_bytes(value)

    def read_int32(self) -> int:
        return struct.unpack_from("<i", self.buffer.read(4))[0]

    def read_uint32(self) -> int:
        return struct.unpack_from("<I", self.buffer.read(4))[0]

    def read_int64(self) -> int:
        return struct.unpack_from("q", self.buffer.read(8))[0]

    def read_bool(self) -> bool:
        constructor = self.read_raw_bytes(4)
        # bytearray(b'\xb5ur\x99') for True
        # bytearray(b'7\x97y\xbc') for False
        return constructor == b"\xb5ur\x99"

    def read_raw_bytes(self, length: int) -> bytes | None:
        return self.buffer.read(length)

    def read_string(self) -> str:
        sl = 1
        length = self.buffer.read(1)[0]

        if length >= 254:
            l_ = self.buffer.read(3)
            length = l_[0] | (l_[1] << 8) | l_[2] << 16
            sl = 4

        padding = (length + sl) % 4
        if padding != 0:
            padding = 4 - padding

        result = self.buffer.read(length).decode()
        self.buffer.read(padding)
        return result
