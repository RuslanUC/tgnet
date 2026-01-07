from __future__ import annotations

from dataclasses import dataclass

from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class Salt:
    salt_valid_since: int
    salt_valid_until: int
    salt: int

    @classmethod
    def deserialize(cls, buffer: TgnetReader) -> Salt:
        salt_valid_since = buffer.read_int32()
        salt_valid_until = buffer.read_int32()
        salt = buffer.read_int64()

        return cls(
            salt_valid_since=salt_valid_since,
            salt_valid_until=salt_valid_until,
            salt=salt,
        )

    def serialize(self, buffer: TgnetReader) -> None:
        buffer.write_int32(self.salt_valid_since)
        buffer.write_int32(self.salt_valid_until)
        buffer.write_int64(self.salt)
