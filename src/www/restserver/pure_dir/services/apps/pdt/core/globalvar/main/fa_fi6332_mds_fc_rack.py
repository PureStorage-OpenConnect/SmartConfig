import os
import glob

from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.components.common import get_device_list
from pure_dir.services.utils.miscellaneous import parse_xml
from pure_dir.global_config import get_discovery_store


class fa_fi6332_mds_fc_rack:
    def __init__(self):
        pass

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_mds_list(self, keys):
        res = result()
        mds_list = get_device_list(device_type="MDS")
        res.setResult(mds_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def esxiimages(self, keys):
        res = result()
        img_list = []
        images = [os.path.basename(fn) for fn in glob.glob(
            '/mnt/system/uploads/Vmware*.iso')]
        if len(images) > 0:
            selected = "1"
            for img in images:
                if img_list:
                    selected = "0"
                img_list.append(
                    {"id": img, "selected": selected, "label": img})
            print img_list
            res.setResult(img_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res
        res.setResult(img_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getpurelist(self, keys):
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_all_ucs_list(self, keys):
        res = result()
        info_list = []
        if os.path.exists(get_discovery_store()) is True:
            doc = parse_xml(get_discovery_store())
            for subelement in doc.getElementsByTagName("device"):
                if subelement.getAttribute("device_type") == "UCSM":
                    details = {}
                    details['label'] = subelement.getAttribute("name")
                    details['id'] = subelement.getAttribute("mac")
                    details['selected'] = "0"
                    info_list.append(details)
        res.setResult(info_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    """def gen_hex(self, length):
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

    def get_ucs_mac_address_A(self, keys):
        res = result()
        mac_list_A = []
        mac_A = ('00', self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(1) + 'A', self.gen_hex(2))
        macA = ':'.join(mac_A)[3:]
        mac_list_A.append({"id": macA, "label": macA, "selected": "0"})
        res.setResult(mac_list_A, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ucs_mac_address_B(self, keys):
        res = result()
        mac_list_B = []
        mac_B = ('00', self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(1) + 'B', self.gen_hex(2))
        macB = ':'.join(mac_B)[3:]
        mac_list_B.append({"id": macB, "label": macB, "selected": "0"})
        res.setResult(mac_list_B, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ucs_wwnn(self, keys):
        res = result()
        wwnn_list = []
        wwnn = ('20', self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2))
        wwnn_pool = ':'.join(wwnn)[3:]
        wwnn_list.append({"id": wwnn_pool, "label": wwnn_pool, "selected": "0"})
        res.setResult(wwnn_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ucs_wwpn_A(self, keys):
        res = result()
        wwpn_list_A = []
        wwpn_A = ('20', self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2),'0A','00')
        wwpn_pool_A = ':'.join(wwpn_A)[3:-6]
        wwpn_list_A.append({"id": wwpn_pool_A, "label": wwpn_pool_A, "selected": "0"})
        res.setResult(wwpn_list_A, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ucs_wwpn_B(self, keys):
        res = result()
        wwpn_list_B = []
        wwpn_B = ('20', self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2), self.gen_hex(2),'0B','00')
        wwpn_pool_B = ':'.join(wwpn_B)[3:-6]
        wwpn_list_B.append({"id": wwpn_pool_B, "label": wwpn_pool_B, "selected": "0"})
        res.setResult(wwpn_list_B, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res"""
