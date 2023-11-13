from __future__ import annotations

from dataclasses import dataclass

from tgnet.native_byte_buffer import NativeByteBuffer


@dataclass
class Salt:
    salt_valid_since: int
    salt_valid_until: int
    salt: int

    @classmethod
    def deserialize(cls, buffer: NativeByteBuffer) -> Salt:
        salt_valid_since = buffer.readInt32()
        salt_valid_until = buffer.readInt32()
        salt = buffer.readInt64()

        return cls(salt_valid_since, salt_valid_until, salt)

    def serialize(self, buffer: NativeByteBuffer) -> None:
        buffer.writeInt32(self.salt_valid_since)
        buffer.writeInt32(self.salt_valid_until)
        buffer.writeInt64(self.salt)
