from __future__ import annotations
from io import BytesIO
from os import PathLike
from typing import BinaryIO

from tgnet import Headers, IP, AuthCredentials
from tgnet.raw import TgnetSession, TgnetReader, Datacenter as RawDatacenter
from tgnet.utils import make_auth_key_id


class Datacenter:
    def __init__(self, dc: RawDatacenter):
        self._dc = dc

    @property
    def id(self) -> int:
        """
        :return: This datacenter id
        """

        return self._dc.datacenter_id

    @property
    def raw_datacenter(self) -> RawDatacenter:
        """
        Underlying "low-level" datacenter object.

        :return: Object of type tgnet.low.Datacenter
        """

        return self._dc

    def set_auth_key_perm(self, key: bytes | None) -> None:
        if key is not None and len(key) != 256:
            raise ValueError(f"Invalid auth key provided. Expected key of length 256.")

        auth = self._dc.auth
        auth.auth_key_perm = key
        auth.auth_key_perm_id = make_auth_key_id(key)
        auth.authorized = key is not None

    def set_auth_key_temp(self, key: bytes | None) -> None:
        if key is not None and len(key) != 256:
            raise ValueError(f"Invalid auth key provided. Expected key of length 256.")

        auth = self._dc.auth
        auth.auth_key_temp = key
        auth.auth_key_temp_id = make_auth_key_id(key)

    def set_auth_key_media_temp(self, key: bytes | None) -> None:
        if key is not None and len(key) != 256:
            raise ValueError(f"Invalid auth key provided. Expected key of length 256.")

        auth = self._dc.auth
        auth.auth_key_media_temp = key
        auth.auth_key_media_temp_id = make_auth_key_id(key)

    def get_auth_key_perm(self) -> bytes | None:
        return self._dc.auth.auth_key_perm

    def get_auth_key_temp(self) -> bytes | None:
        return self._dc.auth.auth_key_temp

    def get_auth_key_media_temp(self) -> bytes | None:
        return self._dc.auth.auth_key_media_temp

    def reset(self) -> None:
        """
        Resets datacenter: clears all auth keys and salts.

        :return: None
        """

        auth = self._dc.auth

        auth.auth_key_perm = None
        auth.auth_key_perm_id = 0
        auth.auth_key_temp = None
        auth.auth_key_temp_id = 0
        auth.auth_key_media_temp = None
        auth.auth_key_media_temp_id = 0
        auth.authorized = False

        self._dc.salt = []
        self._dc.salt_media = []


