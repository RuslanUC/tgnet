from tgnet import Tgnet

tgnet_path = input("tgnet.dat path: ")

tgdata = Tgnet(tgnet_path)

new_dc_id = int(input("New dc id: "))
new_auth_key = bytes.fromhex("New auth key (in hex): ")

tgdata.set_auth_key_perm(new_dc_id, new_auth_key)
# Or
new_dc = tgdata.get_datacenter(new_dc_id)
new_dc.reset()  # Optional
new_dc.set_auth_key_perm(new_auth_key)

tgdata.set_current_datacenter_id(new_dc_id)

tgnet_out_path = input("new tgnet.dat path: ")
tgdata.save(tgnet_out_path)
