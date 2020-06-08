import os
import glob

from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.components.common import get_device_list
from pure_dir.services.utils.miscellaneous import parse_xml
from pure_dir.global_config import get_discovery_store


class fa_nexus5k_fi_iscsi:
    def __init__(self):
        pass

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 5k")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
