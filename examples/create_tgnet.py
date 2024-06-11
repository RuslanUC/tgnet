from tgnet import Tgnet

tgdata = Tgnet.default()

dc_id = int(input("Dc id: "))
auth_key = bytes.fromhex("Auth key (in hex): ")

tgdata.set_auth_key(dc_id, auth_key, "perm")
tgdata.set_current_dc(dc_id)

tgnet_out_path = input("Output tgnet.dat path: ")
tgdata.save(tgnet_out_path)
