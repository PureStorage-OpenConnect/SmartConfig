from pure_dir.components.compute.ucs.ucs_tasks import UCSTasks
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_credentials
from ucsmsdk.ucsexception import UcsException
from ucsmsdk.ucshandle import UcsHandle
from pure_dir.infra.apiresults import PTK_INTERNALERROR, PTK_OKAY, result
import time


def get_ucs_handle(mac):
    """
    Get UCS tasks handler

    :param mac: UCSM FI mac address
    :return UCS task handle
    """
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
    if obj is not None:
        res.setResult(obj, PTK_OKAY,
                      "success")
    else:
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get the device credentials of the UCS")

    return res


def get_ucs_login(mac):
    """
    Get UCS login handle

    :param mac: UCSM FI mac address
    :return UCS login status
    """

    res = result()
    cred = get_device_credentials(
        key="mac", value=mac)
    if not cred:
        loginfo("Unable to get the device credentials of the UCS")
        res.setResult(None, PTK_INTERNALERROR,
                      "Unable to get the device credentials of the UCS")
        return res
    retry = 0
    while retry < 10:
        try:
            handle = UcsHandle(cred['vipaddress'],
                               cred['username'], cred['password'])
            handle_status = handle.login()
            if not handle_status:
                res.setResult(None, PTK_INTERNALERROR,
                              "Unable to get  UCS handle")
                return res
            res.setResult(handle, PTK_OKAY,
                          "success")
            return res
        except BaseException as e:
            loginfo("Caught Base Exception. Unable to get UCS Handle " + str(e))
            if retry == 9:
                loginfo("Maximum attempt reached. Unable to get UCS handle")
                res.setResult(None, PTK_INTERNALERROR,
                              "Unable to get  UCS handle")
                return res
            else:
                loginfo("Unable to get UCS handle. Retrying once more")
                time.sleep(30)
                retry += 1

def ucsm_logout(handle):
    """
    Logout of UCSM

    :param handle: UCS handle
    :return UCS logout status
    """

    ret = result()
    try:
        handle.logout()
    except UcsException as e:
        ret.setResult(
            None,
            PTK_INTERNALERROR,
            "failed to release the handle")
        return ret

    ret.setResult(None, PTK_OKAY, "Success")
    return ret
