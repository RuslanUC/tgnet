from __future__ import annotations
from io import BytesIO
from os import PathLike
from typing import BinaryIO, Union, Optional, Literal

from tgnet import Headers, IP, AuthCredentials
from tgnet.low import TgnetSession, TgnetReader, Datacenter as LowDatacenter
from tgnet.utils import calcKeyId

AuthKeyType = Literal["perm", "temp", "media"]


class Datacenter:
    def __init__(self, dc: LowDatacenter):
        self._dc = dc

    @property
    def id(self) -> int:
        """
        :return: This datacenter id
        """

        return self._dc.datacenterId

    @property
    def low_datacenter(self) -> LowDatacenter:
        """
        Underlying "low-level" datacenter object.

        :return: Object of type tgnet.low.Datacenter
        """

        return self._dc

    def set_auth_key(self, key: Optional[bytes], type_: AuthKeyType = "perm") -> None:
        """
        Used to set the authentication key for the datacenter.

        :param key: The authentication key to be set. It can be None to reset the key.
        :param type_: The type of authentication key to be set. It can be one of the following:
            "perm": Permanent (primary) key.
            "temp": Temporary key (see https://core.telegram.org/api/pfs).
            "media": Media temp key.
        :return: None
        """

        if key is not None and len(key) != 256:
            raise ValueError(f"Invalid auth key provided. Expected key of length 256.")

        auth = self._dc.auth

        if type_ == "perm":
            auth.authKeyPerm = key
            auth.authKeyPermId = calcKeyId(key)
            auth.authorized = key is not None
        elif type_ == "temp":
            auth.authKeyTemp = key
            auth.authKeyTempId = calcKeyId(key)
        elif type_ == "media":
            auth.authKeyMediaTemp = key
            auth.authKeyMediaTempId = calcKeyId(key)
        else:
            raise ValueError(
                f"Invalid auth key type provided. Expected one of (\"perm\", \"temp\", \"media\"), got {type_}."
            )

    def get_auth_key(self, type_: AuthKeyType) -> Optional[bytes]:
        """
        Used to set the authentication key for the datacenter.

        :param type_: The type of authentication key to get. It can be one of the following:
            "perm": Permanent (primary) key.
            "temp": Temporary key (see https://core.telegram.org/api/pfs).
            "media": Media temp key.
        :return: Auth key of the provided type if set, otherwise None
        """

        auth = self._dc.auth

        if type_ == "perm":
            return auth.authKeyPerm
        elif type_ == "temp":
            return auth.authKeyTemp
        elif type_ == "media":
            return auth.authKeyMediaTemp
        else:
            raise ValueError(
                f"Invalid auth key type provided. Expected one of (\"perm\", \"temp\", \"media\"), got {type_}."
            )

    def reset(self) -> None:
        """
        Resets datacenter: clears all auth keys and salts.

        :return: None
        """

        auth = self._dc.auth

        auth.authKeyPerm = None
        auth.authKeyPermId = 0
        auth.authKeyTemp = None
        auth.authKeyTempId = 0
        auth.authKeyMediaTemp = None
        auth.authKeyMediaTempId = 0
        auth.authorized = False

        self._dc.salt = []
        self._dc.saltMedia = []


class Tgnet:
    __slots__ = ("_session", "_datacenters")

    def __init__(self, file: Optional[Union[bytes, bytearray, str, PathLike, BinaryIO]] = None,
                 session: Optional[TgnetSession] = None):
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

    def get_datacenter(self, dc: int) -> Optional[Datacenter]:
        """
        Retrieves the datacenter with the provided dcId.

        :param dc: The ID of the datacenter to retrieve.
        :return: Datacenter if found, otherwise None
        """

        if dc > len(self._datacenters) or dc < 0:
            return

        return self._datacenters[dc - 1]

    @property
    def current_datacenter(self) -> Optional[Datacenter]:
        """
        Retrieves the current datacenter.

        :return: Datacenter if current is set, otherwise None
        """

        if (self._session.headers is None or not self._session.headers.full or not self._session.datacenters or
                self._session.headers.currentDatacenterId == 0):
            return

        return self.get_datacenter(self._session.headers.currentDatacenterId)

    @property
    def auth_key(self) -> Optional[bytes]:
        """
        Retrieves the auth key for the current datacenter.

        :return: Auth key if the current datacenter is set and an auth key is set in it, otherwise None
        """

        if not (dc := self.current_datacenter):
            return
        return dc.get_auth_key("perm")

    def set_auth_key(self, dc: int, key: Optional[bytes], type_: Literal["perm", "temp", "media"] = "perm") -> None:
        """
        Sets the authentication key for the datacenter.

        :param dc: The id of the datacenter.
        :param key: The authentication key to be set. It can be None to reset the key.
        :param type_: The type of authentication key to be set. It can be one of the following:
            "perm": Permanent (primary) key.
            "temp": Temporary key (see https://core.telegram.org/api/pfs).
            "media": Media temp key.
        :return: None
        """

        if (dc := self.get_datacenter(dc)) is None:
            return

        dc.set_auth_key(key, type_)

    def set_current_dc(self, dc: int) -> None:
        """
        Sets current datacenter id.

        :param dc: The id of the datacenter to set.
        :return: None
        """

        if self.get_datacenter(dc) is None:
            return

        self._session.headers.currentDatacenterId = dc

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

        headers.currentDatacenterId = new_current_dc
        headers.timeDifference = 0
        headers.lastDcUpdateTime = 0
        headers.pushSessionId = 0
        headers.registeredForInternalPush = False
        headers.lastServerTime = 0
        headers.currentTime = 0
        headers.sessionsToDestroy = []

    def save(self, file: Union[str, PathLike, BinaryIO]) -> None:
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

        def _dc(id_: int, ips: list[list[IP]]) -> LowDatacenter:
            while len(ips) < 4:
                ips.append([])
            return LowDatacenter(
                currentVersion=13,
                datacenterId=id_,
                lastInitVersion=725,
                lastInitMediaVersion=725,
                ips=ips,
                isCdnDatacenter=False,
                auth=AuthCredentials(
                    authKeyPerm=None,
                    authKeyPermId=0,
                    authKeyTemp=None,
                    authKeyTempId=0,
                    authKeyMediaTemp=None,
                    authKeyMediaTempId=0,
                    authorized=0,
                ),
                salt=[],
                saltMedia=[],
            )

        def _ip(address: str, flags: int) -> IP:
            return IP(address=address, port=443, flags=flags, secret="")

        session = TgnetSession(
            headers=Headers(
                version=5,
                testBackend=False,
                clientBlocked=False,
                lastInitSystemLangCode="en-us",
                full=True,
                currentDatacenterId=0,
                timeDifference=0,
                lastDcUpdateTime=0,
                pushSessionId=0,
                registeredForInternalPush=False,
                lastServerTime=0,
                currentTime=0,
                sessionsToDestroy=[],
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
