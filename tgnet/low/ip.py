from __future__ import annotations

from dataclasses import dataclass

from tgnet.low.tgnet_reader import TgnetReader


@dataclass
class IP:
    address: str
    port: int
    flags: int
    secret: str

    @classmethod
    def deserialize(cls, buffer: TgnetReader, version: int) -> IP:
        address = buffer.readString()
        port = buffer.readUint32()
        flags = buffer.readInt32() if version >= 7 else 0

        secret = None
        if version >= 11:
            secret = buffer.readString()
        elif version >= 9:
            secret = buffer.readString()
            if secret:
                size = len(secret) // 2
                result = bytearray(size)
                for i in range(size):
                    result[i] = int(secret[i * 2:i * 2 + 2], 16)
                secret = result.decode('utf-8')

        return cls(address, port, flags, secret)

    def serialize(self, buffer: TgnetReader, version: int) -> None:
        buffer.writeString(self.address)
        buffer.writeUint32(self.port)
        buffer.writeInt32(self.flags)

        if version >= 11:
            buffer.writeString(self.secret)
        elif version >= 9 and self.secret:
            result = self.secret.encode('utf-8')
            size = len(result)
            output = ""
            for i_ in range(size):
                output += format(result[i_], '02x')
            buffer.writeString(output)
