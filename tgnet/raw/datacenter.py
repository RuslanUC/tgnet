from __future__ import annotations

from dataclasses import dataclass

from tgnet.raw.auth import AuthCredentials
from tgnet.raw.ip import IP
from tgnet.raw.salt import Salt
from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class Datacenter:
    current_version: int
    datacenter_id: int
    last_init_version: int
    last_init_media_version: int | None

    ips: list[list[IP]]
    is_cdn: bool

    auth: AuthCredentials
    salt: list[Salt]
    salt_media: list[Salt]

    @classmethod
    def deserialize(cls, buffer: TgnetReader) -> Datacenter:
        current_version = buffer.read_uint32()
        datacenter_id = buffer.read_uint32()

        last_init_version = buffer.read_uint32() if current_version >= 3 else None
        last_init_media_version = buffer.read_uint32() if current_version >= 10 else None

        ips = [[], [], [], []]
        for b in range(4 if current_version >= 5 else 1):
            ip_array = ips[b]

            ip_count = buffer.read_uint32()
            for _ in range(ip_count):
                ip_array.append(IP.deserialize(buffer, current_version))

        is_cdn = buffer.read_bool() if current_version >= 6 else None

        auth = AuthCredentials.deserialize(buffer, current_version)

        salt_count = buffer.read_uint32()
        salt = [Salt.deserialize(buffer) for _ in range(salt_count)]
        salt_media = None

        if current_version >= 13:
            salt_count = buffer.read_uint32()
            salt_media = [Salt.deserialize(buffer) for _ in range(salt_count)]

        return cls(
            current_version=current_version,
            datacenter_id=datacenter_id,
            last_init_version=last_init_version,
            last_init_media_version=last_init_media_version,
            ips=ips,
            is_cdn=is_cdn,
            auth=auth,
            salt=salt,
            salt_media=salt_media,
        )

    def serialize(self, buffer: TgnetReader) -> None:
        buffer.write_uint32(self.current_version)
        buffer.write_uint32(self.datacenter_id)
        if self.current_version >= 3:
            buffer.write_uint32(self.last_init_version)
        if self.current_version >= 10:
            buffer.write_uint32(self.last_init_media_version)

        for i in range(4 if self.current_version >= 5 else 1):
            buffer.write_uint32(len(self.ips[i]))
            for ip in self.ips[i]:
                ip.serialize(buffer, self.current_version)

        if self.current_version >= 6:
            buffer.write_bool(self.is_cdn)

        self.auth.serialize(buffer, self.current_version)

        buffer.write_uint32(len(self.salt))
        for salt in self.salt:
            salt.serialize(buffer)

        if self.current_version >= 13:
            buffer.write_uint32(len(self.salt_media))
            for salt in self.salt_media:
                salt.serialize(buffer)
