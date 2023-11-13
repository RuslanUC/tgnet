# tgnet
Deserializes/serializes Telegram tgnet.dat format.
Can be used to extract/replace authKey and dcId.

#### This is fork of [batreller/telegram_android_session_converter](https://github.com/batreller/telegram_android_session_converter) with support of serialization and zero dependencies.
#### To convert the session all you need is just tgnet.dat file from the root directory of your telegram app on the phone, it's located at /data/data/org.telegram.messenger.web (or another package name, if you're using an unofficial client), it can be extracted using ADB (Android Debug Bridge).

## Usage
```python
>>> from tgnet import TGAndroidSession, NativeByteBuffer
>>> with open("tgnet.dat", "rb") as f:
...     buf = NativeByteBuffer(f)
...     tgdata = TGAndroidSession.deserialize(buf)
...
>>> currentDcId = tgdata.headers.currentDatacenterId
>>> currentDc = tgdata.datacenters[currentDcId - 1]
>>> print(currentDc.auth.authKeyPerm.hex())
'72a9808fb4a9e51e6ca57259714c14fa83546fc9d56fcb9d7de77c59fa13b6d6...'
```

### Running tests
```shell
pytest -s -x --disable-warnings --cov=tgnet/ test.py
```