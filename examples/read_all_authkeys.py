from tgnet import Tgnet

tgnet_path = input("tgnet.dat path: ")

tgnet = Tgnet(tgnet_path)

for dc_id in range(1, 6):
    dc = tgnet.get_datacenter(dc_id)
    if not dc:
        continue
    if key := dc.get_auth_key("perm"):
        print(key.hex())
    if key := dc.get_auth_key("temp"):
        print(key.hex())