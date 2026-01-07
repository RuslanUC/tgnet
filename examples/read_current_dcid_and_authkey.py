from tgnet import Tgnet

tgnet_path = input("tgnet.dat path: ")

tgnet = Tgnet(tgnet_path)
current_dc = tgnet.get_current_datacenter()
auth_key = current_dc.get_auth_key_perm()

print(f"Current dc id: {current_dc.id}")
print(f"Auth key (hex): {auth_key.hex() if auth_key is not None else None}")
