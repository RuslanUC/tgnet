import struct
from io import BytesIO
from os import PathLike
from typing import Optional, Union, BinaryIO


class TgnetReader:
    def __init__(self, bytes_: Union[bytes, bytearray, str, PathLike, BinaryIO]):
        self.buffer = BytesIO(bytes_) if isinstance(bytes_, (bytes, bytearray)) else bytes_

    def writeByteArray(self, b: bytes) -> None:
        self.buffer.write(b)

    def writeInt32(self, x: int) -> None:
        self.writeByteArray(struct.pack("<i", x))

    def writeInt64(self, x: int) -> None:
        self.writeByteArray(struct.pack("q", x))

    def writeBool(self, value: bool) -> None:
        constructor = bytearray(b'\xb5ur\x99') if value else bytearray(b'7\x97y\xbc')
        self.writeByteArray(constructor)

    def writeBytes(self, b: bytes) -> None:
        self.writeByteArray(b)

    def writeByte(self, i: int) -> None:
        self.buffer.write(i.to_bytes(1, "big"))

    def writeString(self, s: str) -> None:
        s = s.encode("utf-8")
        if len(s) <= 253:
            self.writeByte(len(s))
        else:
            self.writeByte(254)
            self.writeByte(len(s) % 256)
            self.writeByte(len(s) >> 8)
            self.writeByte(len(s) >> 16)

        self.writeByteArray(s)

        padding = (len(s) + (1 if len(s) <= 253 else 4)) % 4
        if padding != 0:
            padding = 4 - padding

        for a in range(padding):
            self.writeByte(0)

    def writeUint32(self, x: int) -> None:
        value = struct.pack("<I", x)
        self.writeByteArray(value)

    def readInt32(self) -> int:
        return struct.unpack_from("<i", self.buffer.read(4))[0]

    def readUint32(self) -> int:
        return struct.unpack_from("<I", self.buffer.read(4))[0]

    def readInt64(self) -> int:
        return struct.unpack_from("q", self.buffer.read(8))[0]

    def readBool(self) -> bool:
        constructor = self.readBytes(4)
        # bytearray(b'\xb5ur\x99') for True
        # bytearray(b'7\x97y\xbc') for False
        return constructor == bytearray(b'\xb5ur\x99')

    def readBytes(self, length: int) -> Optional[bytes]:
        return self.buffer.read(length)

    def readString(self) -> str:
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
