import os
from xml.dom.minidom import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.apiresults import *
import time
from ucsmsdk.ucshandle import UcsHandle
static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'
image_dir = "/mnt/system/uploads/"
esxi_path = '/var/www/html/esxi/'
xml_file = '/mnt/system/pure_dir/pdt/images.xml'


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def encrypt(passwd):
    res = passwd.encode('base64', 'strict')
    return res


def decrypt(passwd):
    res = passwd.decode('base64', 'strict')
    return res


def get_ucsm_type(subelement):
    ipaddress = subelement.getAttribute("ipaddress")
    username = subelement.getAttribute("username")
    password = subelement.getAttribute("password")
    try:
        fi_type = None
        handle = UcsHandle(ipaddress, username, password)
        handle_status = handle.login()
        if handle_status == False:
            return None
        fabrics = handle.query_classid("networkelement")
        mgmtentity = handle.query_classid("MgmtEntity")
        for fabric in fabrics:
            for mgmt in mgmtentity:
                if fabric.oob_if_ip == ipaddress:
                    if fabric.id == mgmt.id:
                        fi_type = mgmt.leadership
        handle.logout()
        return fi_type

    except:
        return None


def get_device_list(device_type):
    info_list = []
    if os.path.exists(static_discovery_store) is True:
        doc = parse_xml(static_discovery_store)
        for subelement in doc.getElementsByTagName("device"):
            if subelement.getAttribute("device_type") == device_type:
                details = {}
                if device_type == "UCSM":
                    #fi_type = get_ucsm_type(subelement)
                    fi_type = subelement.getAttribute("leadership")
                    if fi_type == None or fi_type == "subordinate":
                        continue
                details['label'] = subelement.getAttribute("name")
                details['id'] = subelement.getAttribute("mac")
                details['selected'] = "0"
                info_list.append(details)
        if device_type == "UCSM" and len(info_list) == 1:
            entities = info_list[0]
            entities["selected"] = "1"
    return info_list


def get_device_credentials(key, value):
    status, details = get_xml_element(
        file_name=static_discovery_store, attribute_key=key, attribute_value=value)
    device_credentials = {}
    if status and details:
        device_credentials['ipaddress'] = details[0]['ipaddress']
        if 'vipaddress' in details[0]:
            device_credentials['vipaddress'] = details[0]['vipaddress']
        device_credentials['username'] = details[0]['username']
        decrypt_pwd = decrypt(details[0]['password'])
        device_credentials['password'] = decrypt_pwd
        return device_credentials
    return device_credentials


class Images:

    def __init__(self):
        pass

    def listimages(self, imagetype=''):
        dicts = {}
        images = []
        if os.path.exists(xml_file) is True:
            xmldoc = parse(xml_file)
            image = xmldoc.getElementsByTagName("image")
            for i in image:
                if imagetype:
                    if i.getAttribute("type") == imagetype:
                        dicts = {"name": i.getAttribute(
                            "name"), "type": i.getAttribute("type"), "version": i.getAttribute("version")}
                        images.append(dicts)
                else:
                    dicts = {"name": i.getAttribute(
                        "name"), "type": i.getAttribute("type"), "version": i.getAttribute("version")}
                    images.append(dicts)
            return images
        return images

    def deleteimage(self, file_name):
        img = os.listdir(image_dir)
        if file_name in img:
             path = image_dir
             os.remove(image_dir + file_name)
             doc = parse(xml_file)
             itemlist = doc.getElementsByTagName('image')
             for node in itemlist:
                 if node.attributes['name'].value == file_name:
                     doc.documentElement.removeChild(node)
                     o = open(xml_file, "w+")
                     o.write(pretty_print(doc.toprettyxml(indent="")))
                     o.close()
                     return True
        return False


def get_ucsm_ip(fabric_name):
    if os.path.exists(static_discovery_store) is True:
        doc = parse_xml(static_discovery_store)
        ipaddress = ""
        for subelement in doc.getElementsByTagName("device"):
            if subelement.getAttribute("device_type") == "UCSM":
                if fabric_name == subelement.getAttribute("name"):
                    ipaddress = subelement.getAttribute("vipaddress")
    return ipaddress


def switch_enable_nxapi(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password,
                   timeout=10, look_for_keys=False, allow_agent=False)
    remote_conn = client.invoke_shell()

    remote_conn.send("conf t\n")
    time.sleep(.5)
    remote_conn.send("feature nxapi\n")
    time.sleep(.5)
    remote_conn.send("terminal dont-ask persist\n")
    time.sleep(.5)
    client.close()
    return
