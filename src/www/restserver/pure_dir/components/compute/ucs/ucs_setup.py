from ucsmsdk.ucshandle import UcsHandle
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs import *
from pure_dir.components.common import *
from ucsmsdk.mometa.firmware.FirmwareDownloader import FirmwareDownloader


class UCSSetup:

    def __init__(self, ipaddress='', username='', password=''):
        try:
            self.handle = UcsHandle("10.132.242.158", "qqq", "ss")
            self.handle_status = self.handle.login()
        except:
            self.handle = None

    def ucsDownloadFirmware(self):
        obj = result()
        loginfo("Download Firmware")

        if self.handle == None or self.handle_status != True:
            obj.setResult(None,   PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = FirmwareDownloader(parent_mo_or_dn="sys/fw-catalogue", protocol="sftp", file_name="ucs-6300-k9-bundle-infra.3.1.3a.A.bin",
                                server="10.132.243.97", pwd="root", admin_state="restart", user="root", remote_path="/root")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create IQN Pools for iSCSI Boot\n", logfile)
            return False


a = UCSSetup()
d = a.ucsDownloadFirmware()
