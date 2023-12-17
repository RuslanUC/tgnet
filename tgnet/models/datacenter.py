from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tgnet.models.auth import AuthCredentials
from tgnet.models.ip import IP
from tgnet.models.salt import Salt
from tgnet.native_byte_buffer import NativeByteBuffer


@dataclass
class Datacenter:
    currentVersion: int
    datacenterId: int
    lastInitVersion: int
    lastInitMediaVersion: Optional[int]

    ips: list[list[IP]]
    isCdnDatacenter: bool

    auth: AuthCredentials
    salts: list[Salt]
    saltsMedia: list[Salt]

    @classmethod
    def deserialize(cls, buffer: NativeByteBuffer) -> Datacenter:
        currentVersion = buffer.readUint32()
        datacenterId = buffer.readUint32()

        lastInitVersion = buffer.readUint32() if currentVersion >= 3 else None
        lastInitMediaVersion = buffer.readUint32() if currentVersion >= 10 else None

        ips = [[], [], [], []]
        for b in range(4 if currentVersion >= 5 else 1):
            ip_array = ips[b]

            ip_count = buffer.readUint32()
            for _ in range(ip_count):
                ip_array.append(IP.deserialize(buffer, currentVersion))

        isCdnDatacenter = buffer.readBool() if currentVersion >= 6 else None

        auth = AuthCredentials.deserialize(buffer, currentVersion)

        salt_count = buffer.readUint32()
        salts = [Salt.deserialize(buffer) for _ in range(salt_count)]
        saltsMedia = None

        if currentVersion >= 13:
            salt_count = buffer.readUint32()
            saltsMedia = [Salt.deserialize(buffer) for _ in range(salt_count)]

        return cls(currentVersion, datacenterId, lastInitVersion, lastInitMediaVersion, ips, isCdnDatacenter, auth,
                   salts, saltsMedia)

    def serialize(self, buffer: NativeByteBuffer) -> None:
        buffer.writeUint32(self.currentVersion)
        buffer.writeUint32(self.datacenterId)
        if self.currentVersion >= 3:
            buffer.writeUint32(self.lastInitVersion)
        if self.currentVersion >= 10:
            buffer.writeUint32(self.lastInitMediaVersion)

        for i in range(4 if self.currentVersion >= 5 else 1):
            buffer.writeUint32(len(self.ips[i]))
            for ip in self.ips[i]:
                ip.serialize(buffer, self.currentVersion)

        if self.currentVersion >= 6:
            buffer.writeBool(self.isCdnDatacenter)

        self.auth.serialize(buffer, self.currentVersion)

        buffer.writeUint32(len(self.salts))
        for salt in self.salts:
            salt.serialize(buffer)

        if self.currentVersion >= 13:
            buffer.writeUint32(len(self.saltsMedia))
            for salt in self.saltsMedia:
                salt.serialize(buffer)
