import os
import datetime
import glob
import time
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from ucsmsdk.ucseventhandler import UcsEventHandle
from ucsmsdk.mometa.top.TopSystem import TopSystem
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.firmware.FirmwareCatalogue import FirmwareCatalogue
from ucsmsdk.mometa.firmware.FirmwareDownloader import FirmwareDownloader
from ucsmsdk.mometa.firmware.FirmwareDownloader import FirmwareDownloaderConsts
from ucsmsdk.mometa.firmware.FirmwareAck import FirmwareAckConsts
from pure_dir.services.utils.miscellaneous import *
from pure_dir.components.common import *
import getpass

infra_timeout = 1800
blade_timeout = 1800
image_dir = "/mnt/system/uploads"
settings = "/mnt/system/pure_dir/pdt/settings.xml"


def ucsm_upgrade(ip, username, password, infra='', blade='', logfile=''):
    """
    Upgrade UCS Manager
    :param ip: UCSM FI IP Address
    :param username: FI username
    :param password: FI password
    :infra: Infra image
    :blade: Blade image
    :logfile: handle logging
    :return : ucs upgrade status
    """
    start_time = time.time()
    loginfo(start_time)
    handle = UcsHandle(ip, username, password)
    handle.login()
    if infra:
        loginfo("Starting infra upgrade. Selected bundle %s" % infra)
        loginfo("Uploading image %s to UCS" % infra)
        if not upload_image_to_ucs([infra], handle, image_dir):
            handle.logout()
            return False, "Failed to upload image"
        status, msg = validate_infra(handle, infra)
        if status:
            if not firmware_activate_infra(handle, get_version(infra)):
                handle.logout()
                loginfo("Failed to perform infra upgrade")
                return False, "Failed to perform infra upgrade"
            loginfo("Infra upgrade done for UCS. Waiting for completion.")

            diff_seconds = 0
            #loginfo("Sleep for 2700 seconds")
            #time.sleep(5*60)
            cnt = 0
            upgrade_version = get_version(infra)
            while (True):
              cnt = cnt + 1
              if cnt > 40:
                loginfo("Running and upgrade version same, Upgraded exiting")
                break
              running_version = get_running_version(ip, username, password)
              loginfo("Running version "+ running_version +"Upgrade version "+upgrade_version)
              if running_version != '' and running_version == upgrade_version:
                  loginfo("Running and upgrade version same, Upgraded exiting")
                  break
              time.sleep(60)

            #time.sleep(2700)
            infra_time = str(time.time())
            ucsm_up = False
            while not ucsm_up and diff_seconds < infra_timeout:
                (error, status) = execute_remote_command(
                    ip, username, password, "show version")
                if status is False:
                    loginfo("UCS is still not active. Retrying")
                    time.sleep(10)
                    diff_seconds = int(time.time()) - int(float(infra_time))
                else:
                    loginfo("UCS is up")
                    ucsm_up = True

            status = True
            while status:
                loginfo("checking firmware version in FI-A and B")
                running_version = check_version_FIs(ip, username, password, upgrade_version, "switch")
                if all(running_version):
                    status =False
                    loginfo("Infra upgrade for ucs completed {}".format(upgrade_version))
                time.sleep(30)
            
            retry = 0 
            while retry < 15: 
                try:
                    handle = UcsHandle(ip, username, password)
                    handle.login()
                    loginfo("Checking for infra upgrade completion")
                    
                    status, msg = check_infra_completion(handle, get_version(infra))
                    if not status:
                        handle.logout()
                        loginfo(msg)
                        return False, msg
                    loginfo("Infra upgrade for UCS completed successfully")
                    break
                except Exception:
                    loginfo("unable to get handle, FIs are rebooting")
                    retry +=1
                    time.sleep(20) 
        handle.logout()

    if blade:
        customlogs("Selected bundle %s" % blade, logfile)
        customlogs("Uploading %s to UCS" % blade, logfile)
        if not upload_image_to_ucs([blade], handle, image_dir):
            customlogs("Failed to upload image to UCS", logfile)
            return False, "Failed to upload image"
        customlogs("Upload done", logfile)
        handle = UcsHandle(ip, username, password)
        handle.login()
        time.sleep(120)
        if validate_blade(handle, blade):
            if not firmware_activate_blade(handle, get_version(blade)):
                customlogs("Failed to perform blade firmware upgrade", logfile)
                return False, "Failed to perform blade firmware upgrade"
            customlogs(
                "Blade firmware upgrade done for UCS. Waiting for completion", logfile)

            diff_seconds = 0
            loginfo("Sleep for 900 seconds")
            time.sleep(900)
            blade_time = str(time.time())
            loginfo("Checking for blade server upgrade completion")
            while diff_seconds < blade_timeout:
                status, msg = check_blade_completion(
                    handle, get_version(blade))
                if status is False:
                    loginfo(msg)
                    loginfo(
                        "Blade firmware upgrade yet to complete. Checking the status again")
                    time.sleep(10)
                    diff_seconds = int(time.time()) - int(float(blade_time))
                else:
                    return True, "Blade firmware upgrade completed successfully"

            customlogs(
                "Time exceeded. Failed to perform blade firmware upgrade", logfile)
            return False, "Time exceeded. Failed to perform blade firmware upgrade"
   
    loginfo("verifying FI is swapped or not")
    status = True
    while status:
        error, cluster_state = execute_remote_command(ip, username, password, "show cluster state")
        state = [i.lower() for i in cluster_state.split("\n") if 'A:' in i or 'B:' in i]
        if all([True if 'up' in i else False for i in state]):
            result, output = check_FI()
            if not result:
               return False, output
            loginfo(output)
            status = False
        time.sleep(10)

    retry = 0
    while retry < 15:
        try:
            handle = UcsHandle(ip, username, password)
            handle.login()
            handle.logout()
            break
        except Exception:
            loginfo("unable to get handle FI's are rebooting")
            retry +=1
            time.sleep(20)

    loginfo(time.time() - start_time)

    loginfo("UCS upgrade completed successfully")
    return True, "UCS upgrade completed successfully"


