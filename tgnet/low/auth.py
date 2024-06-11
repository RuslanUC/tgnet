from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tgnet.low.tgnet_reader import TgnetReader


@dataclass
class AuthCredentials:
    authKeyPerm: Optional[bytes]
    authKeyPermId: Optional[int]
    authKeyTemp: Optional[bytes]
    authKeyTempId: Optional[int]
    authKeyMediaTemp: Optional[bytes]
    authKeyMediaTempId: Optional[int]
    authorized: int

    @classmethod
    def deserialize(cls, buffer: TgnetReader, version: int) -> AuthCredentials:
        authKeyPerm = None
        authKeyPermId = None
        authKeyTemp = None
        authKeyTempId = None
        authKeyMediaTemp = None
        authKeyMediaTempId = None

        authKeyPermSize = buffer.readUint32()
        if authKeyPermSize != 0:
            authKeyPerm = buffer.readBytes(authKeyPermSize)

        if version >= 4:
            authKeyPermId = buffer.readInt64()
        else:
            len_of_bytes = buffer.readUint32()
            if len_of_bytes != 0:
                authKeyPermId = buffer.readInt64()

        if version >= 8:
            len_of_bytes = buffer.readUint32()
            if len_of_bytes != 0:
                authKeyTemp = buffer.readBytes(len_of_bytes)
            authKeyTempId = buffer.readInt64()

        if version >= 12:
            len_of_bytes = buffer.readUint32()
            if len_of_bytes != 0:
                authKeyMediaTemp = buffer.readBytes(len_of_bytes)
            authKeyMediaTempId = buffer.readInt64()

        authorized = buffer.readInt32()

        return cls(authKeyPerm, authKeyPermId, authKeyTemp, authKeyTempId, authKeyMediaTemp, authKeyMediaTempId,
                   authorized)

    def serialize(self, buffer: TgnetReader, version: int) -> None:
        buffer.writeUint32(len(self.authKeyPerm) if self.authKeyPerm else 0)
        if self.authKeyPerm:
            buffer.writeBytes(self.authKeyPerm)

        if version >= 4:
            buffer.writeInt64(self.authKeyPermId)
        else:
            if self.authKeyPermId:
                buffer.writeUint32(8)
                buffer.writeInt64(self.authKeyPermId)
            else:
                buffer.writeUint32(0)

        if version >= 8:
            if self.authKeyTemp:
                buffer.writeUint32(len(self.authKeyTemp))
                buffer.writeBytes(self.authKeyTemp)
            else:
                buffer.writeUint32(0)
            buffer.writeInt64(self.authKeyTempId)

        if version >= 12:
            if self.authKeyMediaTemp:
                buffer.writeUint32(len(self.authKeyMediaTemp))
                buffer.writeBytes(self.authKeyMediaTemp)
            else:
                buffer.writeUint32(0)
            buffer.writeInt64(self.authKeyMediaTempId)

        buffer.writeInt32(self.authorized)
