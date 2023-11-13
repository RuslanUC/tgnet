"""
NativeByteBuffer class is a full copy of telegram's class NativeByteBuffer
https://github.com/DrKLO/Telegram/blob/master/TMessagesProj/jni/tgnet/NativeByteBuffer.cpp

Creator https://github.com/batreller/
Code https://github.com/batreller/telegram_android_session_converter
"""

import struct
from typing import Optional


class NativeByteBuffer:
    def __init__(self, bytes_: bytes):
        self.buffer = bytearray(bytes_)
        self._position = 0
        self._limit = len(self.buffer)

    def writeByteArray(self, b: bytes, offset: int=0, length: int=None) -> None:
        #if b"\x14\x00" in b:
        #    raise Exception
        length = length or len(b)
        self.buffer[self._position:self._position + length] = b[offset:offset + length]
        self._position += length

    def writeDouble(self, d: float) -> None:
        value = struct.pack("d", d)
        self.writeByteArray(value)

    def writeInt32(self, x: int) -> None:
        value = struct.pack("<i", x)
        self.writeByteArray(value)

    def writeInt64(self, x: int) -> None:
        value = struct.pack("q", x)
        self.writeByteArray(value)

    def writeBool(self, value: bool) -> None:
        # bytearray(b'\xb5ur\x99') for True
        # bytearray(b'7\x97y\xbc') for False
        constructor = bytearray(b'\xb5ur\x99') if value else bytearray(b'7\x97y\xbc')
        self.writeByteArray(constructor)

    def writeBytes(self, b: bytes, offset: int=0, length: int=None) -> None:
        self.writeByteArray(b, offset, length)

    def writeByte(self, i: int) -> None:
        self.buffer[self._position] = i
        self._position += 1

    def writeString(self, s: str) -> None:
        s = s.encode("utf-8")
        if len(s) <= 253:
            self.writeByte(len(s))
        else:
            if self._position + 4 > self._limit:
                return
            self.writeByte(254)
            self.writeByte(len(s) % 256)
            self.writeByte(len(s) >> 8)
            self.writeByte(len(s) >> 16)

        if self._position + len(s) > self._limit:
            return
        self.writeByteArray(s)

        addition = (len(s) + (1 if len(s) <= 253 else 4)) % 4
        if addition != 0:
            addition = 4 - addition
        if self._position + addition > self._limit:
            return

        for a in range(addition):
            self.writeByte(0)
        #self.writeByteArray(s)
        #self.writeUint32(len(s))
        #sl = 1
        #l = len(s)
        #if l >= 254:
        #    self.writeByte(254)
        #    self.writeUint32(l)
        #    sl = 4
        #else:
        #    self.writeByte(l)
        #addition = (l + sl) % 4
        #if addition != 0:
        #    addition = 4 - addition
        #self.writeByteArray(s)
        #self._position += addition

    def writeUint32(self, x: int) -> None:
        value = struct.pack("<I", x)
        self.writeByteArray(value)

    def readInt32(self) -> int:
        # print(int.from_bytes(self.buffer[self._position:self._position+4], 'little'))
        result = struct.unpack_from("<i", self.buffer, self._position)[0]
        self._position += 4
        return result

    def readUint32(self) -> int:
        result = struct.unpack_from("<I", self.buffer, self._position)[0]
        self._position += 4
        return result

    def readInt64(self) -> int:
        result = struct.unpack_from("q", self.buffer, self._position)[0]
        self._position += 8
        return result

    def readBool(self) -> bool:
        constructor = self.readBytes(4)
        # bytearray(b'\xb5ur\x99') for True
        # bytearray(b'7\x97y\xbc') for False
        return constructor == bytearray(b'\xb5ur\x99')

    def readBytes(self, length: int) -> Optional[bytes]:
        if length > self._limit - self._position:
            return None
        result = self.buffer[self._position: self._position + length]
        self._position += length
        return result

    def readString(self) -> str:
        sl = 1
        if self._position + 1 > self._limit:
            return ""

        l = self.buffer[self._position]
        self._position += 1

        if l >= 254:
            if self._position + 3 > self._limit:
                return ""
            l = self.buffer[self._position] | (self.buffer[self._position + 1] << 8) | (
                    self.buffer[self._position + 2] << 16)
            self._position += 3
            sl = 4
        addition = (l + sl) % 4
        if addition != 0:
            addition = 4 - addition
        if self._position + l + addition > self._limit:
            return ""
        result = self.buffer[self._position: self._position + l].decode()
        self._position += l + addition
        return result
