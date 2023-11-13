"""
BufferWrapper is a wrapper for NativeByteBuffer

Creator https://github.com/batreller/
Code https://github.com/batreller/telegram_android_session_converter
"""

import time
from typing import Literal

from BufferWrapper.models.auth import AuthCredentials
from BufferWrapper.models.datacenter import Datacenter
from BufferWrapper.models.headers import Headers
from BufferWrapper.models.ip import IP
from BufferWrapper.models.salt import Salt
from BufferWrapper.models.tg_android_session import TGAndroidSession
from NativeByteBuffer import NativeByteBuffer


class BufferWrapper:
    def __init__(self, bytes_: bytes):
        self.buffer = NativeByteBuffer(bytes_)
        self.NativeByteBuffer = NativeByteBuffer
        self._PADDING = 24
        self._CONFIG_VERSION = 99999
        self.currentVersion = 0

    def _get_current_time(self) -> int:
        return int(time.time())

    def get_tg_android_session(self) -> TGAndroidSession:
        session = TGAndroidSession()
        session.headers = self.front_headers()
        session.datacenters = self.datacenters()
        return session

    def write_android_session(self, session: TGAndroidSession) -> None:
        self.write_front_headers(session.headers)
        self.write_datacenters(session.datacenters)

    def write_front_headers(self, headers: Headers) -> None:
        self.buffer.writeBytes(b"\xc0\x17\x00\x00")
        self.buffer.writeUint32(headers.version)
        self.buffer.writeBool(headers.testBackend)
        if headers.version >= 3:
            self.buffer.writeBool(headers.clientBlocked)
        if headers.version >= 4:
            self.buffer.writeString(headers.lastInitSystemLangcode)

        self.buffer.writeBool(True)

        self.buffer.writeUint32(headers.currentDatacenterId)
        self.buffer.writeInt32(headers.timeDifference)
        self.buffer.writeInt32(headers.lastDcUpdateTime)
        self.buffer.writeInt64(headers.pushSessionId)

        if headers.version >= 2:
            self.buffer.writeBool(headers.registeredForInternalPush)
        if headers.version >= 5:
            self.buffer.writeInt32(headers.lastServerTime)

        self.buffer.writeUint32(len(headers.sessionsToDestroy))
        for i in headers.sessionsToDestroy:
            self.buffer.writeInt64(i)

    def write_datacenters(self, datacenters: list[Datacenter]) -> None:
        self.buffer.writeUint32(len(datacenters))

        for dc in datacenters:
            self.buffer.writeUint32(dc.currentVersion)
            self.buffer.writeUint32(dc.datacenterId)
            if dc.currentVersion >= 3:
                self.buffer.writeUint32(dc.lastInitVersion)
            if dc.currentVersion >= 10:
                self.buffer.writeUint32(dc.lastInitMediaVersion)

            for i in range(4 if dc.currentVersion >= 5 else 1):
                self.buffer.writeUint32(len(dc.ips[i]))
                for ip in dc.ips[i]:
                    self.buffer.writeString(ip.address)
                    self.buffer.writeUint32(ip.port)
                    if dc.currentVersion >= 7:
                        self.buffer.writeInt32(ip.flags)
                    if dc.currentVersion >= 11:
                        self.buffer.writeString(ip.secret)
                    elif dc.currentVersion >= 9:
                        if ip.secret:
                            result = ip.secret.encode('utf-8')
                            size = len(result)
                            output = ""
                            for i_ in range(size):
                                output += format(result[i_], '02x')
                            self.buffer.writeString(output)

            if dc.currentVersion >= 6:
                self.buffer.writeBool(dc.isCdnDatacenter)

            self.write_auth_credentials(dc.auth, dc)
            self.write_salt_info(dc.salt, dc.salt13, dc)

    def write_auth_credentials(self, auth: AuthCredentials, dc: Datacenter) -> None:
        self.buffer.writeUint32(len(auth.authKeyPerm) if auth.authKeyPerm else 0)
        if auth.authKeyPerm:
            self.buffer.writeBytes(auth.authKeyPerm)

        if dc.currentVersion >= 4:
            self.buffer.writeInt64(auth.authKeyPermId)
        else:
            if auth.authKeyPermId:
                self.buffer.writeUint32(8)
                self.buffer.writeInt64(auth.authKeyPermId)
            else:
                self.buffer.writeUint32(0)

        if dc.currentVersion >= 8:
            if auth.authKeyTemp:
                self.buffer.writeUint32(len(auth.authKeyTemp))
                self.buffer.writeBytes(auth.authKeyTemp)
            else:
                self.buffer.writeUint32(0)
            self.buffer.writeInt64(auth.authKeyTempId)

        if dc.currentVersion >= 12:
            if auth.authKeyMediaTemp:
                self.buffer.writeUint32(len(auth.authKeyMediaTemp))
                self.buffer.writeBytes(auth.authKeyMediaTemp)
            else:
                self.buffer.writeUint32(0)
            self.buffer.writeInt64(auth.authKeyMediaTempId)

        self.buffer.writeInt32(auth.authorized)

    def write_salt_info(self, salts: list[Salt], salts13: list[Salt], dc: Datacenter) -> None:
        self.buffer.writeUint32(len(salts))
        for salt in salts:
            self.buffer.writeInt32(salt.salt_valid_since)
            self.buffer.writeInt32(salt.salt_valid_until)
            self.buffer.writeInt64(salt.salt)

        if dc.currentVersion >= 13:
            self.buffer.writeUint32(len(salts13))
            for salt in salts13:
                self.buffer.writeInt32(salt.salt_valid_since)
                self.buffer.writeInt32(salt.salt_valid_until)
                self.buffer.writeInt64(salt.salt)

    def front_headers(self) -> Headers:
        headers = Headers()
        self.buffer.readBytes(4)
        if self.buffer is not None:
            version = self.buffer.readUint32()
            headers.version = version

            if version <= self._CONFIG_VERSION:
                headers.testBackend = self.buffer.readBool()
                if version >= 3:
                    headers.clientBlocked = self.buffer.readBool()
                if version >= 4:
                    headers.lastInitSystemLangcode = self.buffer.readString()

                if self.buffer.readBool():
                    headers.currentDatacenterId = self.buffer.readUint32()
                    headers.timeDifference = self.buffer.readInt32()
                    headers.lastDcUpdateTime = self.buffer.readInt32()
                    headers.pushSessionId = self.buffer.readInt64()

                    if version >= 2:
                        registeredForInternalPush = self.buffer.readBool()
                        headers.registeredForInternalPush = registeredForInternalPush
                    if version >= 5:
                        lastServerTime = self.buffer.readInt32()
                        currentTime = self._get_current_time()

                        headers.lastServerTime = lastServerTime
                        headers.currentTime = currentTime

                        if headers.timeDifference < currentTime < lastServerTime:
                            headers.timeDifference += (lastServerTime - currentTime)

                    headers.sessionsToDestroy = []
                    count = self.buffer.readUint32()
                    for a in range(count):
                        headers.sessionsToDestroy.append(self.buffer.readInt64())
        return headers

    def get_ip(self, ip_type: Literal['addressesIpv4', 'addressesIpv6', 'addressesIpv4Download', 'addressesIpv6Download']) -> IP:
        ip = IP()
        ip.type_ = ip_type

        address = self.buffer.readString()
        port = self.buffer.readUint32()
        ip.address = address
        ip.port = port

        if self.currentVersion >= 7:
            flags = self.buffer.readInt32()
        else:
            flags = 0
        ip.flags = flags

        if self.currentVersion >= 11:
            ip.secret = self.buffer.readString()

        elif self.currentVersion >= 9:
            secret = self.buffer.readString()
            if secret:
                size = len(secret) // 2
                result = bytearray(size)
                for i in range(size):
                    result[i] = int(secret[i * 2:i * 2 + 2], 16)
                secret = result.decode('utf-8')
            ip.secret = secret

        return ip

    def datacenters(self):
        datacenters = []
        numOfDatacenters = self.buffer.readUint32()

        for i in range(numOfDatacenters):
            datacenter = Datacenter()

            self.currentVersion = datacenter.currentVersion = self.buffer.readUint32()
            datacenter.datacenterId = self.buffer.readUint32()

            if datacenter.currentVersion >= 3:
                datacenter.lastInitVersion = self.buffer.readUint32()

            if datacenter.currentVersion >= 10:
                datacenter.lastInitMediaVersion = self.buffer.readUint32()

            count = 4 if datacenter.currentVersion >= 5 else 1

            for b in range(count):
                array = None
                if b == 0:
                    array = 'addressesIpv4'
                elif b == 1:
                    array = 'addressesIpv6'
                elif b == 2:
                    array = 'addressesIpv4Download'
                elif b == 3:
                    array = 'addressesIpv6Download'

                if array is None:
                    continue

                ips = self.buffer.readUint32()
                ips_ = []
                for ip_index in range(ips):
                    ip = self.get_ip(array)
                    ips_.append(ip)

                datacenter.ips.append(ips_)

            if datacenter.currentVersion >= 6:
                datacenter.isCdnDatacenter = self.buffer.readBool()

            auth_credentials = self.auth_credentials()
            datacenter.auth = auth_credentials

            datacenter.salt, datacenter.salt13 = self.salt_info()
            datacenters.append(datacenter)

        return datacenters

    def auth_credentials(self) -> AuthCredentials:
        auth = AuthCredentials()
        len_of_bytes = self.buffer.readUint32()
        if len_of_bytes != 0:
            auth.authKeyPerm = self.buffer.readBytes(len_of_bytes)

        if self.currentVersion >= 4:
            auth.authKeyPermId = self.buffer.readInt64()
        else:
            len_of_bytes = self.buffer.readUint32()
            if len_of_bytes != 0:
                auth.authKeyPermId = self.buffer.readInt64()

        if self.currentVersion >= 8:
            len_of_bytes = self.buffer.readUint32()
            if len_of_bytes != 0:
                auth.authKeyTemp = self.buffer.readBytes(len_of_bytes)
            auth.authKeyTempId = self.buffer.readInt64()

        if self.currentVersion >= 12:
            len_of_bytes = self.buffer.readUint32()
            if len_of_bytes != 0:
                auth.authKeyMediaTemp = self.buffer.readBytes(len_of_bytes)
            auth.authKeyMediaTempId = self.buffer.readInt64()

        auth.authorized = self.buffer.readInt32()

        return auth

    def salt_info(self):
        salts = []
        salts13 = []
        bytes_len = self.buffer.readUint32()
        for x in range(bytes_len):
            salt = Salt()
            salt.salt_valid_since = self.buffer.readInt32()
            salt.salt_valid_until = self.buffer.readInt32()
            salt.salt = self.buffer.readInt64()
            salts.append(salt)

        if self.currentVersion >= 13:
            bytes_len = self.buffer.readUint32()
            for x in range(bytes_len):
                salt = Salt()
                salt.salt_valid_since = self.buffer.readInt32()
                salt.salt_valid_until = self.buffer.readInt32()
                salt.salt = self.buffer.readInt64()
                salts13.append(salt)

        return salts, salts13
