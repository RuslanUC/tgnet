from __future__ import annotations

from dataclasses import dataclass

from tgnet.raw.datacenter import Datacenter
from tgnet.raw.headers import Headers
from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class TgnetSession:
    headers: Headers
    datacenters: list[Datacenter]

    @classmethod
    def deserialize(cls, buffer: TgnetReader) -> TgnetSession:
        buffer.read_uint32()  # config size (file size minus 4), not used now

        headers = Headers.deserialize(buffer)
        datacenters = []

        numOfDatacenters = buffer.read_uint32()
        for i in range(numOfDatacenters):
            datacenters.append(Datacenter.deserialize(buffer))

        return cls(
            headers=headers,
            datacenters=datacenters,
        )

    def serialize(self, buffer: TgnetReader) -> None:
        start_size = buffer.buffer.tell()
        buffer.write_uint32(0)

        self.headers.serialize(buffer)
        buffer.write_uint32(len(self.datacenters))

        for dc in self.datacenters:
            dc.serialize(buffer)

        config_size = buffer.buffer.tell() - start_size
        buffer.buffer.seek(start_size)
        buffer.write_uint32(config_size - 4)
