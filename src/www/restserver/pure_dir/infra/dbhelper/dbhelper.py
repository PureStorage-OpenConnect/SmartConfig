import json
from pure_dir.services.common.dbservice.client.dbserviceclient import *
from pure_dir.infra.apiresults import *


class DataOperation:
    def __init__(self, cname, path):
        self.cname = cname  # container Name
        self.path = path

    def AddObject(self, objname):
        if self.path == ".":
            # this is a new container
            key = self.cname + "." + objname
            oldkey = objname
        else:
            key = self.cname + "." + self.path + "." + objname
            #oldkey = self.cname + "." + self.path
            oldkey = self.path + "." + objname

        value = "{}"
        res = AddObject_request(key, value)
        if res.getStatus() != PTK_OKAY:
            return None
        ret = res.getResult()['data']
        return DataOperation(self.cname, oldkey)

    def addAttribute(self, key, value):
        if self.path == ".":
            # this is a new container
            key = self.cname + "." + key
        else:
            key = self.cname + "." + self.path + "." + key
        value = json.dumps(value)
        # value="\"{}\""
        #res= AddObject_request(key, "\"{}\"")

        res = AddObject_request(key, value)
        return self

    def deleteAttribute(self, key):
        if self.path == ".":
            key = self.cname + "." + key
        else:
            key = self.cname + "." + self.path + "." + key
        res = DeleteObject_request(key)
        if res.getStatus() != PTK_OKAY:
            return None

    def getAttribute(self, key):
        if self.path == ".":
            key = self.cname + "." + key
        else:
            key = self.cname + "." + self.path + "." + key
        res = GetObject_request(key)
        if res.getStatus() != PTK_OKAY:
            return res

        return res.getResult()['data']['val']


def createContainer(name):
    value = "{}"
    res = AddObject_request(name, value)
    if res.getStatus() != PTK_OKAY:
        return None

    return DataOperation(name, ".")  # path will be "."


def getContainer(name):
    if '.' in name:
        ret = result()
        ret.setResult(None, PTK_FAILED, "Invalid Container Name")
    res = GetObject_request(name)
    if res.getResult()['data']['val'] == "":
        return None
    return DataOperation(name, ".")


def getContainerData(name):
    res = GetObject_request(name)
    if res.getStatus() != PTK_OKAY:
        return res
    return res.getResult()['data']['val']


def deleteContainer(name):
    res = DeleteObject_request(name)
    return res.getResult()['data']