def ucsm_validate_upgrade(handle, infra='', blade=''):
    """
    Validate for UCSM upgrade
    :param handle: UCSM login handle
    :infra: Infra image
    :blade: Blade image
    :return : ucs validation status
    """

    res = result()
    if infra:
        status, msg = validate_infra(handle, infra)
        if not status:
            res.setResult(False, PTK_INTERNALERROR, msg)
            return res
    if blade:
        status, msg = validate_blade(handle, blade)
        if not status:
            res.setResult(False, PTK_INTERNALERROR, msg)
            return res

    res.setResult(True, PTK_OKAY, "Success")
    return res


def validate_infra(handle, image):
    """
    Validate infra image
    :param handle: UCSM login handle
    :image: Infra image
    :return : ucs infra running version status
    """

    version = get_version(image)
    running_version = handle.query_dn(
        "sys/mgmt/fw-system").package_version[:-1]
    if version == running_version:
        return False, "UCS is already running in same version"
    """
    elif version < running_version:
        return False, "UCS is already running at a higher version"
    """
    return True, ""



def validate_blade(handle, image):
    """
    Validate blade image
    :param handle: UCSM login handle
    :image: Blade image
    :return : ucs blade running version status
    """
    version = get_version(image)
    blades = handle.query_classid("ComputeBlade")
    for blade in blades:
        running_version = _get_blade_firmware_running(
            handle, blade).package_version[:-1]
        if version == running_version:
            return False, "Blade is already running in same version"
        """
        elif version < running_version:
            return False, "Blade is already running at a higher version"
	"""
    return True, ""


def check_infra_completion(handle, version):
    """
    Verify if infra upgrade is completed
    :param handle: UCSM login handle
    :version: Infra version to upgrade
    :return : ucs infra upgrade status
    """
    running_version = handle.query_dn(
        "sys/mgmt/fw-system").package_version[:-1]
    if version == running_version:
        running_version_A = handle.query_dn(
            "sys/switch-A/mgmt/fw-system").package_version[:-1]
        running_version_B = handle.query_dn(
            "sys/switch-B/mgmt/fw-system").package_version[:-1]
        if version == running_version_A and version == running_version_B:
            return True, ""
        else:
            return False, "Fabric interconnects still not upgraded"
    else:
        return False, "UCS Manager still not upgraded"


def check_blade_completion(handle, version):
    """
    Verify if blade upgrade is completed
    :param handle: UCSM login handle
    :version: Blade version to upgrade
    :return : ucs blade upgrade status
    """
    blades = handle.query_classid("ComputeBlade")
    for blade in blades:
        running_version = _get_blade_firmware_running(
            handle, blade).package_version[:-1]
        if running_version and version != running_version:
            msg = "Blade server %s still not upgraded" % blade
            return False, msg
    return True, ""


