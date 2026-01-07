from __future__ import annotations

from dataclasses import dataclass

from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class AuthCredentials:
    auth_key_perm: bytes | None
    auth_key_perm_id: int | None
    auth_key_temp: bytes | None
    auth_key_temp_id: int | None
    auth_key_media_temp: bytes | None
    auth_key_media_temp_id: int | None
    authorized: int

    @classmethod
    def deserialize(cls, buffer: TgnetReader, version: int) -> AuthCredentials:
        auth_key_perm = None
        auth_key_perm_id = None
        auth_key_temp = None
        auth_key_temp_id = None
        auth_key_media_temp = None
        auth_key_media_temp_id = None

        auth_key_perm_len = buffer.read_uint32()
        if auth_key_perm_len != 0:
            auth_key_perm = buffer.read_raw_bytes(auth_key_perm_len)

        if version >= 4:
            auth_key_perm_id = buffer.read_int64()
        else:
            len_of_bytes = buffer.read_uint32()
            if len_of_bytes != 0:
                auth_key_perm_id = buffer.read_int64()

        if version >= 8:
            len_of_bytes = buffer.read_uint32()
            if len_of_bytes != 0:
                auth_key_temp = buffer.read_raw_bytes(len_of_bytes)
            auth_key_temp_id = buffer.read_int64()

        if version >= 12:
            len_of_bytes = buffer.read_uint32()
            if len_of_bytes != 0:
                auth_key_media_temp = buffer.read_raw_bytes(len_of_bytes)
            auth_key_media_temp_id = buffer.read_int64()

        authorized = buffer.read_int32()

        return cls(
            auth_key_perm=auth_key_perm,
            auth_key_perm_id=auth_key_perm_id,
            auth_key_temp=auth_key_temp,
            auth_key_temp_id=auth_key_temp_id,
            auth_key_media_temp=auth_key_media_temp,
            auth_key_media_temp_id=auth_key_media_temp_id,
            authorized=authorized,
        )

    def serialize(self, buffer: TgnetReader, version: int) -> None:
        buffer.write_uint32(len(self.auth_key_perm) if self.auth_key_perm else 0)
        if self.auth_key_perm:
            buffer.write_raw_bytes(self.auth_key_perm)

        if version >= 4:
            buffer.write_int64(self.auth_key_perm_id)
        else:
            if self.auth_key_perm_id:
                buffer.write_uint32(8)
                buffer.write_int64(self.auth_key_perm_id)
            else:
                buffer.write_uint32(0)

        if version >= 8:
            if self.auth_key_temp:
                buffer.write_uint32(len(self.auth_key_temp))
                buffer.write_raw_bytes(self.auth_key_temp)
            else:
                buffer.write_uint32(0)
            buffer.write_int64(self.auth_key_temp_id)

        if version >= 12:
            if self.auth_key_media_temp:
                buffer.write_uint32(len(self.auth_key_media_temp))
                buffer.write_raw_bytes(self.auth_key_media_temp)
            else:
                buffer.write_uint32(0)
            buffer.write_int64(self.auth_key_media_temp_id)

        buffer.write_int32(self.authorized)
