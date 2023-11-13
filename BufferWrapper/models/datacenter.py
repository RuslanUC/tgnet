import base64
import ipaddress
import struct
from typing import Optional

from BufferWrapper.models.auth import AuthCredentials
from BufferWrapper.models.ip import IP
from BufferWrapper.models.salt import Salt


class Datacenter:
    # default android's api id and api hash, using desktop's api id and api hash strictly NOT recommended
    API_ID = 6
    API_HASH = 'eb06d4abfb49dc3eeb1aeb98ae0f581e'

    # default port of production server
    PROD_PORT = 443
    DATACENTERS = {
        1: "149.154.175.53",
        2: "149.154.167.51",
        3: "149.154.175.100",
        4: "149.154.167.91",
        5: "91.108.56.130"
    }

    currentVersion: int
    datacenterId: int
    lastInitVersion: int
    lastInitMediaVersion: Optional[int]

    ips = []
    isCdnDatacenter: bool

    auth: AuthCredentials
    salt: list[Salt] = []
    salt13: list[Salt] = []

    def __str__(self):
        return str(self.auth.authKeyPerm)