def firmware_activate_infra(handle, version):
    """
    Activate infra bundle on UCSM
    :param handle: UCSM login handle
    :version: version
    :return : infra upgrade completion status
    """

    loginfo("Infrastructure upgrade started. Upgrading to %s" % version)
    try:
        infra_bundle_version = version + "A"
        firmware_infra_pack = handle.query_classid(
            class_id="FirmwareInfraPack")[0]
        firmware_infra_pack.infra_bundle_version = infra_bundle_version
        handle.set_mo(firmware_infra_pack)
        handle.commit()

        loginfo("Acknowledging switch reboot")
        firmware_ack = handle.query_dn('sys/fw-system/ack')
        firmware_ack.adminState = FirmwareAckConsts.ADMIN_STATE_TRIGGER_IMMEDIATE
        handle.set_mo(firmware_ack)
        handle.commit()

        handle.logout()
        return True

    except Exception as e:
        loginfo("Failed to upgrade Infrastructure bundle")
        loginfo(e)
        return False


def firmware_activate_blade(handle, version):
    """
    Activate blade bundle on UCSM
    :param handle: UCSM login handle
    :version: version
    :return : blade upgrade completion status
    """
    loginfo("Blade server upgrade started. Upgrading to %s" % version)
    try:
        blade_bundle = version + "B"

        host_firmware_packs = []
        firmware_running_map = {}

        blades_ = handle.query_classid("ComputeBlade")
        blades = sorted(blades_, key=lambda blade_: blade_.dn)
        for blade in blades:
            blade_dn = blade.dn
            firmware_running = _get_blade_firmware_running(handle, blade)
            if not firmware_running:
                loginfo("Improper firmware on blade '%s'" % blade_dn)
                continue
            firmware_running_map[blade_dn] = [firmware_running,
                                              blade.assigned_to_dn]
            if firmware_running.version == version:
                loginfo("Blade ('%s') running software version already at version: '%s'" % (
                    blade_dn, version))
                continue
            else:
                loginfo("Blade ('%s') is running at version '%s': Expected '%s'" % (
                    blade_dn, firmware_running.version, version))
                assigned_to_dn = blade.assigned_to_dn
                if not assigned_to_dn:
                    host_firmware_pack_dn = "org-root/fw-host-pack-default"
                else:
                    sp = handle.query_dn(assigned_to_dn)
                    host_firmware_pack_dn = sp.oper_host_fw_policy_name

                if host_firmware_pack_dn in host_firmware_packs:
                    continue

                host_firmware_pack = handle.query_dn(host_firmware_pack_dn)
                host_firmware_pack.blade_bundle_version = blade_bundle

                handle.set_mo(host_firmware_pack)
                handle.commit()

                sps = handle.query_classid(class_id="LsServer")
                for sp in sps:
                    if sp.type == 'instance' and sp.assoc_state == 'associated':
                        if sp.oper_host_fw_policy_name and \
                                sp.oper_host_fw_policy_name == \
                                host_firmware_pack_dn:
                            dn = sp.dn + '/ack'
                            ls_maint_ack = handle.query_dn(dn)
                            if ls_maint_ack:
                                ls_maint_ack.admin_state = 'trigger-immediate'
                                handle.set_mo(ls_maint_ack)
                                handle.commit()
                                loginfo(
                                    "Acknowledging blade '%s', service profile '%s' using hostfirmwarepack '%s'" %
                                    (sp.pn_dn, sp.dn, sp.oper_host_fw_policy_name))
                host_firmware_packs.append(host_firmware_pack_dn)
        return True

    except Exception as e:
        loginfo("Failed to upgrade blade server")
        loginfo(e)
        return False


def upload_image_to_ucs(bundles, handle, image_dir):
    """
    Check if image is already available in UCS and perform upload
    :param handle: UCSM login handle
    :image_dir: UCS image directory
    :return : image upload status
    """

    try:
        # check if image is already available in ucs
        images_to_upload = []
        for image in bundles:
            if not is_image_available_on_ucsm(handle, image):
                images_to_upload.append(image)

        # Uploading images to ucs
        for image in images_to_upload:
            loginfo("Uploading image '%s' to UCS" % image)
            firmware, status = firmware_add_local(handle, image_dir, image)
            if not status:
                loginfo("Failed to upload image to UCS")
                return False
            eh = UcsEventHandle(handle)
            eh.add(managed_object=firmware, prop="transfer_state",
                   success_value=['downloaded'], poll_sec=30,
                   timeout_sec=600)
            loginfo("Upload of image file '%s' is completed" % image)
        return True

    except Exception as e:
        loginfo("Failed to upload image to UCS")
        loginfo(e)
        return False


