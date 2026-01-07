from io import BytesIO

from tgnet import Headers, Datacenter, IP, AuthCredentials, Salt, TgnetReader, TgnetSession


def test_headers():
    headers = Headers(5, False, False, "en-us", True, 2, 150, 1699890434, 0x4242424242424242, True, 1699890400,
                      1699890500, [1, 2, 3])
    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    headers.serialize(buf)
    assert to_serialize.getvalue() == (b'\x05\x00\x00\x007\x97y\xbc7\x97y\xbc\x05en-us\x00\x00\xb5ur'
                                       b'\x99\x02\x00\x00\x00\x96\x00\x00\x00\x02EReBBBBBBBB\xb5ur\x99\xe0DRe\x03\x00'
                                       b'\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03'
                                       b'\x00\x00\x00\x00\x00\x00\x00')

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_headers = Headers.deserialize(buf)
    deserialized_headers.current_time = headers.current_time
    assert deserialized_headers == headers

    return headers


def test_ip():
    ip = IP("127.0.0.1", 443, 123, "00112233445566778899aabbccddeeff")
    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    ip.serialize(buf, 11)
    assert to_serialize.getvalue() == (b'\t127.0.0.1\x00\x00\xbb\x01\x00\x00{\x00\x00\x00 00112233445566778899aabbccdd'
                                       b'eeff\x00\x00\x00')

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_ip = IP.deserialize(buf, 11)
    assert deserialized_ip == ip


def test_salt():
    salt = Salt(1699890400, 1699890500, 0x4242424242424242)
    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    salt.serialize(buf)
    assert to_serialize.getvalue() == b'\xe0DReDEReBBBBBBBB'

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_salt = Salt.deserialize(buf)
    assert deserialized_salt == salt


def test_auth():
    auth = AuthCredentials(b"perm" * 64, 0x4242424242424242, b"temp" * 64, 0x4141414141414141, b"media___" * 32,
                           0x4040404040404040, 1)
    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    auth.serialize(buf, 12)

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_auth = AuthCredentials.deserialize(buf, 12)
    assert deserialized_auth == auth


def test_datacenter():
    dc = Datacenter(
        13, 1, 42, 42, [[IP("127.0.0.1", 443, 123, "00112233445566778899aabbccddeeff")],
                        [IP("127.0.0.1", 444, 123, "00112233445566778899aabbccddeeff")], [], []], False,
        AuthCredentials(b"perm" * 64, 0x4242424242424242, b"temp" * 64, 0x4141414141414141, b"media___" * 32,
                        0x4040404040404040, 1),
        [Salt(1699890400, 1699890500, 0x4242424242424242)], [Salt(1699890402, 1699890502, 0x4343434343434343)]
    )

    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    dc.serialize(buf)

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_dc = Datacenter.deserialize(buf)
    assert deserialized_dc == dc

    return dc


def test_session():
    h = test_headers()
    sess = TgnetSession(h, [test_datacenter()])
    to_serialize = BytesIO()
    buf = TgnetReader(to_serialize)
    sess.serialize(buf)

    to_deserialize = BytesIO(to_serialize.getvalue())
    buf = TgnetReader(to_deserialize)
    deserialized_sess = TgnetSession.deserialize(buf)
    deserialized_sess.headers.current_time = h.current_time
    assert deserialized_sess == sess
