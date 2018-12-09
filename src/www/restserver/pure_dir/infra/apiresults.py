#!/usr/bin/env python
# Project_Name    :pure-director
# title           :aoiresults.py
# description     :Api result
# author          :Abhilash
# date            :12/09/16
# version         :1.0
# =======================================================================

PTK_OKAY = 0  # Success
PTK_CONFIRMCHK = 1  # Confirmation Check
PTK_ALREADYEXIST = -1  # Resouce already exist
PTK_PWDMISMATCH = -2  # Password is Mismatch
PTK_INTERNALERROR = -3  # Unexpected Internal Error
PTK_NOTEXIST = -4  # Resource Not Exist
PTK_SESSIONNOTEXIST = -5  # Session Doesn't Exist
PTK_CURRENTUSERDELETE = -6  # Current User cant be deleted
PTK_INVALIDRESPONSE = -7  # Invalid response from API
PTK_PRECHECKFAILURE = -7  # unmet dependency
PTK_FILEACCESSERROR = -8  # file access error
PTK_CLIERROR = -9  # Switch CLI error
PTK_RESOURCENOTAVAILABLE = -10  # resource not available
PTK_PARTIAL_SUCCESS = -11  # partialy successfull operation
PTK_FAILED = -12  # operation failed


def parseResult(obj):
    return {"data": obj.result, "status": obj.status}


class result:
    def __init__(self):
        self.result = None
        self.status = {PTK_INVALIDRESPONSE, None}
        return

    def setResult(self, result, status, msg):
        self.result = result
        self.status = {'code': status, 'message': msg}

    def getResult(self):
        return self.result

    def getMsg(self):
        return self.status['message']

    def getStatus(self):
        return self.status['code']
