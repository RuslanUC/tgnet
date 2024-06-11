from __future__ import annotations

from dataclasses import dataclass
from time import time

from tgnet.low.tgnet_reader import TgnetReader


@dataclass
class Headers:
    version: int
    testBackend: bool
    clientBlocked: bool
    lastInitSystemLangCode: str
    full: bool
    currentDatacenterId: int = None
    timeDifference: int = None
    lastDcUpdateTime: int = None
    pushSessionId: int = None
    registeredForInternalPush: bool = None
    lastServerTime: int = None
    currentTime: int = None
    sessionsToDestroy: list[int] = None

    @classmethod
    def deserialize(cls, buffer: TgnetReader) -> Headers:
        version = buffer.readUint32()
        if version > 99999:
            raise NotImplementedError(f"Deserializing this version of config ({version}) is not currently supported")

        testBackend = buffer.readBool()
        clientBlocked = buffer.readBool() if version >= 3 else None
        lastInitSystemLangCode = buffer.readString() if version >= 4 else None

        full = buffer.readBool()
        if not full:
            return cls(version, testBackend, clientBlocked, lastInitSystemLangCode, full)

        currentDatacenterId = buffer.readUint32()
        timeDifference = buffer.readInt32()
        lastDcUpdateTime = buffer.readInt32()
        pushSessionId = buffer.readInt64()

        registeredForInternalPush = buffer.readBool() if version >= 2 else None
        lastServerTime = None
        currentTime = int(time())
        if version >= 5:
            lastServerTime = buffer.readInt32()
            if timeDifference < currentTime < lastServerTime:
                timeDifference += (lastServerTime - currentTime)

        sessionsToDestroy = []
        count = buffer.readUint32()
        for a in range(count):
            sessionsToDestroy.append(buffer.readInt64())

        return cls(version, testBackend, clientBlocked, lastInitSystemLangCode, full, currentDatacenterId,
                   timeDifference, lastDcUpdateTime, pushSessionId, registeredForInternalPush, lastServerTime,
                   currentTime, sessionsToDestroy)

    def serialize(self, buffer: TgnetReader) -> None:
        buffer.writeUint32(self.version)
        buffer.writeBool(self.testBackend)
        if self.version >= 3:
            buffer.writeBool(self.clientBlocked)
        if self.version >= 4:
            buffer.writeString(self.lastInitSystemLangCode)

        buffer.writeBool(self.full)
        if not self.full:
            return

        buffer.writeUint32(self.currentDatacenterId)
        buffer.writeInt32(self.timeDifference)
        buffer.writeInt32(self.lastDcUpdateTime)
        buffer.writeInt64(self.pushSessionId)

        if self.version >= 2:
            buffer.writeBool(self.registeredForInternalPush)
        if self.version >= 5:
            buffer.writeInt32(self.lastServerTime)

        buffer.writeUint32(len(self.sessionsToDestroy))
        for i in self.sessionsToDestroy:
            buffer.writeInt64(i)
