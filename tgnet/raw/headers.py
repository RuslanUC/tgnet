from __future__ import annotations

from dataclasses import dataclass
from time import time

from tgnet.raw.tgnet_reader import TgnetReader


@dataclass
class Headers:
    version: int
    test_backend: bool
    client_blocked: bool
    last_init_system_lang_code: str
    full: bool
    current_datacenter_id: int | None = None
    time_difference: int | None = None
    last_dc_update_time: int | None = None
    push_session_id: int | None = None
    registered_for_internal_push: bool | None = None
    last_server_time: int | None = None
    current_time: int | None = None
    sessions_to_destroy: list[int] | None = None

    @classmethod
    def deserialize(cls, buffer: TgnetReader) -> Headers:
        version = buffer.read_uint32()
        if version > 99999:
            raise NotImplementedError(f"Deserializing this version of config ({version}) is not currently supported")

        test_backend = buffer.read_bool()
        client_blocked = buffer.read_bool() if version >= 3 else None
        last_init_system_lang_code = buffer.read_string() if version >= 4 else None

        full = buffer.read_bool()
        if not full:
            return cls(
                version=version,
                test_backend=test_backend,
                client_blocked=client_blocked,
                last_init_system_lang_code=last_init_system_lang_code,
                full=full,
            )

        current_datacenter_id = buffer.read_uint32()
        time_difference = buffer.read_int32()
        last_dc_update_time = buffer.read_int32()
        push_session_id = buffer.read_int64()

        registered_for_internal_push = buffer.read_bool() if version >= 2 else None
        last_server_time = None
        current_time = int(time())
        if version >= 5:
            last_server_time = buffer.read_int32()
            if time_difference < current_time < last_server_time:
                time_difference += (last_server_time - current_time)

        sessions_to_destroy = []
        count = buffer.read_uint32()
        for a in range(count):
            sessions_to_destroy.append(buffer.read_int64())

        return cls(
            version=version,
            test_backend=test_backend,
            client_blocked=client_blocked,
            last_init_system_lang_code=last_init_system_lang_code,
            full=full,
            current_datacenter_id=current_datacenter_id,
            time_difference=time_difference,
            last_dc_update_time=last_dc_update_time,
            push_session_id=push_session_id,
            registered_for_internal_push=registered_for_internal_push,
            last_server_time=last_server_time,
            current_time=current_time,
            sessions_to_destroy=sessions_to_destroy,
        )

    def serialize(self, buffer: TgnetReader) -> None:
        buffer.write_uint32(self.version)
        buffer.write_bool(self.test_backend)
        if self.version >= 3:
            buffer.write_bool(self.client_blocked)
        if self.version >= 4:
            buffer.writeString(self.last_init_system_lang_code)

        buffer.write_bool(self.full)
        if not self.full:
            return

        buffer.write_uint32(self.current_datacenter_id)
        buffer.write_int32(self.time_difference)
        buffer.write_int32(self.last_dc_update_time)
        buffer.write_int64(self.push_session_id)

        if self.version >= 2:
            buffer.write_bool(self.registered_for_internal_push)
        if self.version >= 5:
            buffer.write_int32(self.last_server_time)

        buffer.write_uint32(len(self.sessions_to_destroy))
        for i in self.sessions_to_destroy:
            buffer.write_int64(i)
