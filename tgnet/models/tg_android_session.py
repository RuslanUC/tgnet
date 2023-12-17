from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tgnet.models.datacenter import Datacenter
from tgnet.models.headers import Headers
from tgnet.native_byte_buffer import NativeByteBuffer


@dataclass
class TGAndroidSession:
    headers: Headers
    datacenters: list[Datacenter]

    @classmethod
    def deserialize(cls, buffer: NativeByteBuffer) -> TGAndroidSession:
        buffer.readUint32()  # config size (file size minus 4), not used now

        headers = Headers.deserialize(buffer)
        datacenters = []

        numOfDatacenters = buffer.readUint32()
        for i in range(numOfDatacenters):
            datacenters.append(Datacenter.deserialize(buffer))

        return cls(headers, datacenters)

    def serialize(self, buffer: NativeByteBuffer) -> None:
        start_size = buffer.buffer.tell()
        buffer.writeUint32(0)

        self.headers.serialize(buffer)
        buffer.writeUint32(len(self.datacenters))

        for dc in self.datacenters:
            dc.serialize(buffer)

        config_size = buffer.buffer.tell() - start_size
        buffer.buffer.seek(start_size)
        buffer.writeUint32(config_size - 4)

    def currentDc(self) -> Optional[Datacenter]:
        if (self.headers is None or not self.headers.full or not self.datacenters or
                self.headers.currentDatacenterId == 0):
            return

        return self.datacenters[self.headers.currentDatacenterId]