def firmware_add_local(handle, image_dir, image_name, timeout=10 * 60):
    """
    Downloads the firmware image on ucsm from local server
    :param handle: UCSM login handle
    :param image_dir: path of download directory
    :param image_name: firmware image name
    :param timeout: timeout in seconds
    :return firmwaredownloader managed object
    """
    try:
        host = get_ip_address(get_filtered_ifnames()[0])
        user=getpass.getuser()
        phrase=decrypt(get_xml_element(settings, 'phrase')[1][0]['phrase'])
        file_path = os.path.join(image_dir, image_name)

        if not os.path.exists(file_path):
            loginfo("File does not exist")
            return "", False

        top_system = TopSystem()
        firmware_catalogue = FirmwareCatalogue(parent_mo_or_dn=top_system)
        #modified protocol to SCP to support large image uploads
        firmware_downloader = FirmwareDownloader(parent_mo_or_dn=firmware_catalogue, file_name=image_name, pwd=phrase, 
                                                 remote_path=image_dir, server=host, user=user, protocol="scp")
        firmware_downloader.admin_state = FirmwareDownloaderConsts.ADMIN_STATE_RESTART

        handle.add_mo(firmware_downloader, modify_present=True)
        handle.commit()

        start = datetime.datetime.now()
        while not firmware_downloader.transfer_state == "downloaded":
            firmware_downloader = handle.query_dn(firmware_downloader.dn)
            if firmware_downloader.transfer_state == "failed":
                loginfo("Download of '%s' failed. Error: %s" %
                        (image_name,
                         firmware_downloader.fsm_rmt_inv_err_descr))
                return "", False
            if (datetime.datetime.now() - start).total_seconds() > timeout:
                loginfo("Download of '%s' timed out" % image_name)
                return "", False

        return firmware_downloader, True

    except Exception as e:
        loginfo(str(e))
        loginfo("Download of image failed in firmware add local")
        return "", False

def is_image_available_on_ucsm(handle, image):
    """
    Check if image file is already uploaded in UCS
    :param image: image
    :return :image file available status
    """
    loginfo("Checking if image file: '%s' is already uploaded to UCS" % image)
    deleted = False
    filter_str = '(name, %s, type="eq")' % image
    firmware_package = handle.query_classid(
        class_id="FirmwareDistributable", filter_str=filter_str)
    if firmware_package:
        firmware_dist_image = handle.query_children(
            in_mo=firmware_package[0], class_id="FirmwareDistImage")
        if firmware_dist_image:
            firmware_dist_image = firmware_dist_image[0]
            if firmware_dist_image.image_deleted != "":
                deleted = True

    if deleted or not firmware_package:
        loginfo("Image file '%s' is not available on UCS" % image)
        return False
    else:
        loginfo("Image file '%s' is available on UCS" % image)
        return True


def image_name_ucs(handle, image):
    """
    checking the name of the existing image
    :param image: image eg:ucs-k9-bundle-b-series.4.0.1d.B.bin|gbin
    :return :name of the image
    """

    loginfo("checking image name in ucs %s" % image)
    filter_str = '(name, %s, type="re")' % image
    firmware_package = handle.query_classid(
        class_id="FirmwareDistributable", filter_str=filter_str)
    if firmware_package:
        firmware_image_name = firmware_package[0].name
        return firmware_image_name
    else:
        return ""


def _get_blade_firmware_running(handle, blade):
    """
    Get running firmware version
    :param handle:UCS login handle
    :param blade: ComputeBlade managed object
    :return: firmwareRunning managed object
    """

    mgmt_controllers = handle.query_children(in_mo=blade,
                                             class_id="MgmtController")

    for mgmt_controller in mgmt_controllers:
        if mgmt_controller.subject == "blade":
            firmware_runnings_ = handle.query_children(
                in_mo=mgmt_controller, class_id="FirmwareRunning")
        elif mgmt_controller.subject == "rack":
            firmware_runnings_ = handle.query_children(
                in_mo=mgmt_controller, class_id="FirmwareRunning")
            print(firmware_runnings_)

    firmware_runnings = []
    for firmware_running_ in firmware_runnings_:
        if firmware_running_.deployment == "system":
            firmware_runnings.append(firmware_running_)

    if not firmware_runnings or len(firmware_runnings) != 1:
        loginfo("Improper firmware running")
        return None

    firmware_running = firmware_runnings[0]
    return firmware_running


