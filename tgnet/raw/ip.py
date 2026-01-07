from __future__ import annotations

from dataclasses import dataclass

from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class IP:
    address: str
    port: int
    flags: int
    secret: str

    @classmethod
    def deserialize(cls, buffer: TgnetReader, version: int) -> IP:
        address = buffer.read_string()
        port = buffer.read_uint32()
        flags = buffer.read_int32() if version >= 7 else 0

        secret = None
        if version >= 11:
            secret = buffer.read_string()
        elif version >= 9:
            secret = buffer.read_string()
            if secret:
                size = len(secret) // 2
                result = bytearray(size)
                for i in range(size):
                    result[i] = int(secret[i * 2:i * 2 + 2], 16)
                secret = result.decode("utf-8")

        return cls(
            address=address,
            port=port,
            flags=flags,
            secret=secret,
        )

    def serialize(self, buffer: TgnetReader, version: int) -> None:
        buffer.writeString(self.address)
        buffer.write_uint32(self.port)
        buffer.write_int32(self.flags)

        if version >= 11:
            buffer.writeString(self.secret)
        elif version >= 9 and self.secret:
            result = self.secret.encode("utf-8")
            size = len(result)
            output = ""
            for i_ in range(size):
                output += format(result[i_], "02x")
            buffer.writeString(output)
