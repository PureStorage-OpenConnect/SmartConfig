from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.common import *
import ucsmsdk
from ucsmsdk.ucshandle import UcsHandle
from pure_dir.infra.apiresults import *


def get_ucs_handle(mac):
    # gets ucs tasks handler
    res = result()
    cred = get_device_credentials(
        key="mac", value=mac)
    if not cred:
        loginfo("Unable to get the device credentials of the UCS")
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get the device credentials of the UCS")
        return res

    obj = UCSTasks(cred['vipaddress'],
                   cred['username'],
                   cred['password'])
    if obj != None:
        res.setResult(obj, PTK_OKAY,
                      "success")
    else:
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get the device credentials of the UCS")

    return res


def get_ucs_login(mac):
    res = result()
    cred = get_device_credentials(
        key="mac", value=mac)
    if not cred:
        loginfo("Unable to get the device credentials of the UCS")
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get the device credentials of the UCS")
        return res
    try:
        handle = UcsHandle(cred['vipaddress'],
                           cred['username'], cred['password'])
        handle_status = handle.login()
        if handle_status == False:
            res.setResult(None, PTK_INTERNALERROR,
                          "Unable to get  UCS handle")
            return res

        res.setResult(handle, PTK_OKAY,
                      "success")
        return res
    except:
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get  UCS handle")
        return res


def ucsm_logout(handle):
    ret = result()
    try:
        handle.logout()
    except UcsException as e:
        customlogs(str(e), logfile)
        ret.setResult(
            None,
            PTK_INTERNALERROR,
            "failed to release the handle")
        return ret

    ret.setResult(None, PTK_OKAY, "Success")
    return ret