def ucsinfraimages():
    """
    Get UCS infra images
    :return: infra image
    """

    res = result()
    images = [os.path.basename(fn) for fn in glob.glob(
        '/mnt/system/uploads/ucs*.A.bin')]
    res.setResult(images, PTK_OKAY, "success")
    return res


def ucsbladeimages(version=''):
    """
    Get UCS blade images
    :return: blade image
    """

    image_list = []
    images = [os.path.basename(fn) for fn in glob.glob(
        '/mnt/system/uploads/ucs*.B.*')]

    for image in images:
        details = {}
        if version:
            details['label'] = get_version(image) + "B"
            details['id'] = get_version(image) + "B"
            details['selected'] = "1"
        else:
            details['label'] = image
            details['id'] = image
            details['selected'] = "0"

        image_list.append(details)

    return image_list


def ucsrackimages(version=''):
    """
    Get UCS blade images
    :return: blade image
    """

    image_list = []
    images = [os.path.basename(fn) for fn in glob.glob(
        '/mnt/system/uploads/ucs*.C.*')]

    for image in images:
        details = {}
        if version:
            details['label'] = get_version(image) + "C"
            details['id'] = get_version(image) + "C"
            details['selected'] = "1"
        else:
            details['label'] = image
            details['id'] = image
            details['selected'] = "0"

        image_list.append(details)

    return image_list


def get_version(image):
    """
    Compute version from the image name
    :return: version
    """
    # TODO: To handle gbin support
    if '.gbin' not in image:
        ver = image[-12:].split('.')
        version = ver[0] + "." + ver[1] + "(" + ver[2] + ")"
    else:
        ver = image[-15:].split('.')
        version = ver[0] + "." + ver[1] + "(" + ver[2] + "." + ver[3] + ")"
    return version

def get_running_version(ip, username, password):
    running_version=""
    retry=0
    while retry < 15:
        try:
            handle = UcsHandle(ip, username, password)
            status = handle.login()
            if status:
                running_version = handle.query_dn(
                    "sys/mgmt/fw-system").package_version[:-1]
                handle.logout()
            break
        except Exception:
            loginfo("Unable to get UCS handle.FI's are rebooting")
            retry +=1
            time.sleep(20)
    return running_version

def _get_running_firmware_version(ip, username, password, subject="system"):
    """
      _get_running_firmware_version(handle)
    """
    running_firmware_list = []
    retry = True
    while retry:
        try:
            handle = UcsHandle(ip, username, password)
            status = handle.login()
            if not status:
                handle.login(force=True)
            filter_str_ = '(subject, ' + subject + ', type="eq")'
            mgmt_controllers = handle.query_classid(class_id="MgmtController",
                                                    filter_str=filter_str_)

            if len(mgmt_controllers) == 0:
                raise Exception("No Mgmt Controller Object with subject %s", subject)

            for mgmt_controller in mgmt_controllers:
                list_ = handle.query_children(in_mo=mgmt_controller,
                                                   class_id="FirmwareRunning")
                for running in list_:
                    running_firmware_list.append(running)
            handle.logout()
            retry=False
            return running_firmware_list
        except Exception as e:
            loginfo("unable to get handle")
            loginfo(str(e))
            retry +=1
            time.sleep(15)

def check_version_FIs(ip, username, password, upgrade_version, subject):
    """
    verify image version in FI A and B
    """
    running_version=[]
    version_obj = _get_running_firmware_version(ip, username, password, subject=subject)
    for system_version in version_obj:
        if 'system' in system_version.rn and 'system' in system_version.deployment:
            loginfo("Running version in {}:{} upgrade version {}".format(system_version.dn.split('/')[1],
                                                                         system_version.package_version[:-1],
                                                                         upgrade_version))
            if upgrade_version == system_version.package_version[:-1]:
                running_version.append(True)
            else:
                running_version.append(False)
    return running_version
