from tgnet import NativeByteBuffer, TGAndroidSession

tgnet_path = 'tgnets/tgnet.dat'
with open(tgnet_path, 'rb') as f:
    buf = NativeByteBuffer(f)
    tgdata = TGAndroidSession.deserialize(buf)

valid_session = tgdata.datacenters[tgdata.headers.currentDatacenterId - 1]
# or tgdata.currentDc()

print(f"dc: {tgdata.headers.currentDatacenterId}")
print('auth key:', valid_session.auth.authKeyPerm.hex())

# Uncomment lines below if you want to write tgnet back to file
#with open('tgnets/tgnet_serialized.dat', 'wb') as f:
#    buf = NativeByteBuffer(f)
#    tgdata.serialize(buf)
