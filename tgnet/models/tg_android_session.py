from __future__ import annotations

from dataclasses import dataclass

from tgnet.models.datacenter import Datacenter
from tgnet.models.headers import Headers
from tgnet.native_byte_buffer import NativeByteBuffer


@dataclass
class TGAndroidSession:
    headers: Headers
    datacenters: list[Datacenter]

    @classmethod
    def deserialize(cls, buffer: NativeByteBuffer) -> TGAndroidSession:
        headers = Headers.deserialize(buffer)
        datacenters = []

        numOfDatacenters = buffer.readUint32()
        for i in range(numOfDatacenters):
            datacenters.append(Datacenter.deserialize(buffer))

        return cls(headers, datacenters)

    def serialize(self, buffer: NativeByteBuffer) -> None:
        self.headers.serialize(buffer)
        buffer.writeUint32(len(self.datacenters))

        for dc in self.datacenters:
            dc.serialize(buffer)