class Tgnet:
    __slots__ = ("_session", "_datacenters")

    def __init__(
            self,
            file: bytes | bytearray | str | PathLike | BinaryIO | None = None,
            session: TgnetSession | None = None,
    ) -> None:
        if file is None and session is None:
            raise ValueError(f"You need to pass either \"file\" or \"session\" to {self.__class__.__name__}.")

        if session is None:
            if isinstance(file, (bytes, bytearray)):
                fp = BytesIO(file)
            elif isinstance(file, BinaryIO):
                fp = file
            else:
                fp = open(file, "rb")

            session = TgnetSession.deserialize(TgnetReader(fp))

            if not isinstance(file, (bytes, bytearray, BinaryIO)):
                fp.close()

        self._session = session
        self._datacenters = [Datacenter(dc) for dc in self._session.datacenters]

    def get_datacenter(self, dc: int) -> Datacenter | None:
        """
        Retrieves the datacenter with the provided dcId.

        :param dc: The ID of the datacenter to retrieve.
        :return: Datacenter if found, otherwise None
        """

        if dc > len(self._datacenters) or dc < 0:
            return None

        return self._datacenters[dc - 1]

    def get_current_datacenter(self) -> Datacenter | None:
        """
        Retrieves the current datacenter.

        :return: Datacenter if current is set, otherwise None
        """

        if (self._session.headers is None or not self._session.headers.full or not self._session.datacenters or
                self._session.headers.current_datacenter_id == 0):
            return None

        return self.get_datacenter(self._session.headers.current_datacenter_id)

    def _get_dc(self, dc_id: int | None) -> Datacenter | None:
        if dc_id is None:
            return self.get_current_datacenter()
        else:
            return self.get_datacenter(dc_id)

    def set_auth_key_perm(self, dc_id: int | None, key: bytes | None) -> None:
        """
        Sets the perm authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :param key: The authentication key to be set. It can be None to reset the key.
        :return: None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            dc.set_auth_key_perm(key)

    def set_auth_key_temp(self, dc_id: int | None, key: bytes | None) -> None:
        """
        Sets the temp authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :param key: The authentication key to be set. It can be None to reset the key.
        :return: None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            dc.set_auth_key_temp(key)

    def set_auth_key_media_temp(self, dc_id: int | None, key: bytes | None) -> None:
        """
        Sets the media temp authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :param key: The authentication key to be set. It can be None to reset the key.
        :return: None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            dc.set_auth_key_media_temp(key)

    def get_auth_key_perm(self, dc_id: int | None = None) -> bytes | None:
        """
        Gets the perm authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :return: Auth key or None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            return dc.get_auth_key_perm()

    def get_auth_key_temp(self, dc_id: int | None = None) -> bytes | None:
        """
        Gets the temp authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :return: Auth key or None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            return dc.get_auth_key_temp()

    def get_auth_key_media_temp(self, dc_id: int | None = None) -> bytes | None:
        """
        Gets the media temp authentication key for the datacenter.

        :param dc_id: The id of the datacenter. If None, then current dc is selected.
        :return: Auth key or None
        """

        if (dc := self._get_dc(dc_id)) is not None:
            return dc.get_auth_key_media_temp()

    def set_current_datacenter_id(self, dc: int) -> None:
        """
        Sets current datacenter id.

        :param dc: The id of the datacenter to set.
        :return: None
        """

        if self.get_datacenter(dc) is None:
            return

        self._session.headers.current_datacenter_id = dc

    def reset_dc(self, dc: int) -> None:
        """
        Resets datacenter with given id: clears all auth keys and salts.

        :param dc: The id of the datacenter to reset.
        :return: None
        """

        if (dc := self.get_datacenter(dc)) is None:
            return

        dc.reset()

    def reset(self, new_current_dc: int = 2) -> None:
        """
        Resets all datacenters: clears all auth keys and salts.

        :param new_current_dc: The ID of the new current datacenter. Defaults to 2.
        :return: None
        """

        for dc in self._datacenters:
            dc.reset()

        headers = self._session.headers

        headers.current_datacenter_id = new_current_dc
        headers.time_difference = 0
        headers.last_dc_update_time = 0
        headers.push_session_id = 0
        headers.registered_for_internal_push = False
        headers.last_server_time = 0
        headers.current_time = 0
        headers.sessions_to_destroy = []

    def save(self, file: str | PathLike | BinaryIO) -> None:
        """
        Saves tgnet session to a file.

        :param file: The file or file path to save tgnet session to.
        :return: None
        """

        if isinstance(file, BinaryIO):
            fp = file
        else:
            fp = open(file, "wb")

        self._session.serialize(TgnetReader(fp))

        if not isinstance(file, BinaryIO):
            fp.close()

    @classmethod
    def default(cls) -> Tgnet:
        """
        :return: An instance of Tgnet with default settings.
        """

        def _dc(id_: int, ips: list[list[IP]]) -> RawDatacenter:
            while len(ips) < 4:
                ips.append([])
            return RawDatacenter(
                current_version=13,
                datacenter_id=id_,
                last_init_version=725,
                last_init_media_version=725,
                ips=ips,
                is_cdn=False,
                auth=AuthCredentials(
                    auth_key_perm=None,
                    auth_key_perm_id=0,
                    auth_key_temp=None,
                    auth_key_temp_id=0,
                    auth_key_media_temp=None,
                    auth_key_media_temp_id=0,
                    authorized=0,
                ),
                salt=[],
                salt_media=[],
            )

        def _ip(address: str, flags: int) -> IP:
            return IP(address=address, port=443, flags=flags, secret="")

        session = TgnetSession(
            headers=Headers(
                version=5,
                test_backend=False,
                client_blocked=False,
                last_init_system_lang_code="en-us",
                full=True,
                current_datacenter_id=0,
                time_difference=0,
                last_dc_update_time=0,
                push_session_id=0,
                registered_for_internal_push=False,
                last_server_time=0,
                current_time=0,
                sessions_to_destroy=[],
            ),
            datacenters=[
                _dc(1, [
                    [_ip("149.154.175.59", 0), _ip("149.154.175.55", 16)],
                    [_ip("2001:0b28:f23d:f001:0000:0000:0000:000a", 1)],
                ]),
                _dc(2, [
                    [_ip("149.154.167.51", 0), _ip("149.154.167.41", 16)],
                    [_ip("2001:067c:04e8:f002:0000:0000:0000:000a", 1)],
                    [_ip("149.154.167.151", 2)],
                    [_ip("2001:067c:04e8:f002:0000:0000:0000:000b", 3)],
                ]),
                _dc(3, [
                    [_ip("149.154.175.100", 0)],
                    [_ip("2001:0b28:f23d:f003:0000:0000:0000:000a", 1)],
                ]),
                _dc(4, [
                    [_ip("149.154.167.92", 0)],
                    [_ip("2001:067c:04e8:f004:0000:0000:0000:000a", 1)],
                    [_ip("149.154.166.120", 2)],
                    [_ip("2001:067c:04e8:f004:0000:0000:0000:000b", 3)],
                ]),
                _dc(5, [
                    [_ip("91.108.56.183", 0)],
                    [_ip("2001:0b28:f23f:f005:0000:0000:0000:000a", 1)],
                ]),
            ],
        )

        return cls(session=session)
