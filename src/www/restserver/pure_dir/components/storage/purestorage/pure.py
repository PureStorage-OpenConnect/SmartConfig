import urllib3
from purestorage import FlashArray
from purestorage import PureHTTPError
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


from pure_dir.infra.logging.logmanager import loginfo

pure_credentials_store = "/mnt/system/pure_dir/pdt/purelogin.xml"


class PureHelper:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __init__(self, ipaddress, username, password):
        #self.handle =  FlashArray(ipaddress, username, password, verify_https=False)
        pass

    def purelogin(self, ipaddress, username, password):
        res = result()
        handle = self._pure_handler(ipaddress, username, password)
        if handle != None:
            self._release_pure_handler(handle)
            res.setResult("", PTK_OKAY, "success")
        else:
            res.setResult("", PTK_INTERNALERROR, "failure")
        return res

    def _pure_handler(self, ipaddress="", username="", password=""):
        try:
            handle = FlashArray(ipaddress, username,
                                password, verify_https=False, user_agent="PureStorage SmartConfig /1.2 (Python, CentOS 7.4)")
            return handle
        except Exception as e:
            loginfo("Unable to get purestorage handle")
            loginfo("Error code {} and reason {}".format(e.code, e.reason))
            return None

    def _release_pure_handler(self, handle):
        # handle.logout()
        handle.invalidate_cookie()
