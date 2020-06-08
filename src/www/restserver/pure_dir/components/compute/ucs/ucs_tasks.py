from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs import *
from pure_dir.components.common import *
from pure_dir.services.utils import *
from ucsmsdk.mometa.ls.LsVConAssign import LsVConAssign
from ucsmsdk.mometa.firmware.FirmwareAck import FirmwareAck
from ucsmsdk.mometa.vnic.VnicDefBeh import VnicDefBeh
from ucsmsdk.mometa.vnic.VnicIScsiBootParams import VnicIScsiBootParams
from ucsmsdk.mometa.vnic.VnicIScsiBootVnic import VnicIScsiBootVnic
from ucsmsdk.mometa.vnic.VnicIScsiStaticTargetIf import VnicIScsiStaticTargetIf
from ucsmsdk.mometa.vnic.VnicLun import VnicLun
from ucsmsdk.mometa.vnic.VnicIPv4If import VnicIPv4If
from ucsmsdk.mometa.vnic.VnicIPv4PooledIscsiAddr import VnicIPv4PooledIscsiAddr
from ucsmsdk.mometa.vnic.VnicVlan import VnicVlan
from ucsmsdk.mometa.vnic.VnicIScsiNode import VnicIScsiNode
from ucsmsdk.mometa.lsboot.LsbootVirtualMedia import LsbootVirtualMedia
from ucsmsdk.mometa.lsboot.LsbootSan import LsbootSan
from ucsmsdk.mometa.lsboot.LsbootSanCatSanImage import LsbootSanCatSanImage
from ucsmsdk.mometa.lsboot.LsbootSanCatSanImagePath import LsbootSanCatSanImagePath
from ucsmsdk.ucsmethodfactory import ls_instantiate_n_named_template
from ucsmsdk.ucsbasetype import DnSet, Dn
from ucsmsdk.mometa.equipment.EquipmentChassis import EquipmentChassis
from ucsmsdk.ucsexception import UcsException
from ucsmsdk.mometa.callhome.CallhomeAnonymousReporting import CallhomeAnonymousReporting
from ucsmsdk.mometa.callhome.CallhomeSmtp import CallhomeSmtp
from ucsmsdk.mometa.compute.ComputeServerDiscPolicy import ComputeServerDiscPolicy
from ucsmsdk.mometa.fabric.FabricLanCloud import FabricLanCloud
from ucsmsdk.mometa.compute.ComputeServerMgmtPolicy import ComputeServerMgmtPolicy
from ucsmsdk.mometa.power.PowerMgmtPolicy import PowerMgmtPolicy
from ucsmsdk.mometa.top.TopInfoPolicy import TopInfoPolicy
from ucsmsdk.mometa.compute.ComputePsuPolicy import ComputePsuPolicy
from ucsmsdk.mometa.firmware.FirmwareAutoSyncPolicy import FirmwareAutoSyncPolicy
from ucsmsdk.mometa.compute.ComputeChassisDiscPolicy import ComputeChassisDiscPolicy
from ucsmsdk.mometa.fabric.FabricFcSanEp import FabricFcSanEp
from ucsmsdk.mometa.fabric.FabricFcSanPcEp import FabricFcSanPcEp
from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
from ucsmsdk.mometa.fabric.FabricFcSanPc import FabricFcSanPc
from ucsmsdk.mometa.fabric.FabricFcVsanPc import FabricFcVsanPc
from ucsmsdk.mometa.vnic.VnicLanConnPolicy import VnicLanConnPolicy
from ucsmsdk.mometa.vnic.VnicEther import VnicEther
from ucsmsdk.mometa.storage.StorageLocalDiskConfigPolicy import StorageLocalDiskConfigPolicy
from ucsmsdk.mometa.macpool.MacpoolPool import MacpoolPool
from ucsmsdk.mometa.macpool.MacpoolBlock import MacpoolBlock
from ucsmsdk.mometa.power.PowerPolicy import PowerPolicy
from ucsmsdk.mometa.vnic.VnicSanConnPolicy import VnicSanConnPolicy
from ucsmsdk.mometa.vnic.VnicFc import VnicFc
from ucsmsdk.mometa.vnic.VnicFcIf import VnicFcIf
from ucsmsdk.mometa.bios.BiosVProfile import BiosVProfile
from ucsmsdk.mometa.bios.BiosVfConsistentDeviceNameControl import BiosVfConsistentDeviceNameControl
from ucsmsdk.mometa.bios.BiosVfQuietBoot import BiosVfQuietBoot
from ucsmsdk.mometa.compute.ComputePool import ComputePool
from ucsmsdk.mometa.compute.ComputePooledSlot import ComputePooledSlot
from ucsmsdk.mometa.compute.ComputePooledRackUnit import ComputePooledRackUnit
from ucsmsdk.mometa.compute.ComputeQual import ComputeQual
from ucsmsdk.mometa.processor.ProcessorQual import ProcessorQual
from ucsmsdk.mometa.fabric.FabricEthLanPc import FabricEthLanPc
from ucsmsdk.mometa.fabric.FabricEthLanPcEp import FabricEthLanPcEp
from ucsmsdk.mometa.uuidpool.UuidpoolPool import UuidpoolPool
from ucsmsdk.mometa.uuidpool.UuidpoolBlock import UuidpoolBlock
from ucsmsdk.mometa.vnic.VnicSanConnTempl import VnicSanConnTempl
from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan
from ucsmsdk.mometa.cimcvmedia.CimcvmediaMountConfigPolicy import CimcvmediaMountConfigPolicy
from ucsmsdk.mometa.cimcvmedia.CimcvmediaConfigMountEntry import CimcvmediaConfigMountEntry
from ucsmsdk.mometa.fabric.FabricVConProfile import FabricVConProfile
from ucsmsdk.mometa.fabric.FabricVCon import FabricVCon
from ucsmsdk.mometa.fabric.FabricVsan import FabricVsan
from ucsmsdk.mometa.fcpool.FcpoolInitiators import FcpoolInitiators
from ucsmsdk.mometa.fcpool.FcpoolBlock import FcpoolBlock
from ucsmsdk.mometa.fabric.FabricDceSwSrvEp import FabricDceSwSrvEp
from ucsmsdk.mometa.fabric.FabricEthLanEp import FabricEthLanEp
from ucsmsdk.mometa.qosclass.QosclassEthBE import QosclassEthBE
from ucsmsdk.mometa.comm.CommNtpProvider import CommNtpProvider
from ucsmsdk.mometa.lsmaint.LsmaintMaintPolicy import LsmaintMaintPolicy
from ucsmsdk.mometa.nwctrl.NwctrlDefinition import NwctrlDefinition
from ucsmsdk.mometa.dpsec.DpsecMac import DpsecMac
from ucsmsdk.mometa.firmware.FirmwareComputeHostPack import FirmwareComputeHostPack
from ucsmsdk.mometa.firmware.FirmwareExcludeServerComponent import FirmwareExcludeServerComponent
from ucsmsdk.mometa.vnic.VnicConnDef import VnicConnDef
from ucsmsdk.mometa.vnic.VnicFcNode import VnicFcNode
from ucsmsdk.mometa.ls.LsRequirement import LsRequirement
from ucsmsdk.mometa.ls.LsPower import LsPower
from ucsmsdk.mometa.vnic.VnicIScsi import VnicIScsi
from ucsmsdk.ucshandle import UcsHandle
import time
from ucsmsdk.mometa.iqnpool.IqnpoolPool import IqnpoolPool
from ucsmsdk.mometa.iqnpool.IqnpoolBlock import IqnpoolBlock
from ucsmsdk.mometa.lsboot.LsbootPolicy import LsbootPolicy
from ucsmsdk.mometa.lsboot.LsbootIScsi import LsbootIScsi
from ucsmsdk.mometa.lsboot.LsbootIScsiImagePath import LsbootIScsiImagePath
from ucsmsdk.ucsmethodfactory import ls_clone
from ucsmsdk.mometa.ippool.IppoolPool import IppoolPool
from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock
from ucsmsdk.mometa.bios.BiosVfDRAMClockThrottling import BiosVfDRAMClockThrottling
from ucsmsdk.mometa.bios.BiosVfFrequencyFloorOverride import BiosVfFrequencyFloorOverride
from ucsmsdk.mometa.bios.BiosVfProcessorCState import BiosVfProcessorCState
from ucsmsdk.mometa.bios.BiosVfProcessorC1E import BiosVfProcessorC1E
from ucsmsdk.mometa.bios.BiosVfProcessorC3Report import BiosVfProcessorC3Report
from ucsmsdk.mometa.bios.BiosVfProcessorC7Report import BiosVfProcessorC7Report
from ucsmsdk.mometa.bios.BiosVfLvDIMMSupport import BiosVfLvDIMMSupport
from ucsmsdk.mometa.vnic.VnicIScsiLCP import VnicIScsiLCP
from ucsmsdk.mometa.bios.BiosVfIntelHyperThreadingTech import BiosVfIntelHyperThreadingTech
from ucsmsdk.mometa.bios.BiosVfIntelTurboBoostTech import BiosVfIntelTurboBoostTech
from ucsmsdk.mometa.bios.BiosVfIntelVTForDirectedIO import BiosVfIntelVTForDirectedIO
from ucsmsdk.mometa.bios.BiosVfIntelVirtualizationTechnology import BiosVfIntelVirtualizationTechnology
from ucsmsdk.mometa.bios.BiosVfProcessorEnergyConfiguration import BiosVfProcessorEnergyConfiguration
from ucsmsdk.mometa.bios.BiosVfSelectMemoryRASConfiguration import BiosVfSelectMemoryRASConfiguration
from ucsmsdk.mometa.bios.BiosVfEnhancedIntelSpeedStepTech import BiosVfEnhancedIntelSpeedStepTech
from ucsmsdk.mometa.bios.BiosVfCPUPerformance import BiosVfCPUPerformance
from ucsmsdk.mometa.bios.BiosVfDirectCacheAccess import BiosVfDirectCacheAccess
from ucsmsdk.mometa.ls.LsServer import LsServer
from ucsmsdk.mometa.callhome.CallhomeSource import CallhomeSource
import datetime
import glob
from ucsmsdk.mometa.fabric.FabricSanCloud import FabricSanCloud
from ucsmsdk.mometa.fabric.FabricFcEstcEp import FabricFcEstcEp
from ucsmsdk.mometa.fabric.FabricFcVsanPortEp import FabricFcVsanPortEp
from ucsmsdk.mometa.fabric.FabricEthEstcEp import FabricEthEstcEp
from ucsmsdk.mometa.fabric.FabricEthVlanPortEp import FabricEthVlanPortEp
from pure_dir.components.compute.ucs.ucs_upgrade import is_image_available_on_ucsm, upload_image_to_ucs, image_name_ucs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import get_server_type, get_ucs_upgrade


class UCSTasks:

    def __init__(self, ipaddress='', username='', password=''):
        try:
            if ipaddress:
                self.handle = UcsHandle(ipaddress, username, password)
                self.handle_status = self.handle.login()
        except BaseException:
            self.handle = None

    def release_ucs_handle(self):
        ret = result()
        try:
            self.handle.logout()

        except UcsException:
            loginfo("Failed to release handle")
            ret.setResult(
                None,
                PTK_INTERNALERROR,
                "failed to release the handle")
            return ret

        ret.setResult(None, PTK_OKAY, "Success")
        return ret

    def get_ucs_login(mac):
        """
        Login to UCS Fabric Interconnect

        :param mac: UCS Fabric Interconnect MAC
        :return: Returns the UCS login handle
        """

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
            if not handle_status:
                res.setResult(None, PTK_INTERNALERROR,
                              "Unable to get  UCS handle")
                return res

            res.setResult(handle, PTK_OKAY,
                          "success")
            return res
        except BaseException:
            res.setResult(None, PTK_INTERNALERROR,
                          "Unable to get  UCS handle")
            return res

    def deletebootpolicy(self, inputdict, logfile):
        """
        Delete the UCS Boot policy

        :param inputdict: Dictionary (boot policy)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("delete_boot_policy")

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}

        mo = self.handle.query_dn(
            "org-root/boot-policy-" + inputdict['boot_policy_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()

        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nBoot Policy deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy deletion failed")
            return obj

        customlogs("\nBoot Policy " +
                   inputdict['boot_policy_name'] + " deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Boot Policy deletion successful")
        return obj

    def createbootpolicy(self, inputdict, logfile):
        """
        Create the UCS Boot policy

        :param inputdict: Dictionary (boot policy name,description)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_boot_policy")

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}

        loginfo("Boot Policy Name =" + inputdict['boot_policy_name'])
        loginfo("Boot Policy description =" + inputdict['boot_policy_desc'])
        message = "Boot Policy Name: " + \
                  inputdict['boot_policy_name'] + \
                  "\nBoot Policy Description: " + inputdict['boot_policy_desc']

        customlogs("Create Boot Policy\n", logfile)
        customlogs(message, logfile)

        mo = LsbootPolicy(
            parent_mo_or_dn="org-root",
            name=inputdict['boot_policy_name'],
            descr=inputdict['boot_policy_desc'],
            reboot_on_update="no",
            policy_owner="local",
            enforce_vnic_name="yes",
            boot_mode="legacy")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nBoot Policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy creation failed")
            return obj

        customlogs("\nBoot Policy created successfully \n", logfile)
        dicts['bootpolicyname'] = "org-root/boot-policy-" + \
                                  inputdict['boot_policy_name']
        obj.setResult(dicts, PTK_OKAY, "Boot Policy creation is successful")
        return obj

    def deleteRemoteDiskToBootPolicies(self, inputdict, logfile):
        """
        Remove Remote disk from the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            inputdict['bootpolicyname'] + "/read-only-remote-vm")
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\ndelete Remote Disk To Boot Policies failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "delete Remote Disk To Boot Policies ")
            return obj
        customlogs(
            "Remote disk to boot policy is deleted successfully \n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Delete Remote Disk To Boot Policies  successful")
        return obj

    def addRemoteDiskToBootPolicies(self, inputdict, logfile):
        """
        Add Remote disk to the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(inputdict['bootpolicyname'])
        mo_1 = LsbootVirtualMedia(
            parent_mo_or_dn=mo,
            access="read-only-remote",
            lun_id="0",
            mapping_name="",
            order="1")
        self.handle.add_mo(mo_1)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nAdd Remote disk to Boot Policy failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Add Remote disk to Boot Policy failed")
            return obj
        customlogs(
            "Remote disk to boot policy is added successfully \n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Add Remote Disk to Boot Policy is successful")
        return obj

    def deleteSanBootToBootPolicy(self, inputdict, logfile):
        """
        Delete SAN boot from the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        res_obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            res_obj.setResult(None, PTK_INTERNALERROR,
                              "Unable to connect to UCS")
            return res_obj
        obj = self.handle.query_dn(inputdict['bootpolicyname'])
        mo = LsbootSan(parent_mo_or_dn=obj, order="2")
        mo_1 = self.handle.query_dn(
            inputdict['bootpolicyname'] + "/san/sanimg-" + inputdict['type'])
        self.handle.remove_mo(mo_1)
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException:
            customlogs("\nDelete SAN Boot to boot policy failed\n", logfile)
            res_obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Delete SAN Boot to boot policy failed")
            return res_obj
        customlogs(
            "\n SAN Boot of type " +
            inputdict['type'] + "  with vhba " +
            inputdict['vhba'] + " is deleted successfully \n",
            logfile)
        res_obj.setResult(
            dicts, PTK_OKAY, "Delete SAN Boot to boot policy is successful")
        return res_obj

    def addSanBootToBootPolicy(self, inputdict, logfile):
        """
        Add SAN boot to the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        policy = inputdict['bootpolicyname']
        if inputdict['type'] == "primary":
            mo = self.handle.query_dn(policy)
            mo_1 = LsbootSan(parent_mo_or_dn=mo, order="2")
            LsbootSanCatSanImage(
                parent_mo_or_dn=mo_1,
                type=inputdict['type'],
                vnic_name=inputdict['vhba'])
            self.handle.add_mo(mo_1, True)
        else:
            mo = policy + "/san"
            mo_1 = LsbootSanCatSanImage(
                parent_mo_or_dn=mo,
                type=inputdict['type'],
                vnic_name=inputdict['vhba'])
            self.handle.add_mo(mo_1)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nBoot Policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy creation failed")
            return obj
        customlogs("SAN boot to boot policy is added successfully\n", logfile)
        dicts['type'] = inputdict['type']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Adding san boot to boot policy is successful")
        return obj

    def deleteSanBootTarget(self, inputdict, logfile):
        """
        Delete SAN boot target from the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo_obj = self.handle.query_dn(inputdict['bootpolicyname'])
        mo = LsbootSan(parent_mo_or_dn=mo_obj, order="2")
        LsbootSanCatSanImage(
            parent_mo_or_dn=mo, type=inputdict['san_type'])
        mo_1_1 = self.handle.query_dn(
            inputdict['bootpolicyname'] +
            "/san/sanimg-" +
            inputdict['san_type'] +
            "/sanimgpath-" +
            inputdict['type'])
        self.handle.remove_mo(mo_1_1)
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nDelete SAN Boot Target failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Delete SAN Boot Target failed")
            return obj
        customlogs(
            "\n SAN Boot Target of type " +
            inputdict['type'] +
            " for the SAN Boot type " +
            inputdict['san_type'] +
            " is deleted successfully \n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Delete SAN Boot Target successful")
        return obj

    def addSanBootTarget(self, inputdict, logfile):
        """
        Add SAN boot target to the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        if inputdict['san_type'] == "primary":
            policy = inputdict['bootpolicyname'] + "/san/sanimg-primary"
        else:
            policy = inputdict['bootpolicyname'] + "/san/sanimg-secondary"
        mo = LsbootSanCatSanImagePath(
            parent_mo_or_dn=policy,
            wwn=inputdict['wwpn'],
            type=inputdict['type'],
            lun=inputdict['target_lun'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nBoot Policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy creation failed")
            return obj

        customlogs("SAN Boot Target is added successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Add San Boot Target successful")
        return obj

    def deleteiSCSIBoot(self, inputdict, logfile):
        """
        Delete iSCSI boot target from the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(inputdict['bootpolicyname'] + "/iscsi")
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException:
            customlogs("\nDelete ISCSI Boot failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Delete ISCSI Boot failed")
            return obj

        customlogs("\n iSCSI Boot Target is deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Delete ISCSI Boot Target successful")
        return obj

    def addiSCSIBoot(self, inputdict, logfile):
        """
        Add iSCSI boot target to the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Boot Policy Name =" + inputdict['bootpolicyname'])
        message = "Boot Policy name: " + inputdict['bootpolicyname']
        customlogs("\nAdding iSCSI boot to boot policy\n", logfile)
        customlogs(message, logfile)
        policy = inputdict['bootpolicyname']

        mo = self.handle.query_dn(policy)
        mo_1 = LsbootIScsi(parent_mo_or_dn=mo, order="2")
        LsbootIScsiImagePath(
            parent_mo_or_dn=mo_1,
            i_scsi_vnic_name=inputdict['iSCSI_A_vNIC'],
            type="primary",
            vnic_name="")
        LsbootIScsiImagePath(
            parent_mo_or_dn=mo_1,
            i_scsi_vnic_name=inputdict['iSCSI_B_vNIC'],
            type="secondary",
            vnic_name="")

        self.handle.add_mo(mo_1, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nAdding iSCSI boot to boot policy failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Adding iSCSI boot to boot policy failed")
            return obj

        customlogs(
            "\nAdded iSCSI Boot to boot policy successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Add iSCSI Boot to boot policy successful")
        return obj

    def deleteCimcMountedDisk(self, inputdict, logfile):
        """
        Delete CIMC Mounted disk from the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            inputdict['bootpolicyname'] + "/read-only-remote-cimc-vm")
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nDelete cimc mounted disc failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Delete cimc mounted disc failed")
            return obj

        customlogs(
            "\n Cimc mounted disc from boot policy is deleted successfully \n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Delete cimc mounted disc successful")
        return obj

    def addCimcMountedDisk(self, inputdict, logfile):
        """
        Add Cimc boot target to the UCS Boot policy

        :param inputdict: Dictionary (boot policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(inputdict['bootpolicyname'])
        mo_1 = LsbootVirtualMedia(
            parent_mo_or_dn=mo,
            access="read-only-remote-cimc",
            lun_id="0",
            mapping_name="",
            order="3")
        self.handle.add_mo(mo_1)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nBoot Policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy creation failed")
            return obj
        customlogs("\nCIMC Mounted Disk is added successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "CIMC Mounted Disk added successfully")
        return obj

    def acknowledgeUcsChassis(self, inputdict, logfile):
        """
        Acknowledge Cisco UCS Chassis

        :param inputdict: Dictionary (acknowledge state)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Acknowledge Cisco UCS Chassis")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Acknowledge state: " + inputdict['state'])
        message = "Acknowledge state: " + inputdict['state']
        customlogs("Acknowledge Cisco UCS Chassis", logfile)
        customlogs(message, logfile)

        chassislist = self.handle.query_classid("EquipmentChassis")
        for chassis in chassislist:
            mo = EquipmentChassis(
                parent_mo_or_dn="sys",
                admin_state=inputdict['state'],
                id=chassis.id)
            self.handle.add_mo(mo, True)
        # ucs chassis acknowledgement takes some time after the server ports
        # are configured
        for attempts in range(11):
            if attempts >= 10:

                customlogs("\nAcknowledge Cisco UCS Chassis is successful\n", logfile)
                obj.setResult(dicts,
                              PTK_INTERNALERROR,
                              "Acknowledge UCS Chassis failed")
                return obj
            try:
                self.handle.commit()
            except UcsException as e:
                customlogs(str(e), logfile)
                customlogs(
                    "\n Retrying Acknowledge Cisco UCS Chassis\n", logfile)
                continue
            else:
                break

        # Sleep for blade servers to be discovered
        time.sleep(120)

        customlogs("\nAcknowledge Cisco UCS Chassis is successful\n", logfile)
        dicts['state'] = inputdict['state']
        obj.setResult(dicts, PTK_OKAY, "Acknowledge UCS Chassis successful")
        return obj

    def addBlockIPAddForKVMAccess(self, inputdict, logfile):
        """
        Add Block of IP Address for KVM Access

        :param inputdict: Dictionary (KVM Console IP,Subnet, Gateway)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Add Block of IP Addresses for KVM Access")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "KVM Console IP Range: " + inputdict['kvm_console_ip'] + "\nSubnet mask: " + inputdict[
            'mask'] + \
            "\nGateway: " + inputdict['gateway'] + "\nPrimary DNS: " + \
            inputdict['pri_dns'] + "\nSecondary DNS: " + \
            inputdict['sec_dns']
        loginfo(
            "Add Block of IP Addresses for KVM Access parameters = " +
            message)
        customlogs(message, logfile)

        ip_from = inputdict['kvm_console_ip']
        kvm_ip_range = ip_from.split('-')
        ntwk = network_info()
        kvm_ip_ntwk = ntwk['ip'].split('.')
        kvm_ip_ntwk[3] = kvm_ip_range[0]
        kvm_ip_from = '.'.join(kvm_ip_ntwk)
        kvm_ip_ntwk[3] = kvm_ip_range[1]
        kvm_ip_to = '.'.join(kvm_ip_ntwk)

        mo = IppoolBlock(
            parent_mo_or_dn="org-root/ip-pool-ext-mgmt",
            prim_dns=inputdict['pri_dns'],
            r_from=kvm_ip_from,
            def_gw=inputdict['gateway'],
            sec_dns=inputdict['sec_dns'],
            to=kvm_ip_to)
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nAdd Block of IP Addresses for KVM Access failed\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Add block of IP Addresses for KVM Access failed")
            return obj

        customlogs(
            "\nAdd Block of IP Addresses for KVM Access is successful\n",
            logfile)
        dicts['name'] = "org-root/ip-pool-ext-mgmt/block-" + \
                        kvm_ip_from + "-" + kvm_ip_to
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Add block of IP Addresses for KVM Access successful")
        return obj

    def ucsDeleteKVMIPAddresses(self, inputs, outputs, logfile):
        """
        Delete Block of IP Address for KVM Access

        :param inputdict: Dictionary (KVM Console IP Range)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete KVM IP Address")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(outputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete KVM IP Addresses\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete KVM IP Addresses")
            return obj
        customlogs("Block of KVM IP Addresses deleted successfully", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Block of KVM IP Addresses deleted successfully")
        return obj

    def ucsAnonymousReporting(self, inputdict, logfile):
        """
        Configuration of Anonymous Reporting to Cisco

        :param inputdict: Dictionary (SMTP Server Host, port)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Anonymous reporting")
        dicts = {}
        if self.handle is None or self.handle_status != True:
            loginfo("no handle")
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        loginfo("Admin state = " + inputdict['admin'])
        if 'host' in inputdict:
            loginfo("SMTP server host = " + inputdict['host'])
            loginfo("Port = " + inputdict['port'])
            message = "Admin state: " + inputdict['admin'] + \
                      "\nSMTP server host: " + \
                      inputdict['host'] + "\nPort: " + inputdict['port']
        else:
            message = "Admin state: " + inputdict['admin']
        customlogs(message, logfile)

        obj1 = self.handle.query_dn("call-home")
        mo = CallhomeAnonymousReporting(
            parent_mo_or_dn=obj1,
            admin_state=inputdict['admin'],
            user_acknowledged="no")

        self.handle.add_mo(mo, True)

        if 'host' in inputdict:
            mo = CallhomeSmtp(
                parent_mo_or_dn=obj1,
                host=inputdict['host'],
                port=inputdict['port'])

            self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to update UCS Anonymous reporting settings\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to update UCS Anonymous reporting settings")
            return obj

        customlogs(
            "\nUCS Anonymous reporting settings updated successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "UCS Anonymous reporting settings updated successfully")
        return obj

    def ucsChassisDiscoveryPolicy(self, inputdict, logfile):
        """
        Edit the Chassis Discovery Policy in UCS

        :param inputdict: Dictionary (Chassis Discovery Policy inputs)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Chassis discovery policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Chassis/FEX Discovery Policy" + "\nAction: " + inputdict[
            'fex_action'] + "\nLink Grouping Preference: " + inputdict['agg_pref'] + "\nBackplane Speed Preference: " + \
            inputdict['speed_pref'] + "\nRack Server Discovery Policy" + "\nAction" + inputdict[
            'rack_action'] + "\nScrub Policy: " + inputdict['scrub'] + "\nRack Management Connection Policy: " + \
            inputdict['mgmt_action'] + "\nPower Policy: " + inputdict['redundancy'] + "\nMAC Address Table Aging: " + \
            inputdict['mac_aging'] + "\nGlobal Power Allocation Policy: " + inputdict['style'] + \
            "\nFirmware Auto Sync Server Policy: " + \
            inputdict['sync_state'] + "\nGlobal Power Profiling Policy: " + \
            inputdict['profiling'] + "\nInfo Policy: " + \
            inputdict['info_enable']
        loginfo("Chassis discovery policy parameters = " + message)
        customlogs(message, logfile)

        # Chassis/FEX
        mo = ComputeChassisDiscPolicy(
            parent_mo_or_dn="org-root",
            backplane_speed_pref=inputdict['speed_pref'],
            action=inputdict['fex_action'],
            link_aggregation_pref=inputdict['agg_pref'])
        self.handle.add_mo(mo, True)

        # Rack server
        # ucsmscrubpolicy
        mo = ComputeServerDiscPolicy(
            parent_mo_or_dn="org-root",
            scrub_policy_name=inputdict['scrub'],
            action=inputdict['rack_action'])
        self.handle.add_mo(mo, True)

        # Rack mgmt
        mo = ComputeServerMgmtPolicy(
            parent_mo_or_dn="org-root",
            action=inputdict['mgmt_action'])
        self.handle.add_mo(mo, True)

        # power policy
        mo = ComputePsuPolicy(
            parent_mo_or_dn="org-root",
            redundancy=inputdict['redundancy'])
        self.handle.add_mo(mo, True)
        # mac address
        mo = FabricLanCloud(
            parent_mo_or_dn="fabric",
            mac_aging=inputdict['mac_aging'])
        self.handle.add_mo(mo, True)

        # global power
        mo = PowerMgmtPolicy(
            parent_mo_or_dn="org-root",
            style=inputdict['style'])
        self.handle.add_mo(mo, True)

        # auto sync
        mo = FirmwareAutoSyncPolicy(
            parent_mo_or_dn="org-root",
            sync_state=inputdict['sync_state'])
        self.handle.add_mo(mo, True)

        # global power profiling
        mo = PowerMgmtPolicy(
            parent_mo_or_dn="org-root",
            profiling=inputdict['profiling'])
        self.handle.add_mo(mo, True)

        # info policy
        mo = TopInfoPolicy(
            parent_mo_or_dn="sys",
            state=inputdict['info_enable'])
        self.handle.add_mo(mo, True)

        safe = self.handle.query_classid("ComputeChassisDiscPolicy")
        dicts['speed_pref'] = safe[0].backplane_speed_pref
        dicts['fex_action'] = safe[0].action
        dicts['agg_pref'] = safe[0].link_aggregation_pref
        safe = self.handle.query_classid("ComputeServerDiscPolicy")
        dicts['scrub'] = safe[0].scrub_policy_name
        dicts['rack_action'] = safe[0].action
        safe = self.handle.query_classid("ComputeServerMgmtPolicy")
        dicts['mgmt_action'] = safe[0].action
        safe = self.handle.query_classid("ComputePsuPolicy")
        dicts['redundancy'] = safe[0].redundancy
        safe = self.handle.query_classid("FabricLanCloud")
        dicts['mac_aging'] = safe[0].mac_aging
        safe = self.handle.query_classid("PowerMgmtPolicy")
        dicts['style'] = safe[0].style
        dicts['profiling'] = safe[0].profiling
        safe = self.handle.query_classid("FirmwareAutoSyncPolicy")
        dicts['sync_state'] = safe[0].sync_state
        safe = self.handle.query_classid("TopInfoPolicy")
        dicts['info_enable'] = safe[0].state

        try:
            self.handle.commit()
        except UcsException:
            customlogs("Chassis discovery policy failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Chassis discovery policy failed")
            return obj
        loginfo("Chassis discovery policy updated successfully\n")
        customlogs("\nChassis discovery policy updated successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Chassis discovery policy updated successfully")
        return obj

    def ucsConfigureUnifiedPorts(self, inputdict, logfile):
        """
        Configure Unified Ports

        :param inputdict: Dictionary (Number of ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Configure_Unified_ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("No of Unified Ports to be configured: " +
                inputdict['no_of_ports'])

        message = "\nNo of Unified Ports to be configured: " + \
            inputdict['no_of_ports']

        customlogs(message, logfile)

        parent_mo = "fabric/san/" + inputdict['ucs_fabric_id']
        ports_range = inputdict['no_of_ports'].split('-')
        port_from = int(ports_range[0])
        port_to = int(ports_range[1]) + 1
        for i in range(port_from, port_to):
            i = "%s" % i
            mo = FabricFcSanEp(
                parent_mo_or_dn=parent_mo,
                name="",
                fill_pattern="arbff",
                auto_negotiate="yes",
                usr_lbl="",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nConfiguring Unified ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Configuring Unified ports failed")
            return obj
        dicts['no_of_ports'] = '|'.join(str(i) for i in range(port_from, port_to))
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "Configuring Unified ports successful")

        loginfo("waiting for fabric to reboot after unified ports configuration")
        ucs_mac_id = inputdict['fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for Fabric " + ipaddr +
                   " to reboot after unified ports configuration\n", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of UCS " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)
        customlogs("\nFI rebooted successfully\n", logfile)
        customlogs("Unified Ports configured successfully\n", logfile)
        return obj

    def ucsUnConfigureUnifiedPorts(self, inputdict, logfile):
        """
        Unconfigure the Unified Ports

        :param inputdict: Dictionary (Number of Unified ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UnConfigure_Unified_ports")
        customlogs("UCS Rollback Configure Unified Ports", logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        parent_mo = "fabric/lan/" + inputdict['ucs_fabric_id']
        ports_range = inputdict['no_of_ports'].split('-')
        port_from = int(ports_range[0])
        port_to = int(ports_range[1]) + 1
        for i in range(port_from, port_to):
            i = "%s" % i
            mo = FabricEthLanEp(
                parent_mo_or_dn=parent_mo,
                name="",
                auto_negotiate="yes",
                usr_lbl="",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nUnConfiguring Unified ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "UnConfiguring Unified ports failed")
            return obj

        customlogs("\n Unified Ports unconfigured successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "UnConfiguring Unified ports successful")
        loginfo("waiting for fabric to reboot after unified ports configuration")
        ucs_mac_id = inputdict['fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for Fabric " + ipaddr +
                   " to reboot after rollback of unified ports configuration", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of UCS " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)

        return obj

    def ucsCreateApplicationvNICTemplate(self, inputdict, logfile):
        """
        Create Application vNIC Template

        :param inputdict: Dictionary (Application vNIC Template name,description, template type, mtu, VLAN)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_Application_vNIC_Template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Application vNIC Template Name =" +
                inputdict['application_vnic_templ_name'])
        loginfo("Applictaion vNIC Template Description =" +
                inputdict['application_vnic_templ_desc'])
        loginfo("Fabric ID =" + inputdict['fabric_id'])
        loginfo("Redundancy Pair Type =" + inputdict['redundancy_pair_type'])
        loginfo("Template Type =" + inputdict['templ_type'])
        loginfo("CDN Source =" + inputdict['cdn_source'])
        loginfo("Ident Pool Name =" + inputdict['ident_pool_name'])
        loginfo("Network Control Policy =" + inputdict['nw_ctrl_policy_name'])
        loginfo("MTU =" + inputdict['mtu'])
        loginfo("VLANS =" + inputdict['vlans'])

        message = "Application vNIC Template Name: " + inputdict[
            'application_vnic_templ_name'] + "\nApplication vNIC Template Desc: " + inputdict[
            'application_vnic_templ_desc'] + "\nFabric ID: " + inputdict[
            'fabric_id'] + "\nRedundancy Pair Type: " + inputdict[
            'redundancy_pair_type'] + "\nTemplate Type: " + \
            inputdict['templ_type'] + "\nCDN Source: " + inputdict['cdn_source'] + "\nIdent Pool Name: " + \
            inputdict['ident_pool_name'] + "\nNetwork Control Policy: " + \
            inputdict['nw_ctrl_policy_name'] + "\nMTU: " + inputdict['mtu']

        customlogs(message, logfile)

        mo = VnicLanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_pair_type'],
            name=inputdict['application_vnic_templ_name'],
            descr=inputdict['application_vnic_templ_desc'],
            stats_policy_name="",
            admin_cdn_name="",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            mtu=inputdict['mtu'],
            peer_redundancy_templ_name=inputdict['peer_red_template'] if inputdict[
                'peer_red_template'] != "not-set" else "",
            templ_type=inputdict['templ_type'],
            qos_policy_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            cdn_source=inputdict['cdn_source'],
            nw_ctrl_policy_name=inputdict['nw_ctrl_policy_name'])
        if inputdict['ucs_fabric_id'] == "A":
            if "native_vlan" in inputdict:
                VnicEtherIf(parent_mo_or_dn=mo, default_net="yes",
                            name=inputdict['native_vlan'])

            inputdict['vlans'] = inputdict['vlans'].split('|')
            for name in inputdict['vlans']:
                VnicEtherIf(
                    parent_mo_or_dn=mo,
                    default_net="no",
                    name=name)

        self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Application creation failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Application vNIC creation failed")
            return obj

        customlogs("Application vNIC template is created successfully\n", logfile)
        dicts['application_vnic_templ_name'] = inputdict['application_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "Application vNIC creation successful")
        return obj

    def ucsDeleteApplicationvNICTemplate(self, inputs, outputs, logfile):
        """
        Delete Application vNIC template

        :param inputs: Dictionary (Application vNIC Template name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Application vNIC template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(
            "org-root/lan-conn-templ-" + inputs['application_vnic_templ_name'])
        if mo is None:
            customlogs(
                "\nApplication vNIC template " +
                inputs['application_vnic_templ_name'] +
                " does not exist\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete application vNIC template")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Delete application vNIC template\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete appication vNIC template")
            return obj
        customlogs(
            "\n Application vNIC template " +
            inputs['application_vnic_templ_name'] +
            " deleted successfully\n",
            logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Application vNIC template deleted successfully")
        return obj

    def ucsCreateFCPortChannels(self, inputdict, logfile):
        """
        Create FC Port Channels

        :param inputdict: Dictionary (FC Port Channel Name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create_FC_Port_Channel")

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        loginfo("FC Port Channel Name =" + inputdict['fc_port_channel_name'])
        loginfo("Switch ID =" + inputdict['fabric_id'])
        loginfo("Admin Speed =" + inputdict['admin_speed'])
        loginfo("Port Channel ID =" + inputdict['port_id'])
        loginfo("FC Port List =" + inputdict['port_list'])

        message = "FC Port Channel Name: " + inputdict['fc_port_channel_name'] + "\nSwitch ID: " + inputdict[
            'fabric_id'] + \
            "\nAdmin Speed: " + inputdict['admin_speed'] + "\nPort ID: " + \
            inputdict['port_id'] + "\nVSAN Name: " + \
            inputdict['vsan_name']
        customlogs(message, logfile)
        parent_mo = "fabric/san/" + inputdict['ucs_fabric_id']

        mo = FabricFcSanPc(
            parent_mo_or_dn=parent_mo,
            admin_state="enabled",
            admin_speed=inputdict['admin_speed'],
            port_id=inputdict['port_id'],
            name=inputdict['fc_port_channel_name'],
            descr="")
        ports = inputdict['port_list'].split('|')
        for port in ports:
            FabricFcSanPcEp(
                parent_mo_or_dn=mo,
                name="",
                admin_speed="auto",
                fill_pattern="arbff",
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=port)
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Creating FC Port Channels failed")
            customlogs("\nCreating FC Port Channels failed\n", logfile)
            return obj

        mo7 = FabricFcVsanPc(
            parent_mo_or_dn="fabric/san/" +
                            inputdict['ucs_fabric_id'] +
            "/net-" + inputdict['vsan_name'],
            admin_state="enabled",
            port_id=inputdict['port_id'],
            name="",
            descr="",
            switch_id=inputdict['ucs_fabric_id'])
        self.handle.add_mo(mo7, True)

        try:
            self.handle.commit()

        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Associating VSAN For Port Channels failed")
            customlogs("\nCreating FC Port Channels failed\n", logfile)
            return obj

        #To check whether FI is swapped/not
        fabric_mo="fabric/san/" + inputdict['ucs_fabric_id']+ "/pc-" + inputdict['port_id']
        time.sleep(10)
        state = self.handle.query_dn(fabric_mo).oper_state
        if state != "up":
            loginfo("FI might have been swapped.Please check")

        self.handle.logout()
        customlogs("\nCreated FC Port Channel successfully\n", logfile)
        dicts['fc_port_channel_name'] = parent_mo + \
            "/" + inputdict['fc_port_channel_name']
        obj.setResult(dicts, PTK_OKAY, "Created FC Port Channel successfully")
        return obj

    def ucsDeleteFCPortChannels(self, inputdict, logfile):
        """
        Delete FC Port Channels

        :param inputdict: Dictionary (FC Port Channel name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Deleting_FC_Port_Channel")
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        fabric_mo = "fabric/san/" + \
            inputdict['ucs_fabric_id'] + "/pc-" + inputdict['port_id']
        ports = inputdict['port_list'].split('|')
        for port in ports:
            mo = FabricFcSanPcEp(
                parent_mo_or_dn=fabric_mo,
                name="",
                admin_speed="auto",
                auto_negotiate="yes",
                slot_id="1",
                admin_state="disabled",
                port_id=port)

            self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Deleting FC Port Channels failed")
            customlogs("\nDeleting FC Port Channels failed\n", logfile)
            return obj
        mo1 = self.handle.query_dn(
            "fabric/san/" + inputdict['ucs_fabric_id'] + "/pc-" + inputdict['port_id'])
        self.handle.remove_mo(mo1)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Deleting FC Port Channels failed")
            customlogs("\nDeleting FC Port Channels failed\n", logfile)
            return obj
        customlogs("\n FC Port Channel " +
                   inputdict['fc_port_channel_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "FC Port channel deleted successfully")
        return obj

    def ucsCreateHostFirmwarePackage(self, inputdict, logfile):
        """
        Create Host Firmware Package in UCS

        :param inputdict: Dictionary (Host Firmware Package name, blade package, rack package)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Host Firmware Package")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Host firmware package = " + inputdict['name'])
        if inputdict['blade_pkg']:
            loginfo("Blade Package = " + inputdict['blade_pkg'])
            message = "Blade Package: " + inputdict['blade_pkg']
            customlogs(message, logfile)
        else:
            loginfo("Rack Package = " + inputdict['rack_pkg'])
            message = "Rack Package: " + inputdict['rack_pkg']
            customlogs(message, logfile)

        loginfo("Excluded components = " + inputdict['excluded_comp'])
        loginfo("Create Host Firmware Package started")

        if inputdict['blade_pkg'] == "not-set":
            inputdict['blade_pkg'] = ""
        if inputdict['rack_pkg'] == "not-set":
            inputdict['rack_pkg'] = ""

        if inputdict['blade_pkg']:
            image_prefix = "ucs-k9-bundle-b-series." + \
                inputdict['blade_pkg'].replace(
                    '(', '.').replace(')', '.')

            image = self.get_image_file(self.handle, image_prefix)

            if not is_image_available_on_ucsm(self.handle, image):
                customlogs(
                    "Blade image is not present in UCS. Uploading blade image to UCS", logfile)
                if not upload_image_to_ucs([image], self.handle, "/mnt/system/uploads"):
                    customlogs("Failed to upload blade image to UCS", logfile)
                    self.handle.logout()
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to update host firmware package")
                    return obj
                customlogs("Blade image upload done", logfile)
            else:
                customlogs("Blade image is present in UCS", logfile)

            customlogs("Waiting for blades to complete discovery", logfile)
            blades_list = self.handle.query_classid("computeBlade")
            for blade in blades_list:
                self.verify_blade_discovery(self.handle, blade, logfile)
            time.sleep(60)
        if inputdict['rack_pkg']:
            image_prefix = "ucs-k9-bundle-c-series." + \
                inputdict['rack_pkg'].replace(
                    '(', '.').replace(')', '.')

            image = self.get_image_file(self.handle, image_prefix)

            if not is_image_available_on_ucsm(self.handle, image):
                customlogs(
                    "Rack image is not present in UCS. Uploading rack image to UCS", logfile)
                if not upload_image_to_ucs([image], self.handle, "/mnt/system/uploads"):
                    customlogs("Failed to upload rack image to UCS", logfile)
                    self.handle.logout()
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to update host firmware package")
                    return obj
                customlogs("Rack image upload done", logfile)
            else:
                customlogs("Rack image is present in UCS", logfile)

            customlogs("Waiting for rack to complete discovery", logfile)
            rack_list = self.handle.query_classid("ComputeRackUnit")
            for rack in rack_list:
                self.verify_blade_discovery(self.handle, rack, logfile)
            time.sleep(60)

        mo = FirmwareComputeHostPack(
            parent_mo_or_dn="org-root",
            ignore_comp_check="yes",
            name=inputdict['name'],
            descr=inputdict['desc'],
            stage_size="0",
            rack_bundle_version=inputdict['rack_pkg'],
            update_trigger="immediate",
            policy_owner="local",
            mode="staged",
            blade_bundle_version=inputdict['blade_pkg'],
            override_default_exclusion="yes")
        server_comp = inputdict['excluded_comp'].split('|')
        for excluded_comp in server_comp:
            FirmwareExcludeServerComponent(
                parent_mo_or_dn=mo, server_component=excluded_comp)
        self.handle.add_mo(mo, modify_present=True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("\nFailed to update host firmware package\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to update host firmware package")
            return obj

        self.handle.logout()
        # Waiting for blades to complete upgrade
        time.sleep(600)
        customlogs("\nHost Firmware Package Created Successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Host Firmware Package Created Successfully")
        return obj

    # TODO
    def get_image_file(self, handle, image):
        ucs_upgrade = get_ucs_upgrade()
        if ucs_upgrade == "Yes":
            path = "/mnt/system/uploads"
            image_check = glob.glob(path + '/' + image + "*")
            if image_check != []:
                return image_check[0].split('/')[4]
        else:
            loginfo("UCS upgrade set as NO")
            image_name = image_name_ucs(handle, image)
            if image_name == "":
                loginfo("image is not exist in ucs")
            else:
                return image_name

    def ucsResetHostFirmwarePackage(self, inputs, outputs, logfile):
        """
        Reset Host Firmware Package in UCS

        :param inputs: Dictionary (Host firmware package name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        dicts = {}
        obj = result()
        loginfo("Resetting Host Firmware Blade and Rack package ")
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = FirmwareComputeHostPack(
            parent_mo_or_dn="org-root",
            ignore_comp_check="yes",
            name=inputs['name'],
            descr=inputs['desc'],
            stage_size="0",
            rack_bundle_version='',
            update_trigger="immediate",
            policy_owner="local",
            mode="staged",
            blade_bundle_version='',
            override_default_exclusion="yes")

        self.handle.add_mo(mo, modify_present=True)
        try:
            self.handle.commit()
        except UcsException:
            customlogs(
                "Failed to Reset host firmware blade and rack package", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to Reset host firmware blade and rack package")
            return obj
        customlogs(
            "Host firmware package is reset successfully", logfile)
        obj.setResult(
            None, PTK_OKAY, "Reset host firmware blade and rack package successfully")
        return obj

    def ucsCreateLANConnectivityPolicy(self, inputdict, logfile):
        """
        Create LAN Connectivity policy

        :param inputdict: Dictionary (LAN Connectivity policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_LAN_connectivity_policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(
            "LAN connectivity policy Name =" +
            inputdict['lan_conn_policy_name'])
        loginfo(
            "LAN connectivity policy Description =" +
            inputdict['lan_conn_policy_desc'])

        message = "LAN connectivity policy Name: " + \
                  inputdict['lan_conn_policy_name'] + \
                  "\nLAN Connectivity policy Description: " + \
                  inputdict['lan_conn_policy_desc']
        customlogs(message, logfile)

        mo = VnicLanConnPolicy(
            parent_mo_or_dn="org-root",
            name=inputdict['lan_conn_policy_name'],
            descr=inputdict['lan_conn_policy_desc'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("LAN connectivity policy creation failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "LAN connectivity policy creation failed")
            return obj

        customlogs("LAN Connectivity policy created successfully\n", logfile)
        dicts['lan_conn_policy_name'] = "org-root/lan-conn-pol-" + \
                                        inputdict['lan_conn_policy_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "LAN connectivity policy creation successful")
        return obj

    def ucsDeleteLANConnectivityPolicy(self, inputs, outputs, logfile):
        """
        Delete LAN Connectivity policy

        :param inputs: Dictionary (LAN Connectivity policy name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete LAN Connectivity Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(outputs['lan_conn_policy_name'])
        if mo:
            self.handle.remove_mo(mo)
        else:
            customlogs("\nLAN connectivity policy " +
                       inputs['lan_conn_policy_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete LAN connectivity policy")
            return obj

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete LAN Connectivity Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete LAN connectivity policy")
            return obj
        customlogs("\n LAN connectivity Policy " +
                   inputs['lan_conn_policy_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "LAN connectivity policy deleted successfully")
        return obj

    def ucsCreatevNIC(self, inputdict, logfile):
        """
        Create vNIC in UCS

        :param inputdict: Dictionary (vNIC Name, vNIC template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create vNIC")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Create vNIC parameters = ")
        loginfo(inputdict)
        message = "Name: " + inputdict['vnic_name'] + "\nPolicy Name: " + inputdict['policy_name'] + \
            "\nvNIC Template: " + inputdict['nw_templ_name'] + "\nAdapter policy: " + inputdict['adaptor_policy_name']
        customlogs(message, logfile)
        policy_name = str(inputdict['policy_name'])
        pol_obj = self.handle.query_dn(policy_name)
        mo = VnicEther(
            parent_mo_or_dn=pol_obj,
            name=inputdict['vnic_name'],
            adaptor_profile_name=inputdict['adaptor_policy_name'],
            nw_templ_name=inputdict['nw_templ_name'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("vNIC creation failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "vNIC creation failed")
            return obj

        self.handle.logout()
        customlogs("vNIC " + inputdict['vnic_name'] +
                   " created successfully\n", logfile)
        dicts['vnic_name'] = inputdict['vnic_name']
        obj.setResult(dicts, PTK_OKAY, "vNIC creation successful")
        return obj

    def ucsDeleteiSCSIvNIC(self, inputdict, logfile):
        """
        Delete iSCSI vNIC

        :param inputdict: Dictionary (iSCSI vNIC name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete iSCSI vNIC")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            inputdict['policy_name'] + "/iscsi-" + inputdict['vnic_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()

        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("Delete iSCSI vNIC failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Delete iSCSI vNIC creation failed")
            return obj

        customlogs("iSCSI vNIC deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Delete iSCSI vNIC successful")
        return obj

    def ucsCreateiSCSIvNIC(self, inputdict, logfile):
        """
        Create iSCSI vNIC

        :param inputs: Dictionary (vNIC name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create iSCSI vNIC")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Create iSCSI vNIC parameters = ")
        loginfo(inputdict)
        message = "Name: " + inputdict['vnic_name'] + "\npolicyname" + inputdict[
            'policy_name'] + "\nOverlay vNIC Template" + \
            inputdict['overlay_vnic'] + "\nAdapter policy" + \
            inputdict['adaptor_policy_name']
        customlogs(message, logfile)
        policy_name = str(inputdict['policy_name'])
        pol_obj = self.handle.query_dn(policy_name)

        mo = VnicIScsiLCP(
            parent_mo_or_dn=pol_obj,
            cdn_prop_in_sync="yes",
            addr="derived",
            admin_host_port="ANY",
            admin_vcon="any",
            stats_policy_name="default",
            admin_cdn_name="",
            switch_id="A",
            pin_to_group_name="",
            vnic_name=inputdict['overlay_vnic'],
            qos_policy_name="",
            adaptor_profile_name="default",
            ident_pool_name="",
            cdn_source="vnic-name",
            order="unspecified",
            nw_templ_name="",
            name=inputdict['vnic_name'])
        VnicVlan(parent_mo_or_dn=mo, name="", vlan_name=inputdict['vlan_name'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("iSCSI vNIC creation failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "iSCSI vNIC creation failed")
            return obj

        self.handle.logout()
        customlogs("iSCSI vNIC created successfully\n", logfile)
        dicts['vnic_name'] = policy_name + "/ether-" + inputdict['vnic_name']
        obj.setResult(dicts, PTK_OKAY, "iSCSI vNIC creation successful")
        return obj

    def ucsDeletevNIC(self, inputs, outputs, logfile):
        """
        Delete vNIC

        :param inputs: Dictionary (vNIC name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        loginfo("Deleting vNIC " + inputs['vnic_name'])
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        try:
            mo = self.handle.query_dn(
                inputs['policy_name'] + "/ether-" + outputs['vnic_name'])
            if mo:
                self.handle.remove_mo(mo)
                self.handle.commit()
            else:
                customlogs("vNIC does not exist", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to delete vNIC")
                return obj

        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Failed to delete vNIC", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "Failed to delete vNIC")
            return obj
        customlogs("vNIC " + inputs['vnic_name'] +
                   " deleted successfully\n", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY, "vNIC deleted successfully")
        return obj

    def ucsCreateLocalDiskConfigurationPolicy(
            self, inputdict, logfile):
        """
        Create Local disk configuration policy

        :param inputs: Dictionary (local disk config policy name, flex flash state)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Local Disk Configuration Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nMode: " + inputdict['mode'] + "\nFlexFlash: " + \
            inputdict['flash_state'] + "\nFlexFlash RAID Reporting state: " + inputdict['raid_state']
        loginfo("Create Local Disk Configuration Policy parameters = " + message)
        customlogs(message, logfile)

        mo = StorageLocalDiskConfigPolicy(
            parent_mo_or_dn="org-root",
            protect_config="yes",
            name=inputdict['name'],
            descr=inputdict['descr'],
            flex_flash_raid_reporting_state=inputdict['raid_state'],
            flex_flash_state=inputdict['flash_state'],
            policy_owner="local",
            mode=inputdict['mode'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs(
                "\nFailed to Create Local Disk Configuration Policy\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Local Disk Configuration Policy Creation failed")
            return obj

        customlogs(
            "\nLocal Disk Configuration Policy Created successfully\n",
            logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Local Disk Configuration Policy Created successfully")
        return obj

    def ucsDeleteLocalDiskConfigurationPolicy(self, inputs, outputs, logfile):
        """
        Delete Local disk configuration policy

        :param inputs: Dictionary (local disk configuration policy name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Local Disk Configuration Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(
            "org-root/local-disk-config-" + outputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Delete Local Disk Configuration Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete local disk configuration policy")
            return obj
        customlogs("\n Local Disk Configuration Policy " +
                   outputs['name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Local disk configuration deleted successfully")
        return obj

    def ucsCreateMACAddressPools(self, inputdict, logfile):
        """
        Create MAC Address pools for both switching fabric

        :param inputdict: Dictionary (MAC Address pool name, mac address start,size)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("MAC Pool name = " + inputdict['mac_name'])
        loginfo("Assignment order = " + inputdict['mac_order'])
        loginfo("MAC Start Address = " + inputdict['mac_start'])
        loginfo("MAC Address size = " + inputdict['size'])

        message = "MAC Pool name: " + inputdict['mac_name'] + "\nAssignment order: " + \
                  inputdict['mac_order'] + "\nMAC Address size: " + inputdict['size'] + \
                  "\nMAC Start Address: " + inputdict['mac_start']
        customlogs(message, logfile)

        mac_start_addr = str(inputdict['mac_start'])
        mac_size = int(inputdict['size'])
        mac_int = int(mac_start_addr.translate(None, ":.- "), 16)
        mac_end_int = mac_int + (mac_size - 1)
        mac_hex = "{:012X}".format(mac_end_int)
        mac_end = ":".join(mac_hex[i:i + 2] for i in range(0, len(mac_hex), 2))

        loginfo("MAC End Address= " + mac_end)

        mo = MacpoolPool(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            descr="",
            assignment_order=inputdict['mac_order'],
            name=inputdict['mac_name'])
        MacpoolBlock(
            parent_mo_or_dn=mo,
            to=mac_end,
            r_from=inputdict['mac_start'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create MAC Address Pools\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "MAC Address Pool creation failed")
            return obj

        customlogs("\nMAC Address Pool created successfully\n", logfile)
        dicts['mac_name'] = inputdict['mac_name']
        obj.setResult(dicts, PTK_OKAY, "MAC Address Pool created successfully")
        return obj

    def ucsDeleteMACAddressPools(self, inputs, outputs, logfile):
        """
        Delete MAC Address pools from both switching fabric

        :param inputs: Dictionary (MAC pool name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("org-root/mac-pool-" + outputs['mac_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create MAC Address Pools\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "MAC Address Pool deletion failed for mac pool" + outputs['mac_name'])
            return obj
        customlogs("MAC Address pool " +
                   outputs['mac_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "MAC Address Pool" +
            outputs['mac_name'] +
            " deleted successfully")
        return obj

    def ucsCreateMgmtvNiCTemplate(self, inputdict, logfile):
        """
        Create Management vNIC template

        :param inputs: Dictionary (Management vNIC Template name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_Management_vNIC_Template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(
            "Mgmt vNIC Template Name =" +
            inputdict['mgmt_vnic_templ_name'])
        loginfo(
            "Mgmt vNIC Template Description =" +
            inputdict['mgmt_vnic_templ_desc'])
        loginfo("Fabric ID =" + inputdict['ucs_fabric_id'])
        loginfo("Redundancy Pair Type =" + inputdict['redundancy_pair_type'])
        loginfo("VLANs =" + inputdict['vlans'])
        loginfo("Native VLAN =" + inputdict['native_vlan'])
        loginfo("Template Type =" + inputdict['templ_type'])
        loginfo("CDN Source =" + inputdict['cdn_source'])
        loginfo("Ident Pool Name =" + inputdict['ident_pool_name'])
        loginfo("Network Control Policy =" + inputdict['nw_ctrl_policy_name'])
        loginfo("MTU =" + inputdict['mtu'])
        loginfo("VLANS =" + inputdict['vlans'])

        message = "Mgmt vNIC Template Name: " + inputdict['mgmt_vnic_templ_name'] + "\nMgmt vNIC Template Desc: " + \
                  inputdict['mgmt_vnic_templ_desc'] + "\nFabric ID: " + inputdict[
                      'fabric_id'] + "\nRedundancy Pair Type: " + inputdict['redundancy_pair_type'] + \
                  "\nTemplate Type: " + inputdict['templ_type'] + "\nCDN Source: " + inputdict[
                      'cdn_source'] + "\nIdent Pool Name: " + inputdict['ident_pool_name'] + \
                  "\nNetwork Control Policy: " + \
                  inputdict['nw_ctrl_policy_name'] + "\nMTU: " + \
                  inputdict['mtu']

        customlogs(message, logfile)

        mo = VnicLanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_pair_type'],
            name=inputdict['mgmt_vnic_templ_name'],
            descr=inputdict['mgmt_vnic_templ_desc'],
            stats_policy_name="",
            admin_cdn_name="",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            mtu=inputdict['mtu'],
            peer_redundancy_templ_name=inputdict['peer_red_template'] if inputdict[
                'peer_red_template'] != "not-set" else "",
            templ_type=inputdict['templ_type'],
            qos_policy_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            cdn_source=inputdict['cdn_source'],
            nw_ctrl_policy_name=inputdict['nw_ctrl_policy_name'])

        inputdict['vlans'] = inputdict['vlans'].split('|')
        for name in inputdict['vlans']:
            if name == inputdict['native_vlan']:
                VnicEtherIf(
                    parent_mo_or_dn=mo,
                    default_net="yes",
                    name=name)
            else:
                VnicEtherIf(
                    parent_mo_or_dn=mo,
                    default_net="no",
                    name=name)
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Management creation failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Management vNIC creation failed")
            return obj
        customlogs("Management vNIC template created successfully\n", logfile)
        dicts['mgmt_vnic_templ_name'] = inputdict['mgmt_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "Management vNIC creation successfull")
        return obj

    def ucsDeleteMgmtvNiCTemplate(self, inputs, outputs, logfile):
        """
        Delete Management vNIC template

        :param inputs: Dictionary (Management vNIC Template name)
        :param outputs: Outputs from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Management vNIC template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(
            "org-root/lan-conn-templ-" + inputs['mgmt_vnic_templ_name'])
        if mo is None:
            customlogs("\nManagement vNIC template " +
                       inputs['mgmt_vnic_templ_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete management vNIC template")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete management vNIC template\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete management vNIC template")
            return obj
        customlogs("\n Management vNIC template " +
                   inputs['mgmt_vnic_templ_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Management vNIC template deleted successfully")
        return obj

    def ucsDeleteiSCSIvNiCTemplate(self, inputdict, logfile):
        """
        Delete iSCSI vNIC template

        :param inputdict: Dictionary (iSCSI vNIC Template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_iSCSI_vNIC_Template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            "org-root/lan-conn-templ-" + inputdict['iSCSI_vnic_templ_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException:
            customlogs("\nFailed to Delete iSCSI vNIC template\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete ISCSI vNIC template")
            return obj
        customlogs("\n iSCSI vNIC template " +
                   inputdict['iSCSI_vnic_templ_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "iSCSI vNIC template deleted successfully")
        return obj

    def ucsCreateiSCSIvNiCTemplate(self, inputdict, logfile):
        """
        Create iSCSI vNIC template

        :param inputdict: Dictionary (iSCSI vNIC template)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_iSCSI_vNIC_Template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(
            "iSCSI vNIC Template Name =" +
            inputdict['iSCSI_vnic_templ_name'])
        loginfo(
            "iSCSI vNIC Template Description =" +
            inputdict['iSCSI_vnic_templ_desc'])
        loginfo("Fabric ID =" + inputdict['ucs_fabric_id'])
        loginfo("Redundancy Pair Type =" + inputdict['redundancy_pair_type'])
        loginfo("VLANs =" + inputdict['vlans'])
        loginfo("Template Type =" + inputdict['templ_type'])
        loginfo("Ident Pool Name =" + inputdict['ident_pool_name'])
        loginfo("Network Control Policy =" + inputdict['nw_ctrl_policy_name'])
        #        loginfo("Stats Threshold Policy =" + inputdict['stats_policy_name'])
        loginfo("MTU =" + inputdict['mtu'])

        message = "iSCSI vNIC Template Name: " + inputdict['iSCSI_vnic_templ_name'] + "\niSCSI vNIC Template Desc: " + \
                  inputdict['iSCSI_vnic_templ_desc'] + "\nFabric ID: " + inputdict[
                      'fabric_id'] + "\nRedundancy Pair Type: " + inputdict['redundancy_pair_type'] + \
                  "\nTemplate Type: " + inputdict['templ_type'] + "\nIdent Pool Name: " + inputdict['ident_pool_name'] + \
                  "\nNetwork Control Policy: " + \
                  inputdict['nw_ctrl_policy_name'] + "\nMTU: " + \
                  inputdict['mtu']

        customlogs(message, logfile)

        mo = VnicLanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_pair_type'],
            name=inputdict['iSCSI_vnic_templ_name'],
            descr=inputdict['iSCSI_vnic_templ_desc'],
            stats_policy_name="default",
            admin_cdn_name="",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            mtu=inputdict['mtu'],
            peer_redundancy_templ_name="",
            templ_type=inputdict['templ_type'],
            qos_policy_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            cdn_source="vnic-name",
            nw_ctrl_policy_name=inputdict['nw_ctrl_policy_name'])

        inputdict['vlans'] = inputdict['vlans'].split('|')
        for name in inputdict['vlans']:
            VnicEtherIf(
                parent_mo_or_dn=mo,
                default_net="yes",
                name=name)
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("iSCSI vNIC template creation failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "iSCSI vNIC creation failed")
            return obj
        customlogs("iSCSI vNIC created successfully\n", logfile)
        dicts['iSCSI_vnic_templ_name'] = inputdict['iSCSI_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "iSCSI vNIC creation successfull")
        return obj

    def ucsCreatePowerControlPolicy(self, inputdict, logfile):
        """
        Create Power Control policy

        :param inputdict: Dictionary (Name, fan speed policy,cap)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Power Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nFan speed policy: " + \
                  inputdict['speed'] + "\nCap: " + inputdict['cap']
        loginfo("Create Power Control Policy parameters = " + message)
        customlogs(message, logfile)

        mo = PowerPolicy(
            parent_mo_or_dn="org-root",
            fan_speed=inputdict['speed'],
            policy_owner="local",
            name=inputdict['name'],
            prio=inputdict['cap'],
            descr=inputdict['descr'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create Power Control Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Power Control Policy creation failed")
            return obj

        customlogs("\nPower Control Policy Created Successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Power Control Policy Created Successfully")
        return obj

    def ucsDeletePowerControlPolicy(self, inputs, outputs, logfile):
        """
        Delete Power control policy

        :param inputs: Dictionary (power control policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Power Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("org-root/power-policy-" + inputs['name'])

        try:
            self.handle.remove_mo(mo)
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete Power Control policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete power control policy")
            return obj
        customlogs("Power control policy " +
                   inputs['name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Power control policy deleted successfully")
        return obj

    def ucsCreateSANConnectivityPolicy(self, inputdict, logfile):
        """
        Create SAN Connectivity policy

        :param inputdict: Dictionary (SAN Connectivity policy name. description, WWNN pool name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_SAN_connectivity_policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(
            "SAN connectivity policy Name =" +
            inputdict['san_conn_policy_name'])
        loginfo(
            "SAN connectivity policy Description =" +
            inputdict['san_conn_policy_desc'])
        loginfo("Ident Pool Name =" + inputdict['ident_pool_name'])

        message = "SAN connectivity policy Name: " + inputdict[
            'san_conn_policy_name'] + "\n SAN Connectivity policy Description: " + \
            inputdict['san_conn_policy_desc'] + \
            "\nIdent Pool Name: " + inputdict['ident_pool_name']

        customlogs(message, logfile)

        mo = VnicSanConnPolicy(
            parent_mo_or_dn="org-root",
            name=inputdict['san_conn_policy_name'],
            descr=inputdict['san_conn_policy_desc'])
        VnicFcNode(parent_mo_or_dn=mo,
                   ident_pool_name=inputdict['ident_pool_name'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nSAN connectivity policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "SAN Connectivity policy creation failed")
            return obj
        customlogs("\nSAN Connectivity policy created successfully\n", logfile)
        dicts['san_conn_policy_name'] = inputdict['san_conn_policy_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "SAN Connectivity policy creation successful")
        return obj

    def ucsDeleteSANConnectivityPolicy(self, inputdict, logfile):
        """
        Delete SAN Connectivity policy

        :param inputdict: Dictionary (SAN Connectivity policy name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("delete_SAN_connectivity_policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            "org-root/san-conn-pol-" + inputdict['san_conn_policy_name'])
        if mo is None:
            customlogs("\nSAN connectivity policy " +
                       inputdict['san_conn_policy_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete SAN connectivity policy")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nSAN connectivity policy deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "SAN Connectivity policy deletion failed")
            return obj
        customlogs("\nSAN Connectivity policy " +
                   inputdict['san_conn_policy_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "SAN Connectivity policy deletion successful")
        return obj

    def ucsCreateServerBIOSPolicy(self, inputdict, logfile):
        """
        Create Server BIOS policy

        :param inputdict: Dictionary (name,reboot,quiet boot,cdn)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Server BIOS Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nReboot on BIOS settings change: " + inputdict[
            'reboot'] + "\nQuiet boot: " + inputdict['boot'] + \
            "\nConsistent device naming: " + \
            inputdict['device_naming']
        loginfo("Create Server BIOS Policy parameters  = " + message)
        customlogs(message, logfile)

        mo = BiosVProfile(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            name=inputdict['name'],
            descr=inputdict['descr'],
            reboot_on_update=inputdict['reboot'])
        BiosVfConsistentDeviceNameControl(
            parent_mo_or_dn=mo, vp_cdn_control=inputdict['device_naming'])
        BiosVfQuietBoot(
            parent_mo_or_dn=mo,
            vp_quiet_boot=inputdict['boot'])
        BiosVfDRAMClockThrottling(
            parent_mo_or_dn=mo,
            vp_dram_clock_throttling=inputdict['dram_clock'])
        BiosVfFrequencyFloorOverride(
            parent_mo_or_dn=mo,
            vp_frequency_floor_override=inputdict['freq_floor'])
        BiosVfProcessorCState(parent_mo_or_dn=mo,
                              vp_processor_c_state=inputdict['proc_c_state'])
        BiosVfProcessorC1E(
            parent_mo_or_dn=mo,
            vp_processor_c1_e=inputdict['proc_c1e'])
        BiosVfProcessorC3Report(
            parent_mo_or_dn=mo,
            vp_processor_c3_report=inputdict['proc_c3_report'])
        BiosVfProcessorC7Report(
            parent_mo_or_dn=mo,
            vp_processor_c7_report=inputdict['proc_c7_report'])
        BiosVfProcessorEnergyConfiguration(
            parent_mo_or_dn=mo,
            vp_power_technology=inputdict['power_tech'],
            vp_energy_performance=inputdict['energy_perf'])
        BiosVfLvDIMMSupport(
            parent_mo_or_dn=mo,
            vp_lv_ddr_mode=inputdict['lv_ddr_mode'])
        BiosVfIntelTurboBoostTech(
            parent_mo_or_dn=mo, vp_intel_turbo_boost_tech=inputdict['intel_turbo'])
        BiosVfEnhancedIntelSpeedStepTech(
            parent_mo_or_dn=mo, vp_enhanced_intel_speed_step_tech=inputdict['intel_speedstep'])
        BiosVfIntelHyperThreadingTech(
            parent_mo_or_dn=mo, vp_intel_hyper_threading_tech=inputdict['hyper_threading'])
        BiosVfIntelVirtualizationTechnology(
            parent_mo_or_dn=mo, vp_intel_virtualization_technology=inputdict['intel_vt'])
        BiosVfIntelVTForDirectedIO(
            parent_mo_or_dn=mo,
            vp_intel_vtd_pass_through_dma_support="platform-default",
            vp_intel_vtdats_support="platform-default",
            vp_intel_vtd_interrupt_remapping="platform-default",
            vp_intel_vtd_coherency_support="platform-default",
            vp_intel_vt_for_directed_io=inputdict['intel_vtd'])
        BiosVfCPUPerformance(parent_mo_or_dn=mo,
                             vp_cpu_performance=inputdict['cpu_perf'])
        BiosVfDirectCacheAccess(
            parent_mo_or_dn=mo, vp_direct_cache_access=inputdict['direct_cache_access'])
        BiosVfSelectMemoryRASConfiguration(
            parent_mo_or_dn=mo, vp_select_memory_ras_configuration=inputdict['memory_ras'])

        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Create Server BIOS Policy\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Server BIOS Policy Creation failed")
            return obj

        customlogs(
            "\nServer BIOS Policy created successfully \n",
            logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server BIOS Policy Created Successfully ")
        return obj

    def ucsDeleteServerBIOSPolicy(self, inputs, outputs, logfile):
        """
        Delete Server BIOS policy

        :param inputdict: Dictionary
        :param outputs:Dictionary(name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Server BIOS Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("org-root/bios-prof-" + outputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to delete Server BIOS Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete Server BIOS policy")
            return obj
        dicts['status'] = "SUCCESS"
        customlogs("\nServer BIOS Policy " +
                   outputs['name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Server BIOS policy deleted successfully")
        return obj

    def ucsCreateServerPool(self, inputdict, logfile):
        """
        Create Server Pool for Cisco UCS environment

        :param inputdict: Dictionary (name,servers)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Server Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + \
                  "\nSelected servers: " + inputdict['servers']
        customlogs(message, logfile)

        mo = ComputePool(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            name=inputdict['name'],
            descr=inputdict['desc'])
        inputdict['servers'] = inputdict['servers'].split("|")
        for server in inputdict['servers']:
            if "chassis" in server:
                slots = server.split('/')
                chassis_id = slots[1].split('-')
                slot_id = slots[2].split('-')
                ComputePooledSlot(
                    parent_mo_or_dn=mo, slot_id=str(
                        slot_id[1]), chassis_id=str(
                        chassis_id[1]))
            else:
                slots = server.split('-')
                slot_id = slots[2]
                ComputePooledRackUnit(parent_mo_or_dn=mo, id=slot_id)
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("\nCreate Server Pool failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Server Pool created successfully")
            return obj

        self.handle.logout()
        customlogs("\nServer Pool created successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(dicts, PTK_OKAY, "Server Pool created successfully")
        return obj

    def ucsCreateServerPoolQualificationPolicy(
            self, inputdict, logfile):
        """
        Create Server pool qualification policy

        :param inputdict: Dictionary (name,pid,min max cores,min max threads,speed)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Server Pool Qualification Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nPID: " + inputdict['pid'] + "\nProcessor Architecture" + inputdict[
            'arch'] + "\nMin no of cores" + inputdict['min_cores'] + "\nMax no of cores" + \
            inputdict['max_cores'] + "\nMin no of threads" + inputdict['min_threads'] + "\nMax no of threads" + \
            inputdict['max_threads'] + "\nCPU speed" + \
            inputdict['speed'] + "\nCPU stepping" + inputdict['stepping']
        loginfo("Create Server Pool Qualification Policy paramaters = " + message)
        customlogs(message, logfile)

        mo = ComputeQual(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            name=inputdict['name'],
            descr=inputdict['descr'])
        ProcessorQual(
            parent_mo_or_dn=mo,
            max_procs="unspecified",
            max_threads=inputdict['max_threads'],
            min_threads=inputdict['min_threads'],
            min_procs="unspecified",
            speed=inputdict['speed'],
            max_cores=inputdict['max_cores'],
            stepping=inputdict['stepping'],
            min_cores=inputdict['min_cores'],
            model=inputdict['pid'],
            arch=inputdict['arch'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Create Server Pool Qualification Policy\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Server Pool Qualification Policy creation failed")
            return obj

        customlogs(
            "\nServer Pool Qualification Policy created successfully\n",
            logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server Pool Qualification Policy created successfully")
        return obj

    def ucsCreateServiceProfileFromTemplate(self, inputdict, logfile):
        """
        Create Service Profile from template

        :param inputdict: Dictionary (name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("create_service_profile_from_template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("profilename =" + inputdict['profile_name'])
        loginfo("templatename =" + inputdict['template_name'])
        loginfo("description =" + inputdict['profile_desc'])
        message = "Profile name: " + inputdict['profile_name'] + "\nTemplate name: " + \
                  inputdict['template_name'] + \
                  "\nProfile description: " + inputdict['profile_desc']
        customlogs("Create service profile started....\n", logfile)
        customlogs(message, logfile)
        mo = LsServer(
            parent_mo_or_dn="org-root",
            descr=inputdict['profile_desc'],
            src_templ_name=inputdict['template_name'],
            name=inputdict['profile_name'])
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nService profile creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile creation failed")
            return obj

        customlogs("\nService profile created successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Service profile creation successful")
        return obj

    def ucsServerReset(self, inputdict, logfile):
        """
        Reset UCS Server to reboot after FlashArray configuration is completed

        :param inputdict: Dictionary
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        if get_server_type() == "Blade":
            loginfo("Resetting the Blade server")
        else:
            loginfo("Resetting the Rack server")

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        service_profiles = self.handle.query_classid("lsServer")
        for sp in service_profiles:
            if sp.type != "updating-template":
                mo = LsServer(
                    parent_mo_or_dn="org-root",
                    name=sp.name)
                LsPower(parent_mo_or_dn=mo,
                        state="hard-reset-immediate")
                self.handle.add_mo(mo, modify_present=True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nReset server failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Reset server failed")
            return obj

        customlogs("\nServers reset successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Reset server successful")
        return obj

    def wait_assoc_completion(self, handle, sp_dn, server_dn, logfile):
        """
        Wait until the specified physical server has completed the association FSM

        :param handle: ucs login handle
        :param sp_dn: Service Profile DN
        :param server_dn: Blade Server DN
        :param logfile: Logfile name
        """
        assoc_completion_timeout = 20 * 60
        start = datetime.datetime.now()

        sp_mo = handle.query_dn(sp_dn)
        if sp_mo is None:
            raise Exception("Service Profile %s does not exist", sp_dn)

        phys_mo = handle.query_dn(server_dn)
        if phys_mo is None:
            raise Exception("Server %s does not exist" % sp_dn)
        while phys_mo.association != 'associated':
            time.sleep(10)
            if (datetime.datetime.now() - start).total_seconds() > \
                    assoc_completion_timeout:
                loginfo('Server %s has not completed association' %
                        (server_dn))
                customlogs('Server %s has not completed association' %
                           (server_dn), logfile)
                break
            loginfo(
                'Server %s fsmStatus: %s, elapsed=%ds' %
                (server_dn, phys_mo.fsm_status, (datetime.datetime.now() - start).total_seconds()))
            # Query again to update association state
            phys_mo = handle.query_dn(server_dn)

        if phys_mo.association == 'associated':
            loginfo('Server %s has completed association' % (
                server_dn))
            customlogs('Server %s has completed association' % (
                server_dn), logfile)

    def verify_blade_discovery(self, handle, blade, logfile):
        """
        Wait until the blade discovery is completed

        :param handle: ucs login handle
        :param blade: UCS blade server
        :param logfile: Logfile name
        """

        discovery_timeout = 15 * 60
        start = datetime.datetime.now()
        mo = handle.query_dn(blade.dn)
        while mo.discovery != 'complete':
            time.sleep(10)
            if (datetime.datetime.now() - start).total_seconds() > \
                    discovery_timeout:
                loginfo('Server %s has not completed discovery' % (blade.dn))
                customlogs('Server %s has not completed discovery.May take long time' % (
                    blade.dn), logfile)
                break
            loginfo('Server %s fsmStatus: %s, elapsed=%ds' %
                    (blade.dn, blade.fsm_status, (datetime.datetime.now() - start).total_seconds()))
            # Query again to update discovery state
            mo = handle.query_dn(blade.dn)
        if mo.discovery == 'complete':
            loginfo('Server %s has completed discovery' % (blade.dn))
            customlogs('Server %s has completed discovery' %
                       (blade.dn), logfile)

    def ucsCreateServiceProfilesFromTemplate(self, inputdict, logfile):
        """
        Create Service profiles from service profile template

        :param inputdict: Dictionary (name,instances,suffix start number)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_service_profile_from_template")
        instances = int(inputdict['instances'])
        count = int(inputdict['suffix_starting_number'])
        loginfo("Service profile instances =" + inputdict['instances'])
        loginfo("Suffix start =" + inputdict['suffix_starting_number'])

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        cnt = instances + 1
        for suffix in range(instances, 0, -1):
            dn = Dn()
            dn_set = DnSet()
            cnt -= count
            dn.attr_set("value", inputdict['profile_prefix'] + str(cnt))
            dn_set.child_add(dn)
            elem = ls_instantiate_n_named_template(
                cookie=self.handle.cookie,
                dn="org-root/ls-" +
                inputdict['template_name'],
                in_error_on_existing="true",
                in_name_set=dn_set,
                in_target_org="org-root",
                in_hierarchical="false")
            self.handle.process_xml_elem(elem)
            time.sleep(10)
        customlogs(
            "\nWaiting for Service profile association to be completed\n", logfile)
        time.sleep(60)

        if get_server_type() == "Blade":
            blades_list = self.handle.query_classid("computeBlade")
            for blade in blades_list:
                self.verify_blade_discovery(self.handle, blade, logfile)
        else:
            rack_list = self.handle.query_classid("ComputeRackUnit")
            for rack in rack_list:
                self.verify_blade_discovery(self.handle, rack, logfile)

        # Waiting because it takes sometime for service profile to get associated
        # with the server once it is up
        time.sleep(120)
        sp_unassoc_cnt = 0
        service_profiles_list = []
        service_profiles = self.handle.query_classid("lsServer")
        for sp in service_profiles:
            if sp.type != "updating-template":
                service_profiles_list.append(sp)
        total_sp_cnt = len(service_profiles_list)
        for sp in service_profiles:
            if sp.type != "updating-template":
                if sp.dn != '' and sp.pn_dn != '':
                    self.wait_assoc_completion(
                        self.handle, sp.dn, sp.pn_dn, logfile)
                else:
                    customlogs("Failed to associate service profile " + sp.name + "\n", logfile)
                    #fix for service profile deletion
                    mo = self.handle.query_dn("org-root/ls-" + sp.name)
                    self.handle.remove_mo(mo)
                    try:
                        self.handle.commit()
                    except UcsException:
                        obj.setResult(None, PTK_INTERNALERROR, "Service profile template deletion failed")   
                    sp_unassoc_cnt += 1
                    continue
        if sp_unassoc_cnt == total_sp_cnt:
            customlogs("Failed to associate all service profiles", logfile)
            #fix for service profile deletion
            tmp_list = []
            mo = self.handle.query_classid("lsServer")
            for i in mo:
                if i.type == 'instance':
                    if i.src_templ_name == inputdict['template_name']:
                        tmp_list.append(ls_mo.name)
            for j in tmp_list:
                mo = self.handle.query_dn("org-root/ls-" + j)
                self.handle.remove_mo(mo)
            try:
                self.handle.commit()
            except UcsException:
                obj.setResult(None, PTK_INTERNALERROR, "Service profile template deletion failed")
            obj.setResult(None, PTK_INTERNALERROR, "Service profiles association failed")
        else:
            customlogs("\nService profiles are created successfully\n", logfile)
            obj.setResult(dicts, PTK_OKAY, "Service profiles creation successful")
        # Waiting for sh flogi database entries to be displayed during MDS Zoning
        time.sleep(230)
        return obj

    def ucsCloneServiceProfileTemplate(self, inputdict, logfile):
        """
        Clone service profile template to create vMedia service profile template

        :param inputdict: Dictionary (vmedia_template)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("clone_service_profile_template")

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        elem = ls_clone(
            cookie=self.handle.cookie,
            dn="org-root/ls-" +
               inputdict['template_name'],
            in_server_name=inputdict['vmedia_template'],
            in_target_org="",
            in_hierarchical="false")
        self.handle.process_xml_elem(elem)

        mo = LsServer(
            parent_mo_or_dn="org-root",
            vmedia_policy_name=inputdict['vmedia_policy_name'],
            ext_ip_state="none",
            bios_profile_name=inputdict['biospolicy'],
            mgmt_fw_policy_name="",
            agent_policy_name="",
            mgmt_access_policy_name="",
            dynamic_con_policy_name="",
            kvm_mgmt_policy_name="",
            sol_policy_name="",
            uuid="0",
            descr="",
            stats_policy_name="default",
            policy_owner="local",
            ext_ip_pool_name="ext-mgmt",
            boot_policy_name=inputdict['boot_policy_name'],
            usr_lbl="",
            host_fw_policy_name="",
            vcon_profile_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            src_templ_name="",
            local_disk_policy_name=inputdict['local_disk_policy_name'],
            scrub_policy_name="",
            power_policy_name=inputdict['power_policy_name'],
            maint_policy_name="default",
            name=inputdict['vmedia_template'],
            power_sync_policy_name="",
            resolve_remote="yes")

        self.handle.add_mo(mo, True)
        self.handle.commit()
        dicts['vmedia_template'] = inputdict['vmedia_template']
        customlogs(
            "\nvMedia Service profile template created successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "vMedia Service profile template created successfully")
        return obj

    def ucsCreateServiceProfileTemplate(self, inputdict, logfile):
        """
        Create Service Profile template

        :param inputdict: Dictionary (template name,type,boot policy,uuid pool,local disk policy,power policy)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        loginfo("template_description =" + inputdict['template_desc'])
        message = "Template name: " + \
                  inputdict['template_name'] + \
                  "\nTemplate_description: " + inputdict['template_desc']
        customlogs(message, logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}

        mo = LsServer(
            parent_mo_or_dn="org-root",
            vmedia_policy_name="",
            descr=inputdict['template_desc'],
            stats_policy_name="default",
            policy_owner="local",
            ext_ip_pool_name="ext-mgmt",
            boot_policy_name=inputdict['boot_policy_name'],
            ident_pool_name=inputdict['ident_pool_name'],
            type=inputdict['type'],
            local_disk_policy_name=inputdict['local_disk_policy_name'],
            power_policy_name=inputdict['power_policy_name'],
            name=inputdict['template_name'],
            resolve_remote="yes",
            maint_policy_name=inputdict['maint_policy_name'],
            bios_profile_name=inputdict['biospolicy'])
        vnic_list = self.handle.query_classid("vnicEther")
        lan_dn = "lan-conn-pol-" + inputdict['lan_conn_policy_name']
        VnicConnDef(parent_mo_or_dn=mo,
                    san_conn_policy_name=inputdict['san_conn_policy_name'],
                    lan_conn_policy_name=inputdict['lan_conn_policy_name'])
        order = 0
        for vnic in vnic_list:
            if vnic.dn.split("/")[1] == lan_dn:
                order += 1
                vnic_name = vnic.name
                LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", admin_host_port="ANY",
                             order=str(order), transport="ethernet", vnic_name=vnic_name)
                VnicEther(
                    parent_mo_or_dn=mo,
                    cdn_prop_in_sync="yes",
                    nw_ctrl_policy_name="",
                    admin_host_port="ANY",
                    admin_vcon="any",
                    stats_policy_name="default",
                    admin_cdn_name="",
                    switch_id="A",
                    pin_to_group_name="",
                    name=vnic_name,
                    order=str(order),
                    qos_policy_name="",
                    adaptor_profile_name="",
                    ident_pool_name="",
                    cdn_source="vnic-name",
                    mtu="1500",
                    nw_templ_name="",
                    addr="derived")
        san_dn = "san-conn-pol-" + inputdict['san_conn_policy_name']
        fc_list = self.handle.query_classid("vnicFc")
        for fc in fc_list:
            if fc.dn.split("/")[1] == san_dn:
                order += 1
                vnic_name = fc.name
                LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", admin_host_port="ANY",
                             order=str(order), transport="fc", vnic_name=vnic_name)
                VnicFc(
                    parent_mo_or_dn=mo,
                    cdn_prop_in_sync="yes",
                    addr="derived",
                    admin_host_port="ANY",
                    admin_vcon="any",
                    stats_policy_name="default",
                    admin_cdn_name="",
                    switch_id="A",
                    pin_to_group_name="",
                    pers_bind="disabled",
                    order=str(order),
                    pers_bind_clear="no",
                    qos_policy_name="",
                    adaptor_profile_name="",
                    ident_pool_name="",
                    cdn_source="vnic-name",
                    max_data_field_size="2048",
                    nw_templ_name="",
                    name=vnic_name)

        VnicFcNode(parent_mo_or_dn=mo,
                   ident_pool_name="node-default", addr="pool-derived")
        # mo_15 = LsRequirement(parent_mo_or_dn=mo, restrict_migration="no", name=inputdict['pool_assignment'], qualifier=inputdict['qualifier'])
        LsRequirement(parent_mo_or_dn=mo, restrict_migration="no",
                      name=inputdict['pool_assignment'], qualifier="")
        LsPower(parent_mo_or_dn=mo, state="admin-up")
        FabricVCon(
            parent_mo_or_dn=mo,
            placement="physical",
            fabric="NONE",
            share="shared",
            select="all",
            transport="ethernet,fc",
            id="1",
            inst_type="auto")
        FabricVCon(
            parent_mo_or_dn=mo,
            placement="physical",
            fabric="NONE",
            share="shared",
            select="all",
            transport="ethernet,fc",
            id="2",
            inst_type="auto")
        FabricVCon(
            parent_mo_or_dn=mo,
            placement="physical",
            fabric="NONE",
            share="shared",
            select="all",
            transport="ethernet,fc",
            id="3",
            inst_type="auto")
        FabricVCon(
            parent_mo_or_dn=mo,
            placement="physical",
            fabric="NONE",
            share="shared",
            select="all",
            transport="ethernet,fc",
            id="4",
            inst_type="auto")

        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nService profile template creation failed\n", logfile)
            loginfo("\nService profile template creation failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile template creation failed")
            return obj
        self.handle.logout()
        customlogs("\nService profile template created successfully\n", logfile)
        dicts['serviceprofilename'] = inputdict['template_name']
	dicts['ident_pool_name'] = inputdict['ident_pool_name']
	dicts['boot_policy_name'] = inputdict['boot_policy_name']
	dicts['power_policy_name'] = inputdict['power_policy_name']
	dicts['local_disk_policy_name'] = inputdict['local_disk_policy_name']
	dicts['biospolicy'] = inputdict['biospolicy']

        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profile template creation successful")
        return obj

    def ucsCreateServiceProfileTemplateForiSCSI(self, inputdict, logfile):
        """
        Create Service Profile template for iSCSI

        :param inputdict: Dictionary (template name,type,boot policy,uuid pool,local disk policy,power policy,iSCSI vNIC name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        loginfo("template_description =" + inputdict['template_desc'])
        message = "Template name: " + \
                  inputdict['template_name'] + \
                  "\nTemplate Description: " + inputdict['template_desc']
        customlogs(message, logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        mo = LsServer(
            parent_mo_or_dn="org-root",
            vmedia_policy_name="",
            ext_ip_state="none",
            bios_profile_name=inputdict["biospolicy"],
            mgmt_fw_policy_name="",
            agent_policy_name="",
            mgmt_access_policy_name="",
            dynamic_con_policy_name="",
            kvm_mgmt_policy_name="",
            sol_policy_name="",
            uuid="0",
            descr="",
            stats_policy_name="default",
            policy_owner="local",
            ext_ip_pool_name="ext-mgmt",
            boot_policy_name=inputdict["boot_policy_name"],
            usr_lbl="",
            host_fw_policy_name="",
            vcon_profile_name="",
            ident_pool_name=inputdict["ident_pool_name"],
            src_templ_name="",
            type=inputdict["type"],
            local_disk_policy_name=inputdict["local_disk_policy_name"],
            scrub_policy_name="",
            power_policy_name=inputdict['power_policy_name'],
            maint_policy_name="default",
            name=inputdict['template_name'],
            power_sync_policy_name="",
            resolve_remote="yes")

        vnic_list = self.handle.query_classid("vnicEther")
        lan_dn = "lan-conn-pol-" + inputdict['lan_conn_policy_name']
        order = 0
        for vnic in vnic_list:
            if vnic.dn.split("/")[1] == lan_dn:
                order += 1
                vnic_name = vnic.name
                LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", admin_host_port="ANY",
                             order=str(order), transport="ethernet", vnic_name=vnic_name)
                VnicEther(
                    parent_mo_or_dn=mo,
                    cdn_prop_in_sync="yes",
                    nw_ctrl_policy_name="",
                    admin_host_port="ANY",
                    admin_vcon="any",
                    stats_policy_name="default",
                    admin_cdn_name="",
                    switch_id="A",
                    pin_to_group_name="",
                    name=vnic_name,
                    order=str(order),
                    qos_policy_name="",
                    adaptor_profile_name="",
                    ident_pool_name="",
                    cdn_source="vnic-name",
                    mtu="1500",
                    nw_templ_name="",
                    addr="derived")

        VnicConnDef(parent_mo_or_dn=mo, san_conn_policy_name="",
                    lan_conn_policy_name=inputdict['lan_conn_policy_name'])

        VnicDefBeh(parent_mo_or_dn=mo, name="", descr="",
                   policy_owner="local", action="none", type="vhba", nw_templ_name="")
        VnicFcNode(parent_mo_or_dn=mo,
                   ident_pool_name="node-default", addr="pool-derived")
        mo_21 = VnicIScsi(
            parent_mo_or_dn=mo,
            cdn_prop_in_sync="yes",
            addr="derived",
            iqn_ident_pool_name="",
            admin_host_port="ANY",
            admin_vcon="any",
            stats_policy_name="default",
            admin_cdn_name="",
            adaptor_profile_name="",
            switch_id="A",
            pin_to_group_name="",
            vnic_name="",
            ext_ip_state="none",
            qos_policy_name="",
            auth_profile_name="",
            ident_pool_name="",
            cdn_source="vnic-name",
            order="unspecified",
            name=inputdict['iSCSI_vNIC_A'],
            nw_templ_name="",
            initiator_name="")
        VnicVlan(parent_mo_or_dn=mo_21, name="", vlan_name="default")
        mo_22 = VnicIScsi(
            parent_mo_or_dn=mo,
            cdn_prop_in_sync="yes",
            addr="derived",
            iqn_ident_pool_name="",
            admin_host_port="ANY",
            admin_vcon="any",
            stats_policy_name="default",
            admin_cdn_name="",
            adaptor_profile_name="",
            switch_id="A",
            pin_to_group_name="",
            vnic_name="",
            ext_ip_state="none",
            qos_policy_name="",
            auth_profile_name="",
            ident_pool_name="",
            cdn_source="vnic-name",
            order="unspecified",
            name=inputdict['iSCSI_vNIC_B'],
            nw_templ_name="",
            initiator_name="")
        VnicVlan(parent_mo_or_dn=mo_22, name="", vlan_name="default")
        VnicIScsiNode(parent_mo_or_dn=mo, initiator_policy_name="",
                      iqn_ident_pool_name=inputdict['iqn_ident_pool_name'], initiator_name="")
        LsPower(parent_mo_or_dn=mo, state="admin-up")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                   share="shared", select="all", transport="ethernet,fc", id="1", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                   share="shared", select="all", transport="ethernet,fc", id="2", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                   share="shared", select="all", transport="ethernet,fc", id="3", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                   share="shared", select="all", transport="ethernet,fc", id="4", inst_type="auto")
        LsRequirement(parent_mo_or_dn=mo, restrict_migration="no",
                      name=inputdict['pool_assignment'], qualifier="")

        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nService profile template creation failed\n", logfile)
            loginfo("\nService profile template creation failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile template creation failed")
            return obj
        self.handle.logout()
        customlogs("\nService profile template is created successfully\n", logfile)
        dicts['serviceprofilename'] = inputdict['template_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profile template creation successful")
        return obj

    def ucsSetiSCSIBootParameters(self, inputdict, logfile):
        """
        Set iSCSI Boot parameters in Boot policy

        :param inputdict: Dictionary (template name,iSCSI vNIC name,iSCSI ip address)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        message = "Template name: " + \
                  inputdict['template_name']
        customlogs(message, logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        if inputdict['iSCSI_Boot'] == "A":
            mo = VnicIScsiBootParams(
                parent_mo_or_dn="org-root/ls-" +
                inputdict['template_name'],
                policy_owner="local",
                descr="")
        else:
            mo = self.handle.query_dn(
                "org-root/ls-" + inputdict['template_name'] + "/" + "iscsi-boot-params")
            mo.policy_owner = "local"
            mo.descr = ""

        mo_1 = VnicIScsiBootVnic(parent_mo_or_dn=mo, initiator_name="", iqn_ident_pool_name="",
                                 auth_profile_name="", policy_owner="local", descr="",
                                 name=inputdict['iSCSI_vNIC_name'])
        mo_1_1 = VnicIScsiStaticTargetIf(parent_mo_or_dn=mo_1, priority="1", port="3260",
                                         ip_address=inputdict['iSCSI_ip_address_eth8'],
                                         name=inputdict['iSCSI_Target_name'], auth_profile_name="")
        VnicLun(parent_mo_or_dn=mo_1_1, bootable="no", id="1")
        mo_1_2 = VnicIScsiStaticTargetIf(parent_mo_or_dn=mo_1, priority="2", port="3260",
                                         ip_address=inputdict['iSCSI_ip_address_eth9'],
                                         name=inputdict['iSCSI_Target_name'], auth_profile_name="")
        VnicLun(parent_mo_or_dn=mo_1_2, bootable="no", id="1")
        mo_1_3 = VnicIPv4If(parent_mo_or_dn=mo_1, name="")

        VnicIPv4PooledIscsiAddr(
            parent_mo_or_dn=mo_1_3, ident_pool_name=inputdict['init_ipaddr_policy'])
        if inputdict['iSCSI_Boot'] == "A":
            self.handle.add_mo(mo)
        else:
            self.handle.set_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nSet iSCSI Boot parameters for iSCSI vNIC failed\n", logfile)
            loginfo("\nSet iSCSI Boot parameters for iSCSI vNIC failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Set iSCSI Boot parameters for iSCSI vNIC failed")
            return obj
        self.handle.logout()
        customlogs(
            "\niSCSI Boot parameters for iSCSI vNIC is set successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "iSCSI Boot parameters for iSCSI vNIC is set successfully")
        return obj

    def ucsDeleteiSCSIBootParams(self, inputs, outputs, logfile):
        """
        Delete iSCSI Boot params from the boot policy

        :param inputs: Dictionary (template name,iSCSI vnic name)
        :param outputs: Output from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        loginfo("Deleting iSCSI Boot params")
        customlogs("Deleting iSCSI Boot params", logfile)
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        try:
            mo = self.handle.query_dn(
                "org-root/ls-" + inputs['template_name'] + "/" + "iscsi-boot-params")

            mo_1 = VnicIScsiBootVnic(
                parent_mo_or_dn=mo,
                initiator_name="",
                iqn_ident_pool_name="",
                auth_profile_name="",
                policy_owner="local",
                descr="",
                name=inputs['iSCSI_vNIC_name'])
            for instance in range(1, 3):
                mo_1_1 = self.handle.query_dn(
                    "org-root/ls-" +
                    inputs['template_name'] +
                    "/" +
                    "iscsi-boot-params/boot-vnic-" +
                    inputs['iSCSI_vNIC_name'] +
                    "/" +
                    str(instance))
                self.handle.remove_mo(mo_1_1)

            mo_1_1 = VnicIPv4If(parent_mo_or_dn=mo_1, name="")
            VnicIPv4PooledIscsiAddr(
                parent_mo_or_dn=mo_1_1, ident_pool_name="iscsi-initiator-pool")
            self.handle.set_mo(mo)

            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Failed to reset iSCSI Boot parameters", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to reset iSCSI Boot parameters")
            return obj
        customlogs("iSCSI Boot parameters reset successfully", logfile)
        obj.setResult(None, PTK_OKAY,
                      "iSCSI Boot parameters reset successfully")
        return obj

    def ucsCreateUplinkPortChannels(self, inputdict, logfile):
        """
        Create uplink port channels

        :param inputdict: Dictionary (name,ports,id)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Uplink Port Channels")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(inputdict)
        message = "Name: " + inputdict['name'] + "\nID: " + \
                  inputdict['id'] + "\nSelected ports: " + inputdict['ports']
        customlogs(message, logfile)

        fabric = "fabric/lan/" + inputdict['ucs_fabric_id']

        mo = FabricEthLanPc(
            parent_mo_or_dn=fabric,
            name=inputdict['name'],
            descr="",
            flow_ctrl_policy="default",
            admin_speed="10gbps",
            auto_negotiate="yes",
            admin_state="enabled",
            oper_speed="10gbps",
            port_id=inputdict['id'],
            lacp_policy_name="default")
        inputdict['ports'] = inputdict['ports'].split('|')
        for port in inputdict['ports']:
            port = FabricEthLanPcEp(
                parent_mo_or_dn=mo,
                eth_link_profile_name="default",
                name="",
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=port)
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            dicts['status'] = 'FAILURE'
            customlogs("Failed to Create Uplink Port Channels", logfile)
            obj.setResult(
                dicts,
                PTK_OKAY,
                "Uplink Port Channels Creation failed")
            return obj

        customlogs("\nUplink Port Channels Created Successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Uplink Port Channels Created Successfully")
        return obj

    def ucsDeleteUplinkPortChannel(self, inputs, outputs, logfile):
        """
        Delete uplink port channel

        :param inputs: Dictionary (ucs_fabric_id, id)
        :param outputs: Result of task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        loginfo("Deleting Uplink Port Channel" + inputs['name'])
        customlogs("Deleting Uplink Port Channel " + inputs['name'], logfile)
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        try:
            fabric = "fabric/lan/" + inputs['ucs_fabric_id']
            mo = self.handle.query_dn(fabric + '/pc-' + inputs['id'])
            if mo is None:
                customlogs("Uplink Port Channel does not exist", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to delete uplink port channel")
                return obj

            self.handle.remove_mo(mo)
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Failed to delete uplink port channel", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to delete uplink port channel")
            return obj
        customlogs("\nUplink Port Channel " +
                   inputs['name'] + " deleted successfully\n", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY,
                      "Uplink Port Channel deleted successfully")
        return obj

    def ucsCreateUUIDSuffixPool(self, inputdict, logfile):
        """
        Create UUID suffix pool

        :param inputdict: Dictionary (name,prefix,order,uuid_from,size)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create UUID Suffix Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("UUID Pool name = " + inputdict['name'])
        loginfo("Prefix = " + inputdict['prefix'])
        loginfo("Assignment order = " + inputdict['order'])
        loginfo("UUID From = " + inputdict['uuid_from'])
        #        loginfo("UUID To = " + inputdict['uuid_to'])
        loginfo("Size = " + inputdict['size'])
        message = "UUID Pool name: " + inputdict['name'] + "\nPrefix: " + inputdict['prefix'] + "\nAssignment order: " + \
            inputdict['order'] + "\nUUID from: " + inputdict['uuid_from'] + "\nSize: " + inputdict['size']
        customlogs(message, logfile)

        uuid_split = inputdict['uuid_from'].split('-')
        uuid_to_int = int(str(uuid_split[1])) + (int(inputdict['size']) - 1)
        uuid_hex = "{:012X}".format(uuid_to_int)
        uuid_to = uuid_split[0] + "-" + uuid_hex
        loginfo("UUID To Block = " + uuid_to)

        mo = UuidpoolPool(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            prefix=inputdict['prefix'],
            descr=inputdict['desc'],
            assignment_order=inputdict['order'],
            name=inputdict['name'])
        UuidpoolBlock(
            parent_mo_or_dn=mo,
            to=uuid_to,
            r_from=inputdict['uuid_from'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            dicts['status'] = 'FAILURE'
            self.handle.logout()
            customlogs("\nCreate UUID Suffix Pool failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "UUID Suffix Pool created failed")
            return obj

        customlogs("\nUUID Suffix Pool created successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(dicts, PTK_OKAY, "UUID Suffix Pool created successfully")
        return obj

    def ucsDeleteUUIDSuffixPool(self, inputs, outputs, logfile):
        """
        Delete UUID suffix pool

        :param inputs: Dictionary (name)
        :param outputs:Result from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Delete UUID Suffix Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("org-root/uuid-pool-" + inputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete UUID Suffix Pool\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete UUID Suffix Pool")
            return obj
        customlogs("\nUUID Suffix pool " +
                   inputs['name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "UUID Suffix pool deleted successfully")
        return obj

    def ucsCreatevHBA(self, inputdict, logfile):
        """
        Create vHBA from vHBA template

        :param inputdict: Dictionary (vhba_name,vhba_template,vsan_con_policy)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        objs = result()
        loginfo("create vHBA")

        if self.handle is None or self.handle_status != True:
            objs.setResult(None, PTK_INTERNALERROR,
                           "Unable to connect to UCS")
            return objs

        dicts = {}
        loginfo("vHBA Name =" + inputdict['vhba_name'])
        loginfo("vHBA Template =" + inputdict['vhba_template'])
        # SAN Connectivity policy name
        loginfo("VSAN Connectivity Policy  Name =" +
                inputdict['vsan_con_policy'])

        message = "vHBA Name: " + inputdict['vhba_name'] + "\nvHBA Template: " + \
                  inputdict['vhba_template'] + "\nvSAN Name: " + \
                  inputdict['vsan_con_policy']

        customlogs(message, logfile)

        mo = self.handle.query_dn(
            "org-root/san-conn-pol-" +
            inputdict['vsan_con_policy'])
        mo_1 = VnicFc(
            parent_mo_or_dn=mo,
            cdn_prop_in_sync="yes",
            addr="default",
            admin_host_port="ANY",
            admin_vcon="any",
            stats_policy_name="default",
            admin_cdn_name="",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            pers_bind="disabled",
            order="1",
            pers_bind_clear="no",
            qos_policy_name="",
            adaptor_profile_name="",
            ident_pool_name="",
            cdn_source="vnic-name",
            max_data_field_size="2048",
            nw_templ_name=inputdict['vhba_template'],
            name=inputdict['vhba_name'])
        VnicFcIf(parent_mo_or_dn=mo_1, name="")
        self.handle.add_mo(mo_1)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nvHBA creation failed\n", logfile)
            objs.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vHBA Template creation failed")
            return objs

        customlogs("\nvHBA created successfully\n", logfile)
        dicts['vhba_name'] = inputdict['vhba_name']
        objs.setResult(dicts, PTK_OKAY, "vHBA creation successful")
        return objs

    def ucsCreatevHBATemplate(self, inputdict, logfile):
        """
        Create vHBA template

        :param inputdict: Dictionary (vhba_name,ucs_fabric_id,vsan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_vHBA_template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("vHBA Name =" + inputdict['vhba_name'])
        loginfo("vHBA Description =" + inputdict['vhba_description'])
        loginfo(
            "Indent Pool Name =" +
            inputdict['ident_pool_name'])  # WWPN Pool
        loginfo("Switch ID =" + inputdict['ucs_fabric_id'])  # fabric ID
        loginfo("Max data field Size =" + inputdict['max_data_field_size'])
        loginfo("VSAN Name =" + inputdict['vsan_name'])  # vSAN

        message = "vHBA Name: " + inputdict['vhba_name'] + "\nvHBA Description: " + inputdict[
            'vhba_description'] + "\nIndent Pool Name: " + inputdict['ident_pool_name'] + \
            "\nSwitch ID: " + inputdict['ucs_fabric_id'] + "\nMax data field size: " + \
            inputdict['max_data_field_size'] + \
            "\nVSAN Name: " + inputdict['vsan_name']

        customlogs(message, logfile)

        mo = VnicSanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_type'],
            name=inputdict['vhba_name'],
            descr=inputdict['vhba_description'],
            stats_policy_name="default",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            peer_redundancy_templ_name="",
            templ_type=inputdict['template_type'],
            qos_policy_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            max_data_field_size=inputdict['max_data_field_size'])
        VnicFcIf(parent_mo_or_dn=mo, name=inputdict['vsan_name'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nvHBA Template creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vHBA Template creation failed")
            return obj

        customlogs("\nvHBA Template created successfully\n", logfile)
        dicts['vhba_name'] = inputdict['vhba_name']
        obj.setResult(dicts, PTK_OKAY, "vHBA Template creation successful")
        return obj

    def ucsDeleteServiceProfilesFromTemplate(self, inputdict, logfile):
        """
        Delete Service Profiles from  template

        :param inputdict: Dictionary (template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        temp_list = []
        mo = self.handle.query_classid("lsServer")
        for ls_mo in mo:
            if ls_mo.type == 'instance':
                if ls_mo.src_templ_name == inputdict['template_name']:
                    temp_list.append(ls_mo.name)
        for j in temp_list:
            mo = self.handle.query_dn("org-root/ls-" + j)
            self.handle.remove_mo(mo)
        try:
            self.handle.commit()

        except UcsException:
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile template deletion failed")
            return obj
        customlogs(
            "\nAll Service profiles with prefix " +
            inputdict['profile_prefix'] +
            " deleted successfully\n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profiles deletion successful")
        return obj

    def ucsDeleteServerPool(self, inputdict, logfile):
        """
        Delete Server pool

        :param inputdict: Dictionary (name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Server Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("org-root/compute-pool-" + inputdict['name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("\nDelete Server Pool failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Server Pool deleted successfully")
            return obj

        customlogs("\nServer Pool " +
                   inputdict['name'] + " deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Server Pool deleted successfully")
        return obj

    def ucsDeleteServiceProfileTemplate(self, inputdict, logfile):
        """
        Delete Service Profile template

        :param inputdict: Dictionary (template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        dicts = {}
        mo = self.handle.query_dn("org-root/ls-" + inputdict['template_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nService profile template deletion failed\n", logfile)
            loginfo("\nService profile template deletion failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile template deletion failed")
            return obj
        customlogs("\n Service profile template " +
                   inputdict['template_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profile template deletion successful")
        return obj

    def ucsDeleteClonedServiceProfileTemplate(self, inputdict, logfile):
        """
        Delete vMedia Service Profile template

        :param inputdict: Dictionary (template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        customlogs(
            "Delete vMedia service profile template started....\n", logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        dicts = {}
        mo = self.handle.query_dn(
            "org-root/ls-" + inputdict['vmedia_template'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nService profile template deletion failed\n", logfile)
            loginfo("\nService profile template deletion failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Service profile template deletion failed")
            return obj
        customlogs(
            "\n vMedia Service profile template " +
            inputdict['vmedia_template'] +
            " deleted successfully\n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "vMedia Service profile template deletion successful")
        return obj

    def ucsDeletevHBATemplate(self, inputdict, logfile):
        """
        Delete vHBA template

        :param inputdict: Dictionary (vhba_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("delete_vHBA")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            "org-root/san-conn-templ-" + inputdict['vhba_name'])
        if mo is None:
            customlogs("\nvHBA template " +
                       inputdict['vhba_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete vHBA template")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nvHBA Template deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vHBA Template deletion failed")
            return obj

        customlogs("\nvHBA Template" +
                   inputdict['vhba_name'] + " deletion successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "vHBA Template deletion successful")
        return obj

    def ucsDeletevHBA(self, inputdict, logfile):
        """
        Delete vHBA

        :param inputdict: Dictionary (vhba_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Delete_vHBA")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            "org-root/san-conn-pol-" +
            inputdict['vsan_con_policy'] +
            "/fc-" +
            inputdict['vhba_name'])

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nvHBA deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vHBA Template deletion failed")
            return obj

        customlogs(
            "\nvHBA " + inputdict['vhba_name'] + " deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "vHBA deletion successful")
        return obj

    def ucsCreateVLAN(self, inputdict, logfile):
        """
        Create VLAN

        :param inputdict: Dictionary (template name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("create_VLAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("VLAN Name =" + inputdict['vlan_name'])
        loginfo("VLAN ID =" + inputdict['vlan_id'])
        loginfo("Sharing =" + inputdict['sharing'])
        loginfo("Multicast Policy =" + " ")

        message = "VLAN Name: " + inputdict['vlan_name'] + "\nVLAN ID: " + inputdict['vlan_id'] + \
                  "\nSharing: " + inputdict['sharing']

        customlogs(message, logfile)

        if self.handle is None:
            customlogs("VLAN creation failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "VLAN creation failed")
            return obj

        mo = FabricVlan(
            parent_mo_or_dn=inputdict["vlan_type"],
            sharing=inputdict['sharing'],
            name=inputdict['vlan_name'],
            id=inputdict['vlan_id'],
            default_net="no",
            mcast_policy_name="",
            compression_type="included")
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("VLAN creation failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "VLAN creation failed")
            return obj

        customlogs("\nVLAN created successfully\n", logfile)
        vlan_id = inputdict['vlan_id']
        if '-' in vlan_id:
            vlan_id = vlan_id.split("-")
            vlan_name_list = [inputdict['vlan_name'] +
                              str(v_id) for v_id in vlan_id]
            dicts['vlan_name'] = vlan_name_list
        else:
            dicts['vlan_name'] = inputdict['vlan_name']
        obj.setResult(dicts, PTK_OKAY, "VLAN creation successful")
        return obj

    def ucsDeleteVLAN(self, inputs, outputs, logfile):
        """
        Delete VLAN

        :param inputs: Dictionary (vlan_name)
        :param outputs: Result of task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Delete VLAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        vlan_type = inputs['vlan_type']
        mo = self.handle.query_dn(vlan_type + "/net-" + inputs['vlan_name'])
        if mo is None:
            customlogs(
                "\nVLAN " + inputs['vlan_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete VLAN")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete VLAN \n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete VLAN")
            return obj
        customlogs("\n VLAN " + inputs["vlan_name"] +
                   " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "VLAN deleted successfully")
        return obj

    def ucsCreatevMediaPolicy(self, inputdict, logfile):
        """
        Create vMedia policy

        :param inputdict: Dictionary (name,mount,descr,mount_name,mount_desc,type,protocol,image_name,remote_file)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create vMedia Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        ntwk = network_info()
        mount_ip = ntwk['ip']

        message = "Name: " + inputdict['name'] + "\nRetry on mount failure: " + inputdict['mount'] + "\nDescription: " + \
                  inputdict['descr'] + "\nvMedia Mount name: " + inputdict['mount_name'] + "\nDescription: " + \
                  inputdict['mount_desc'] + \
                  "\nDevice type: " + inputdict['type'] + "\nProtocol: " + inputdict['protocol'] + \
                  "\nImage name variable: " + \
                  inputdict['image_name'] + "\nRemote file: " + \
                  inputdict['remote_file']
        loginfo("Create vMedia Policy parameters = " + message)
        customlogs(message, logfile)

        mo = CimcvmediaMountConfigPolicy(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            retry_on_mount_fail=inputdict['mount'],
            name=inputdict['name'],
            descr=inputdict['descr'])
        CimcvmediaConfigMountEntry(
            parent_mo_or_dn=mo,
            user_id="",
            description=inputdict['mount_desc'],
            remote_ip_address=mount_ip,
            remote_port="0",
            image_name_variable=inputdict['image_name'],
            auth_option="default",
            mapping_name=inputdict['mount_name'],
            image_file_name=inputdict['remote_file'],
            device_type=inputdict['type'],
            mount_protocol=inputdict['protocol'],
            password="",
            image_path=inputdict['image_path'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create vMedia Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vMedia Policy creation failed")
            return obj

        customlogs("\nvMedia Policy created successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(dicts, PTK_OKAY, "vMedia Policy created successfully")
        return obj

    def ucsDeletevMediaPolicy(self, inputs, outputs, logfile):
        """
        Delete vMedia policy

        :param inputdict: Dictionary (name)
        :param outputs: Result of task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete vMedia Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("org-root/mnt-cfg-policy-" + inputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to delete vMedia Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete vMedia policy")
            return obj
        dicts['status'] = "SUCCESS"
        customlogs("\nvMedia Policy " +
                   inputs['name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "vMedia policy deleted successfully")
        return obj

    def ucsCreatevMotionvNICTemplate(self, inputdict, logfile):
        """
        Create vMotion vNIC Template
        :param inputdict: Dictionary (vmotion_vnic_templ_name,vmotion_vnic_templ_desc,fabric_id,
                                redundancy_pair_type,templ_type,cdn_source,ident_pool_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("create_vMotion_vNIC_Template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(
            "vMotion vNIC Template Name =" +
            inputdict['vmotion_vnic_templ_name'])
        loginfo("vMotion vNIC Template Description =" +
                inputdict['vmotion_vnic_templ_desc'])
        loginfo("Fabric ID =" + inputdict['fabric_id'])
        loginfo("Redundancy Pair Type =" + inputdict['redundancy_pair_type'])
        loginfo("Template Type =" + inputdict['templ_type'])
        loginfo("CDN Source =" + inputdict['cdn_source'])
        loginfo("Ident Pool Name =" + inputdict['ident_pool_name'])
        loginfo("Network Control Policy =" + inputdict['nw_ctrl_policy_name'])
        loginfo("MTU =" + inputdict['mtu'])
        loginfo("VLANS =" + inputdict['vlans'])

        message = "vMotion vNIC Template Name: " + inputdict[
            'vmotion_vnic_templ_name'] + "\nvMotion vNIC Template Desc: " + inputdict[
            'vmotion_vnic_templ_desc'] + "\nFabric ID: " + inputdict['fabric_id'] + "\nRedundancy Pair Type: " + \
            inputdict['redundancy_pair_type'] + \
            "\nTemplate Type: " + inputdict['templ_type'] + "\nCDN Source: " + inputdict[
            'cdn_source'] + "\nIdent Pool Name: " + inputdict['ident_pool_name'] + \
            "\nNetwork Control Policy: " + \
            inputdict['nw_ctrl_policy_name'] + "\nMTU: " + \
            inputdict['mtu'] + "\nDefault Native LAN: " + \
            inputdict['vlans']

        customlogs(message, logfile)

        mo = VnicLanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_pair_type'],
            name=inputdict['vmotion_vnic_templ_name'],
            descr=inputdict['vmotion_vnic_templ_desc'],
            stats_policy_name="",
            admin_cdn_name="",
            switch_id=inputdict['ucs_fabric_id'],
            pin_to_group_name="",
            mtu=inputdict['mtu'],
            peer_redundancy_templ_name=inputdict['peer_red_template'] if inputdict[
                'peer_red_template'] != "not-set" else "",
            templ_type=inputdict['templ_type'],
            qos_policy_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            cdn_source=inputdict['cdn_source'],
            nw_ctrl_policy_name=inputdict['nw_ctrl_policy_name'])
        inputdict['vlans'] = inputdict['vlans'].split('|')
        for name in inputdict['vlans']:
            VnicEtherIf(
                parent_mo_or_dn=mo,
                default_net="yes",
                name=name)

        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("vMotion creation failed", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vMotion vNIC creation failed")
            return obj

        customlogs("\nvMotion vNIC template created successfully\n", logfile)
        dicts['vmotion_vnic_templ_name'] = inputdict['vmotion_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "vMotion vNIC creation successful")
        return obj

    def ucsDeletevMotionvNICTemplate(self, inputs, outputs, logfile):
        """
        Delete vMotion vNIC Template
        :param inputs: Dictionary (vmotion_vnic_templ_name)
        :param outputs:Result of task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete vMotion vNIC template")
        customlogs("Deleting vMotion vNIC template", logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(
            "org-root/lan-conn-templ-" + inputs['vmotion_vnic_templ_name'])
        if mo is None:
            customlogs("\nvMotion vNIC template " +
                       inputs['vmotion_vnic_templ_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete vMotion vNIC template")
            return obj

        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete vMotion vNIC template\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete vMotion vNIC template")
            return obj
        customlogs("\n vMotion vNIC template " +
                   inputs['vmotion_vnic_templ_name'] + " deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "vMotion vNIC template deleted successfully")
        return obj

    def ucsCreatevNICvHBAPlacementPolicy(self, inputdict, logfile):
        """
        Create vNIC vHBA Placement policy
        :param inputdict: Dictionary (name,scheme,port_id,preference)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create vNIC/vHBA Placement Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name" + inputdict['name'] + "\nVirtual slot mapping scheme" + inputdict['scheme'] + \
            "\nVirtual Slot" + inputdict['port_id'] + "\nSelection preference" + inputdict['preference']
        loginfo("Create vNIC/vHBA Placement Policy parameters = " + message)
        customlogs(message, logfile)

        mo = FabricVConProfile(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            name=inputdict['name'],
            descr="",
            mezz_mapping=inputdict['scheme'])

        FabricVCon(
            parent_mo_or_dn=mo,
            placement="physical",
            fabric="NONE",
            share="shared",
            select=inputdict['preference'],
            transport="ethernet,fc",
            id=inputdict['port_id'],
            inst_type="auto")
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Create vNIC/vHBA Placement Policy\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "vNIC/vHBA Placement Policy Creation failed")
            return obj

        customlogs(
            "\nvNIC/vHBA Placement Policy Created Successfully\n",
            logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "vNIC/vHBA Placement Policy Created Successfully")
        return obj

    def ucsDeletevNICvHBAPlacementPolicy(self, inputs, outputs, logfile):
        """
        Delete vNIC vHBA placement polocy
        :param inputdict: Dictionary (name)
        :param logfile: Logfile name
        :param outputs: Result from task execution
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Deleting vNIC vHBA Placement policy" + outputs['name'])

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            "org-root/" + "vcon-profile-" + outputs['name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException:
            customlogs("Failed to delete vNIC/vHBA placement policy", logfile)
            obj.setResult(None, PTK_INTERNALERROR,
                          "Failed to delete vNIC/vHBA placement policy")
            return obj

        self.handle.logout()
        customlogs("\nvNIC/vHBA Placement Policy deleted successfully\n", logfile)
        obj.setResult(None, PTK_OKAY,
                      "vNIC/vHBA placement policy deleted successfully")
        return obj

    def ucsDeleteVSANs(self, inputdict, logfile):
        """
        Delete vSAN
        :param inputdict: Dictionary (vsan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("delete_VSAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            "fabric/san/" + inputdict['ucs_fabric_id'] + "/net-" + inputdict['vsan_name'])
        if mo is None:
            customlogs(
                "\n VSAN " + inputdict['vsan_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete VSAN")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nVSAN deletion failed\n", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "VSAN deletion failed")
            return obj
        customlogs(
            "\nVSAN " + inputdict['vsan_name'] + " deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "VSAN deletion successful")
        return obj

    def ucsCreateVSANs(self, inputdict, logfile):
        """
        Create vSAN
        :param inputdict: Dictionary (vsan_name,fabric_id,vsan_id,fcoe_vlan)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create_VSAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(inputdict)
        loginfo("VSAN Name: " + inputdict['vsan_name'])
        loginfo("Fabric ID: " + inputdict['fabric_id'])
        loginfo("VSAN ID: " + inputdict['vsan_id'])
        loginfo("FCoE VLAN ID: " + inputdict['fcoe_vlan'])

        message = "VSAN Name: " + inputdict['vsan_name'] + "\nFabric ID: " + inputdict['fabric_id'] + \
            "\nVSAN Id: " + inputdict['vsan_id'] + "\nFCoE Id: " + inputdict['fcoe_vlan']

        customlogs(message, logfile)
        fabric_id = "fabric/san/" + inputdict['ucs_fabric_id']
        mo = FabricVsan(
            parent_mo_or_dn=fabric_id,
            name=inputdict['vsan_name'],
            fcoe_vlan=inputdict['fcoe_vlan'],
            zoning_state=inputdict['zoning_state'],
            id=inputdict['vsan_id'])
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nVSAN creation failed\n", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "VSAN creation failed")
            return obj
        customlogs("\nVSAN is created successfully\n", logfile)
        dicts['vsan'] = inputdict['vsan_name']
        dicts['vsan_name'] = fabric_id + \
            "/net-" + inputdict['vsan_name']
        obj.setResult(dicts, PTK_OKAY, "VSAN creation successful")
        return obj

    def ucsCreateWWNNPool(self, inputdict, logfile):
        """
        Create WWNN Pool
        :param inputdict: Dictionary (name,order,from_ip,size)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create WWNN Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Name = " + inputdict['name'])
        loginfo("Assignment order = " + inputdict['order'])
        loginfo("From = " + inputdict['from_ip'])
        loginfo("Size = " + inputdict['size'])
        message = "Name: " + inputdict['name'] + "\nAssignment order: " + \
                  inputdict['order'] + "\nFrom: " + \
                  inputdict['from_ip'] + "\nSize: " + inputdict['size']
        customlogs(message, logfile)

        wwnn_start_addr = str(inputdict['from_ip'])
        wwnn_size = int(inputdict['size'])
        wwnn_int = int(wwnn_start_addr.translate(None, ":.- "), 16)
        wwnn_end_int = wwnn_int + (wwnn_size - 1)
        wwnn_hex = "{:012X}".format(wwnn_end_int)
        wwnn_end = ":".join(wwnn_hex[i:i + 2]
                            for i in range(0, len(wwnn_hex), 2))

        loginfo("WWNN End Block: " + wwnn_end)

        mo = FcpoolInitiators(
            parent_mo_or_dn="org-root",
            name=inputdict['name'],
            policy_owner="local",
            descr=inputdict['desc'],
            assignment_order=inputdict['order'],
            purpose="node-wwn-assignment")
        FcpoolBlock(
            parent_mo_or_dn=mo,
            to=wwnn_end,
            r_from=inputdict['from_ip'])

        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create WWNN Pool\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "WWNN Pool creation failed")
            return obj

        customlogs("\nWWNN Pool created successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(dicts, PTK_OKAY, "WWNN Pool created successfully")
        return obj

    def ucsDeleteIQNPool(self, inputdict, logfile):
        """
        Delete IQN Pool
        :param inputdict: Dictionary (name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete IQN Pool")
        loginfo("Name = " + inputdict['name'])
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("org-root/iqn-pool-" + inputdict['name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nIQN Pool Deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "IQN Pool deletion failed")
            return obj

        customlogs("\nIQN Pool deletion completed successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "IQN Pool deletion completed successfully")
        return obj

    def ucsDeleteWWNPool(self, inputdict, logfile):
        """
        Delete WWNN Pool
        :param inputdict: Dictionary (name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
       """

        obj = result()
        loginfo("Delete WWN Pool")
        loginfo("Name = " + inputdict['name'])
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("org-root/wwn-pool-" + inputdict['name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nWWN Pool Deletion failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "WWN Pool deletion failed")
            return obj

        customlogs("\nWWN Pool deletion completed successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "WWN Pool deletion completed successfully")
        return obj

    def ucsCreateWWPNPool(self, inputdict, logfile):
        """
        Create WWPN Pool
        :param inputdict: Dictionary (name,order,from_ip,size)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create WWPN Pool")
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Name = " + inputdict['name'])
        loginfo("Assignment order = " + inputdict['order'])
        loginfo("From = " + inputdict['from_ip'])
        loginfo("Size = " + inputdict['size'])
        message = "Name: " + inputdict['name'] + "\nAssignment order: " + \
                  inputdict['order'] + "\nFrom: " + \
                  inputdict['from_ip'] + "\nSize: " + inputdict['size']
        customlogs(message, logfile)

        wwpn_start_addr = str(inputdict['from_ip'])
        wwpn_size = int(inputdict['size'])
        wwpn_int = int(wwpn_start_addr.translate(None, ":.- "), 16)
        wwpn_end_int = wwpn_int + (wwpn_size - 1)
        wwpn_hex = "{:012X}".format(wwpn_end_int)
        wwpn_end = ":".join(wwpn_hex[i:i + 2]
                            for i in range(0, len(wwpn_hex), 2))

        loginfo("WWPN End Block= " + wwpn_end)

        mo = FcpoolInitiators(
            parent_mo_or_dn="org-root",
            name=inputdict['name'],
            policy_owner="local",
            descr=inputdict['desc'],
            assignment_order=inputdict['order'],
            purpose="port-wwn-assignment")
        FcpoolBlock(
            parent_mo_or_dn=mo,
            to=wwpn_end,
            r_from=inputdict['from_ip'])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nWWPN Pool creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "WWPN Pool creation failed")
            return obj

        customlogs("\nWWPN Pool creation completed successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "WWPN Pool creation completed successfully")
        return obj

    def ucsEnableServerPorts(self, inputdict, logfile):
        """
        Enable Server Ports
        :param inputdict: Dictionary (ucs_fabric_id,ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Enable Server Ports")
        message = "Ports to be configured as Server Ports: " + \
            inputdict['ports']
        customlogs(message, logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        server = "fabric/server/sw-" + inputdict['ucs_fabric_id']
        ports_list = []
        if 'ports' in inputdict:
            ports_list = inputdict['ports'].split('|')
            for port in ports_list:
                mo = FabricDceSwSrvEp(
                    parent_mo_or_dn=server,
                    name="",
                    auto_negotiate="yes",
                    usr_lbl="",
                    slot_id="1",
                    admin_state="enabled",
                    port_id=port)
                self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Enable Server Ports\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to enable Server Ports")
            return obj

        customlogs("Server Ports enabled successfully\n", logfile)
        if 'ports' in inputdict:
            dicts['ports'] = inputdict['ports']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server Ports enabled successfully")
        return obj

    def ucsEnableUplinkPorts(self, inputdict, logfile):
        """
        Enable uplink ports
        :param inputdict: Dictionary (ucs_fabric_id,ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Enable Uplink Ports")
        message = "Ports to be configured as uplink Ports: " + \
            inputdict['ports']
        customlogs(message, logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        uplink = "fabric/lan/" + inputdict['ucs_fabric_id']

        if 'ports' in inputdict:
            uplink_ports_list = inputdict['ports'].split('|')
            for port in uplink_ports_list:
                mo = FabricEthLanEp(
                    parent_mo_or_dn=uplink,
                    eth_link_profile_name="default",
                    name="",
                    flow_ctrl_policy="default",
                    admin_speed="10gbps",
                    auto_negotiate="yes",
                    usr_lbl="",
                    slot_id="1",
                    admin_state="enabled",
                    port_id=port)
                self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Enable Uplink Ports\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to enable Uplink Ports")
            return obj

        customlogs("Uplink Ports enabled successfully\n", logfile)
        if 'ports' in inputdict:
            dicts['ports'] = inputdict['ports']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Uplink Ports enabled successfully")
        return obj

    def ucsDisableServerPorts(self, inputs, outputs, logfile):
        """
        Disable Server Ports
        :param inputs: Dictionary (ports)
        :param outputs: Result from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Disable Server Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        ports_list = []
        if 'ports' in inputs:
            ports_list = inputs['ports'].split('|')
            for port in ports_list:
                parent_mo = "sys/switch-" + \
                    inputs['ucs_fabric_id'] + \
                    "/slot-1/switch-ether/port-" + port
                mo = self.handle.query_dn(parent_mo)
                if mo.ep_dn != '':
                    mo1 = self.handle.query_dn(mo.ep_dn)
                    self.handle.remove_mo(mo1)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to disable Server Ports\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to disable Server Ports")
            return obj

        customlogs(
            "\nServer Ports " + inputs['ports'] + " for FI " +
            inputs['ucs_fabric_id'] + " disabled successfully\n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server Ports disabled successfully")
        return obj

    def ucsDisableUplinkPorts(self, inputs, outputs, logfile):
        """
        Disable uplink ports
        :param inputs: Dictionary (ports)
        :param outputs: Output from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Disable Uplink Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        uplink = "fabric/lan/" + inputs['ucs_fabric_id']

        if 'ports' in inputs:
            uplink_ports_list = inputs['ports'].split('|')
            for port in uplink_ports_list:
                mo = FabricEthLanEp(
                    parent_mo_or_dn=uplink,
                    eth_link_profile_name="default",
                    name="",
                    flow_ctrl_policy="default",
                    admin_speed="10gbps",
                    auto_negotiate="yes",
                    usr_lbl="",
                    slot_id="1",
                    admin_state="disabled",
                    port_id=port)
                self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to disable Uplink Ports\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to disable Uplink Ports")
            return obj
        customlogs(
            "\nUplink Ports " + inputs['ports'] + " for FI " +
            inputs['ucs_fabric_id'] + " disabled successfully\n",
            logfile)
        customlogs("\nUplink Ports disabled successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Uplink Ports disabled successfully")
        return obj

    def ucsGlobalPolicy(self, inputdict, logfile):

        obj = result()
        loginfo("setting ucs global policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Time Zone = " + inputdict['zone'])
        loginfo("NTP = " + inputdict['ntp'])
        message = "Time Zone: " + \
                  inputdict['zone'] + "\nNTP: " + inputdict['ntp']
        customlogs("Global Policy settings started", logfile)
        customlogs(message, logfile)

        # Chassis/FEX
        mo = ComputeChassisDiscPolicy(
            parent_mo_or_dn="org-root",
            backplane_speed_pref="40G",
            action="2-link",
            link_aggregation_pref="none")
        self.handle.add_mo(mo, True)

        # Rack server
        mo = ComputeServerDiscPolicy(
            parent_mo_or_dn="org-root",
            scrub_policy_name="default",
            action="immediate")
        self.handle.add_mo(mo, True)

        # Rack mgmt
        mo = ComputeServerMgmtPolicy(
            parent_mo_or_dn="org-root",
            action="auto-acknowledged")
        self.handle.add_mo(mo, True)

        # power policy
        mo = ComputePsuPolicy(
            parent_mo_or_dn="org-root",
            redundancy="non-redundant")
        self.handle.add_mo(mo, True)

        # mac address
        mo = FabricLanCloud(parent_mo_or_dn="fabric", mac_aging="mode-default")
        self.handle.add_mo(mo, True)

        # global power
        mo = PowerMgmtPolicy(
            parent_mo_or_dn="org-root",
            style="manual-per-blade")
        # mo = PowerMgmtPolicy(parent_mo_or_dn="org-root", style="intelligent-policy-driven")
        self.handle.add_mo(mo, True)

        # auto sync
        mo = FirmwareAutoSyncPolicy(
            parent_mo_or_dn="org-root",
            sync_state="User Acknowledge")
        # mo = FirmwareAutoSyncPolicy(parent_mo_or_dn="org-root", sync_state="No Actions")
        self.handle.add_mo(mo, True)

        # global power
        mo = PowerMgmtPolicy(parent_mo_or_dn="org-root", profiling="yes")
        # mo = PowerMgmtPolicy(parent_mo_or_dn="org-root", profiling="no")
        self.handle.add_mo(mo, True)

        # info policy
        mo = TopInfoPolicy(parent_mo_or_dn="sys", state="enabled")
        # mo = TopInfoPolicy(parent_mo_or_dn="sys", state="disabled")
        self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to change Global Policies\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Global Policy settings updated successfully")
            return obj
        customlogs("\nChanged the Global Policies successfully\n", logfile)
        customlogs("\nGlobal Policy settings updated successfully\n", logfile)
        dicts['zone'] = mo.timezone
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Global Policy settings updated successfully")
        return obj

    def ucsSetJumboFrames(self, inputdict, logfile):
        """
        Set UCS Jumbo Frames
        :param inputdict: Dictionary (mtu)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Set_Jumbo_Frames")
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("MTU =" + inputdict['mtu'])

        message = "MTU: " + inputdict['mtu']

        customlogs(message, logfile)

        mo = self.handle.query_dn("fabric/lan/classes")
        mo.policy_owner = "local"
        mo.descr = ""

        QosclassEthBE(
            parent_mo_or_dn=mo,
            multicast_optimize="no",
            name="",
            weight="5",
            mtu=inputdict['mtu'])
        self.handle.set_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("\nJumbo frames setting failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Setting jumbo frames failed")
            return obj
        self.handle.logout()
        customlogs("\nJumbo frames is set successfully\n", logfile)
        dicts['mtu'] = inputdict['mtu']
        obj.setResult(dicts, PTK_OKAY, "Setting jumbo frames successful")
        return obj

    def ucsResetJumboFrames(self, inputs, outputs, logfile):
        """
        Reset UCS Jumbo frames
        :param inputs: Dictionary (mtu)
        :param outputs: Dictionary (mtu)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}
        loginfo("Resetting Jumbo Frames Best effort row MTU from " +
                outputs['mtu'] + " to normal")
        customlogs("Resetting Jumbo Frames Best effort row MTU from " +
                   outputs['mtu'] + " to normal", logfile)
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        try:
            mo = self.handle.query_dn("fabric/lan/classes")

            QosclassEthBE(
                parent_mo_or_dn=mo, multicast_optimize="no", name="", weight="5", mtu="normal")
            self.handle.set_mo(mo)
            self.handle.commit()

        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Failed to reset Jumbo frames MTU", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to reset Jumbo frames MTU")
            return obj
        customlogs("\nJumbo frames MTU reset successfully\n", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY, "Jumbo frames mtu reset successfully")
        return obj

    def ucsSynchronizeUCStoNTP(self, inputdict, logfile):
        """
        Synchronize UCS to NTP
        :param inputdict: Dictionary (zone,ntp)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("synchronize ucs to ntp")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Time Zone = " + inputdict['zone'])
        loginfo("NTP = " + inputdict['ntp'])
        message = "Time Zone: " + \
                  inputdict['zone'] + "\nNTP: " + inputdict['ntp']
        customlogs(message, logfile)

        mo = self.handle.query_dn("sys/svc-ext/datetime-svc")
        mo.admin_state = "enabled"
        mo.port = "0"
        mo.descr = ""
        self.handle.set_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to change the Time Zone\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to change the timezone")
            return obj
        customlogs("\nChanged the Time Zone successfully", logfile)

        mo = CommNtpProvider(
            parent_mo_or_dn="sys/svc-ext/datetime-svc",
            name=inputdict['ntp'],
            descr="")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            self.handle.logout()
            customlogs("\nFailed to update NTP server details\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Synchronize UCS to NTP failed")
            return obj
        customlogs("\nNTP server details updated", logfile)

        customlogs("\nSynchronize UCS to NTP is successful\n", logfile)
        # dicts['zone'] = mo.timezone
        obj.setResult(dicts, PTK_OKAY, "Synchronize UCS to NTP successful")
        return obj

    def ucsRollbackSynchronizeUCStoNTP(self, inputs, outputs, logfile):
        """
        Rollback synchronizing UCS to NTP
        :param inputs: Dictionary (ntp)
        :param outputs: Output from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Rollback synchronize UCS to NTP")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("sys/svc-ext/datetime-svc")
        mo.timezone = ""

        mo_1 = self.handle.query_dn(
            "sys/svc-ext/datetime-svc/ntp-" + inputs['ntp'])
        self.handle.remove_mo(mo_1)
        self.handle.set_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to rollback UCS Synchronize to NTP \n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to rollback UCS Synchronize to NTP")
            return obj

        customlogs("\n Rollback Synchronize UCS to NTP successful\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "rollback UCS Synchronize to NTP is completed successfully")
        return obj

    def ucsUpdateDefaultMaintenancePolicy(self, inputdict, logfile):
        """
        Update default maintenance policy
        :param inputdict: Dictionary (uptime,timer,descr,trigger)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Update Default Maintenance Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Update Default Maintenance Policy parameters")

        state = self.handle.query_classid("LsmaintMaintPolicy")
        if inputdict['uptime'] == "immediate":
            message = "Soft Shutdown Timer: " + \
                      inputdict['timer'] + "\nReboot Policy: " + \
                inputdict['uptime']
            customlogs(message, logfile)
            mo = LsmaintMaintPolicy(
                parent_mo_or_dn="org-root",
                uptime_disr=inputdict['uptime'],
                name="default",
                descr=inputdict['descr'],
                trigger_config="",
                soft_shutdown_timer=inputdict['timer'],
                sched_name="",
                policy_owner="local")
        elif inputdict['uptime'] == "timer-automatic":
            message = "Soft Shutdown Timer: " + inputdict['timer'] + "\nReboot Policy: " + inputdict['uptime'] + \
                "\nOn next boot: " + inputdict['trigger'] + "\nSchedule: " + inputdict['sched']
            customlogs(message, logfile)
            mo = LsmaintMaintPolicy(
                parent_mo_or_dn="org-root",
                uptime_disr=inputdict['uptime'],
                name="default",
                descr=inputdict['descr'],
                trigger_config=inputdict['trigger'],
                soft_shutdown_timer=inputdict['timer'],
                sched_name=inputdict['sched'],
                policy_owner="local")
        else:
            message = "Soft Shutdown Timer: " + \
                      inputdict['timer'] + "\nReboot Policy: " + \
                      inputdict['uptime'] + "\nOn next boot: " + \
                inputdict['trigger']
            customlogs(message, logfile)
            mo = LsmaintMaintPolicy(
                parent_mo_or_dn="org-root",
                uptime_disr=inputdict['uptime'],
                name="default",
                descr=inputdict['descr'],
                trigger_config=inputdict['trigger'],
                soft_shutdown_timer=inputdict['timer'],
                sched_name="",
                policy_owner="local")

        self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to Update Default Maintenance Policy\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Update Default Maintenance Policy failed")
            return obj

        self.handle.logout()
        customlogs(
            "\nUpdate Default Maintenance Policy completed successfully\n",
            logfile)
        dicts['trigger'] = state[0].trigger_config
        dicts['timer'] = state[0].soft_shutdown_timer
        dicts['descr'] = state[0].descr
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Update Default Maintenance Policy completed successfully")
        return obj

    def ucsResetMaintenancePolicy(self, inputs, outputs, logfile):
        """
        Reset maintenance policy
        :param inputs: Dictionary ((uptime,timer,descr,trigger)
        :param outputs: Output from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Reset Default Maintenance Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = LsmaintMaintPolicy(
            parent_mo_or_dn="org-root",
            uptime_disr=inputs['uptime'],
            name="default",
            descr=inputs['descr'],
            trigger_config=inputs['trigger'],
            soft_shutdown_timer=inputs['timer'],
            sched_name="",
            policy_owner="local")
        self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to reset default Maintenance Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to reset default maintenance policy")
            return obj
        dicts['status'] = "SUCCESS"
        customlogs("\nDefault Maintenance policy reset successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Default maintenance policy resetted successfully")
        return obj

    def ucsCreateNetworkControlPolicy(self, inputdict, logfile):
        """
        Create network control policy
        :param inputdict: Dictionary (name,cdp,mac_mode,uplink_fail,forge,lldp_tra,lldp_rec)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Network Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nCDP: " + inputdict['cdp'] + "\nMAC Register mode: " + inputdict[
            'mac_mode'] + "\nAction on Uplink fail: " + \
            inputdict['uplink_fail'] + "\nForge: " + inputdict['forge'] + "\nLLDP Transmit: " + \
            inputdict['lldp_tra'] + "\nLLDP Receive: " + inputdict['lldp_rec']
        loginfo("Create Network Control Policy parameters = " + message)
        customlogs(message, logfile)

        mo = NwctrlDefinition(
            parent_mo_or_dn="org-root",
            lldp_transmit=inputdict['lldp_tra'],
            name=inputdict['name'],
            lldp_receive=inputdict['lldp_rec'],
            mac_register_mode=inputdict['mac_mode'],
            policy_owner="local",
            cdp=inputdict['cdp'],
            uplink_fail_action=inputdict['uplink_fail'],
            descr=inputdict['descr'])
        DpsecMac(
            parent_mo_or_dn=mo,
            forge=inputdict['forge'],
            policy_owner="local",
            name="",
            descr="")
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create Network Control Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create network control policy")
            return obj

        customlogs("\nNetwork Control Policy Created Successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Network control policy created successfully")
        return obj

    def ucsDeleteNetworkControlPolicy(self, inputs, outputs, logfile):
        """
        Delete network control policy
        :param inputs: Dictionary (name)
        :param outputs: name : network control policy name
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Network Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("org-root/nwctrl-" + outputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete Network Control Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete network control policy")
            return obj
        customlogs("\nNetwork Control Policy deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Network control policy deleted successfully")
        return obj

    def ucsCreateIQNPoolsForiSCSIBoot(self, inputdict, logfile):
        """
        Create IQN Pools for iSCSI boot
        :param inputdict: Dictionary (name,desc,prefox,suffix,order,suffix_to)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create IQN Pools for iSCSI Boot")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nDescription: " + inputdict['desc'] + \
                  "\nAssignment order: " + inputdict['order'] + "\nPrefix: " + inputdict['prefix'].split(':')[0] + "\nIQN suffix: " + \
                  inputdict['suffix'].split(':')[0] + "\nFrom: " + inputdict['suffix_from'] + \
                  "\nTo: " + inputdict['suffix_to']
        loginfo("Create IQN Pools for iSCSI Boot parameters: " + message)
        customlogs(message, logfile)

        mo = IqnpoolPool(
            parent_mo_or_dn="org-root",
            policy_owner="local",
            prefix=inputdict['prefix'].split(':')[0],
            descr=inputdict['desc'],
            assignment_order=inputdict['order'],
            name=inputdict['name'])
        IqnpoolBlock(
            parent_mo_or_dn=mo,
            to=inputdict['suffix_to'],
            r_from=inputdict['suffix_from'],
            suffix=inputdict['suffix'].split(':')[0])
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create IQN Pools for iSCSI Boot\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create IQN pools for iSCSI boot")
            return obj

        customlogs("\nIQN Pools for iSCSI Boot Created Successfully\n", logfile)
        dicts['name'] = inputdict['name']

        obj.setResult(
            dicts,
            PTK_OKAY,
            "IQN Pools for iSCSI Boot created successfully")
        return obj

    def ucsDeleteIPPoolsForiSCSIBoot(self, inputdict, logfile):
        """
        Delete IP Pools for iSCSI Boot
        :param inputdict: Dictionary (ip_pool_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete IP Pools for iSCSI Boot")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            "org-root/ip-pool-" + inputdict['ip_pool_name'])
        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete IP Pools for iSCSI Boot\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete IP pools for iSCSI boot")
            return obj

        customlogs("\nIP Pools for iSCSI Boot Deleted Successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "IP Pools for iSCSI Boot deleted successfully")
        return obj

    def ucsCreateIPPoolsForiSCSIBoot(self, inputdict, logfile):
        """
        Create IP Pools for iSCSI Boot
        :param inputdict: Dictionary (ip_pool_name,order,desc,ip_from,size)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create IP Pools for iSCSI Boot")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['ip_pool_name'] + "\nDescription: " + inputdict['desc'] + \
                  "\nAssignment order: " + inputdict['order'] + "\nFrom IP: " + inputdict['ip_from'] + "\nSize: " + \
                  inputdict['size']
        loginfo("Create IP Pools for iSCSI Boot parameters = " + message)
        customlogs(message, logfile)

        ip_from = inputdict['ip_from']
        ip_addr_split = ip_from.split('.')
        ip_increment = int(ip_addr_split[3]) + int(inputdict['size']) - 1
        ip_addr_split[3] = str(ip_increment)
        to_ip_addr = '.'.join(ip_addr_split)

        mo = IppoolPool(
            parent_mo_or_dn="org-root",
            is_net_bios_enabled="disabled",
            name=inputdict['ip_pool_name'],
            descr=inputdict['desc'],
            policy_owner="local",
            ext_managed="internal",
            supports_dhcp="disabled",
            assignment_order=inputdict['order'])
        IppoolBlock(parent_mo_or_dn=mo, to=to_ip_addr,
                    r_from=inputdict['ip_from'], def_gw="0.0.0.0")
        self.handle.add_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create IP Pools for iSCSI Boot\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create IP pools for iSCSI boot")
            return obj

        customlogs("\nIP Pools for iSCSI Boot created Successfully\n", logfile)
        dicts['ip_pool_name'] = inputdict['ip_pool_name']

        obj.setResult(
            dicts,
            PTK_OKAY,
            "IP Pools for iSCSI Boot created successfully")
        return obj

    def ucsunbindfromthetemplate(self, inputdict, logfile):
        """
        Unbind from service profile template
        :param inputdict: Dictionary (vmedia_policy_name,bios_profile_name,boot_policy_name,ident_pool_name
                                        local_disk_policy_name,power_policy_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS unbind from the template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = LsServer(
            parent_mo_or_dn="org-root",
            vmedia_policy_name=inputdict['vmedia_policy_name'],
            ext_ip_state="none",
            bios_profile_name=inputdict['bios_profile_name'],
            mgmt_fw_policy_name="",
            agent_policy_name="",
            mgmt_access_policy_name="",
            dynamic_con_policy_name="",
            kvm_mgmt_policy_name="",
            sol_policy_name="",
            uuid="",
            descr="",
            stats_policy_name="default",
            policy_owner="local",
            ext_ip_pool_name="ext-mgmt",
            boot_policy_name=inputdict['boot_policy_name'],
            usr_lbl="",
            host_fw_policy_name="",
            vcon_profile_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            src_templ_name="",
            local_disk_policy_name=inputdict['local_disk_policy_name'],
            scrub_policy_name="",
            power_policy_name=inputdict['power_policy_name'],
            maint_policy_name="default",
            name=inputdict['service_profile_name'],
            power_sync_policy_name="",
            resolve_remote="yes")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException:
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to unbind from the template")
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Unbind from the template successfully")
        return obj

    def ucsbindtoatemplate(self, inputdict, logfile):
        """
        Bind service profile to template
        :param inputdict: Dictionary (vmedia_policy_name,bios_profile_name,boot_policy_name,ident_pool_name
                                        local_disk_policy_name,power_policy_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS bind to a  template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = LsServer(
            parent_mo_or_dn="org-root",
            vmedia_policy_name=inputdict['vmedia_policy_name'],
            ext_ip_state="none",
            bios_profile_name=inputdict['bios_profile_name'],
            mgmt_fw_policy_name="",
            agent_policy_name="",
            mgmt_access_policy_name="",
            dynamic_con_policy_name="",
            kvm_mgmt_policy_name="",
            sol_policy_name="",
            uuid="",
            descr="",
            stats_policy_name="default",
            policy_owner="local",
            ext_ip_pool_name="ext-mgmt",
            boot_policy_name=inputdict['boot_policy_name'],
            usr_lbl="",
            host_fw_policy_name="",
            vcon_profile_name="",
            ident_pool_name=inputdict['ident_pool_name'],
            src_templ_name=inputdict['service_profile_template'],
            local_disk_policy_name=inputdict['local_disk_policy_name'],
            scrub_policy_name="",
            power_policy_name=inputdict['power_policy_name'],
            maint_policy_name="default",
            name=inputdict['service_profile_name'],
            power_sync_policy_name="",
            resolve_remote="yes")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException:
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to bind to a  template")
        obj.setResult(
            dicts,
            PTK_OKAY,
            "bind to a  template successfully")
        return obj

    def bladeFirmwareUpgrade(self, inputdict, logfile, ipaddress, username, password):
        """
        Perform blade firmware upgrade
        :param inputdict: Dictionary (blade_upg)
        :param logfile: Logfile name
        :ipaddress: ipaddress of the Fabric Interconnect
        :username: username of the fabric interconnect
        :password: password of the fabric interconnect
        :return: Returns the status of the execution
        """

        obj = result()
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        blade_upg = eval(inputdict['blade_upg'])
        if blade_upg['upgrade']['value'] == "Yes" and blade_upg['firmware']['value'] != "":
            customlogs("Blade server firmware upgrade started", logfile)
            status, msg = ucsm_upgrade(ip=ipaddress, username=username, password=password,
                                       blade=blade_upg['firmware']['value'], logfile=logfile)
            if not status:
                dicts['status'] = "FAILURE"
                customlogs("Failed to upgrade blade server package", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Blade server firmware upgrade failed")
                return obj
            customlogs("Blade server firmware upgrade completed", logfile)

        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      "Blade firmware task completed")
        return obj

    def ucs_configure_fc_storage_port(self, inputdict, logfile):
        """
        Configure FC storage port

        :param inputdict: Dictionary (Number of ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("configure_fc_storage_port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("No of FC Storage ports to be configured: " +
                inputdict['fc_ports'])

        message = "\nFC Ports to be configured as Storage port: " + \
            inputdict['fc_ports']

        customlogs(message, logfile)
        ports_range = inputdict['fc_ports'].split('|')
        for i in ports_range:
            i = "%s" % i
            mo = FabricFcEstcEp(
                parent_mo_or_dn="fabric/fc-estc/" +
                inputdict['ucs_fabric_id'],
                name="",
                fill_pattern="arbff",
                auto_negotiate="yes",
                usr_lbl="",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nConfiguring FC storage ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Configuring FC Storage ports failed")
            return obj
        customlogs("\nFC Storage Port configured successfully\n", logfile)
        dicts['fc_ports'] = inputdict['fc_ports']
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "Storage ports configured successfully")
        return obj

    def ucs_unconfigure_fc_storage_port(self, inputdict, logfile):
        """
        Unconfigure FC storage port.

        :param inputdict: Dictionary (Number of ports)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("unconfigure_fc_storage_port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("No of FC Storage ports to be configured: " +
                inputdict['fc_ports'])

        message = "\nFC Ports to be configured as Storage port: " + \
            inputdict['fc_ports']

        customlogs(message, logfile)
        ports_range = inputdict['fc_ports'].split('|')
        for i in ports_range:
            i = "%s" % i
            mo = FabricFcSanEp(
                parent_mo_or_dn="fabric/san/" +
                inputdict['ucs_fabric_id'],
                name="",
                fill_pattern="arbff",
                auto_negotiate="yes",
                usr_lbl="",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nUnconfiguring FC storage ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Unconfiguring FC Storage ports failed")
            return obj
        customlogs("\nFC Storage Port unconfigured successfully\n", logfile)
        dicts['fc_ports'] = inputdict['fc_ports']
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "Storage ports unconfigured successfully")
        return obj

    def ucs_assign_vsan_fc_storage_port(self, inputdict, logfile):
        """
        Assign Storage cloud VSAN on each of the FC port in both the Fabrics

        :param inputdict: Dictionary (fc_ports,vsan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("assign_storage_cloud_vsan_storage_port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        ports_range = inputdict['fc_ports'].split('|')
        for i in ports_range:
            i = "%s" % i
            mo = FabricFcVsanPortEp(
                parent_mo_or_dn="fabric/fc-estc/" +
                inputdict['ucs_fabric_id'] +
                "/net-" +
                inputdict['vsan_name'],
                name="",
                switch_id=inputdict['ucs_fabric_id'],
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nAssigning VSAN to FC storage ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Assigning VSAN to FC Storage ports failed")
            return obj
        customlogs(
            "\nStorage Cloud VSAN " +
            inputdict['vsan_name'] +
            " assigned to FC Storage Port successfully\n",
            logfile)
        dicts['fc_ports'] = inputdict['fc_ports']
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "VSAN assigned to Storage ports successfully")
        return obj

    def ucs_assign_default_vsan_fc_storage_port(self, inputdict, logfile):
        """
        Assign default VSAN on each of the FC port in both the Fabrics

        :param inputdict: Dictionary (fc_ports,vsan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("ucs_assign_default_vsan_fc_storage_port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        ports_range = inputdict['fc_ports'].split('|')
        for i in ports_range:
            i = "%s" % i
            mo = FabricFcVsanPortEp(
                parent_mo_or_dn="fabric/fc-estc/net-default",
                name="",
                switch_id=inputdict['ucs_fabric_id'],
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=i)
            self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nAssigning default VSAN to FC storage ports failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Assigning default VSAN to FC Storage ports failed")
            return obj
        customlogs("\nDefault VSAN assigned to FC Storage Port successfully\n", logfile)
        dicts['fc_ports'] = inputdict['fc_ports']
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "default VSAN assigned to Storage ports successfully")
        return obj

    def configureCiscoUCSCallHome(self, inputdict, logfile):
        """
        Configure Cisco UCS Call Home
        :param inputdict: Dictionary ()
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Configure Cisco UCS Call Home")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("call-home")
        mo.policy_owner = "local"
        mo.name = ""
        mo.alert_throttling_admin_state = inputdict['throttling']
        mo.admin_state = inputdict['state']
        mo.descr = ""

        mo_1 = CallhomeSource(
            parent_mo_or_dn=mo,
            email=inputdict['email'],
            r_from=inputdict['email_from'],
            contract=inputdict['contract_id'],
            reply_to=inputdict['reply_to'],
            site=inputdict['site_id'],
            phone=inputdict['phone'],
            contact=inputdict['contact'],
            customer=inputdict['customer_id'],
            urgency=inputdict['switch_priority'],
            addr=inputdict['address'])
        self.handle.set_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to \n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to Configure Cisco UCS Call Home")
            return obj
        dicts['status'] = "SUCCESS"
        customlogs("\nConfigured UCS Call Home successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Configured UCS Call Home successfully")
        return obj

    def UnConfigureCiscoUCSCallHome(self, inputdict, logfile):
        """
        Unconfigure Cisco Call Home
        :param inputdict: Dictionary ()
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Unconfigure Cisco Call Home")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn("call-home")
        mo.policy_owner = "local"
        mo.name = ""
        mo.alert_throttling_admin_state = inputdict['throttling']
        mo.admin_state = inputdict['state']
        mo.descr = ""

        self.handle.set_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to \n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to Unconfigure Cisco Call Home")
            return obj

    def ucs_set_fc_switching_mode(self, inputdict, logfile):
        """
        Set Fibre channel switching mode to switching

        :param inputdict: Dictionary (Fabric ID)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("ucs_set_fc_switching_mode")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        # Set the FC switching mode restarts both the fabric interconnects in a cluster
        mo = FabricSanCloud(parent_mo_or_dn="fabric", mode="switch")
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nUnable to set Fibre Channel switching mode to switching\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Setting Fibre channel switching mode to switching failed")
            return obj

        loginfo("waiting for both the fabric interconnects to restart after configuring switching mode")
        ucs_mac_id = inputdict['sec_fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for subordinate FI to reboot\n", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of subordinate FI " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)
        # acknowledge primary fabric interconnect reboot
        loginfo("acknowledge primary fi reboot")
        time.sleep(200)  # time required for subordinate to come from inapplicable state
        customlogs("Subordinate FI rebooted successfully\n", logfile)
        mo = FirmwareAck(parent_mo_or_dn="sys/fw-system", admin_state="trigger-immediate")
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Unable to reboot primary FI", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Unable to firmware acknowledge primary FI")
            return obj

        ucs_pri_mac_id = inputdict['pri_fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_pri_mac_id)
        fabric_ip = cred['vipaddress']
        pri_ipaddr = cred['ipaddress']
        customlogs("Waiting for primary FI to reboot\n", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(pri_ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of primary FI " + pri_ipaddr)
            ucsm.verify_ucsm_accessible(pri_ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)
        customlogs("Primary FI rebooted successfully\n", logfile)
        customlogs("\nFibre Channel switching mode configured successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Switching port mode configure successfully")
        return obj

    def ucs_set_fc_endhost_mode(self, inputdict, logfile):
        """
        Set Fibre channel switching mode to end host

        :param inputdict: Dictionary (Fabric ID)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("ucs_set_fc_endhost_mode")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        # Set the FC switching mode restarts both the fabric interconnects in a cluster
        mo = FabricSanCloud(parent_mo_or_dn="fabric", mode="end-host")
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nUnable to set Fibre Channel switching mode to end host\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Setting Fibre channel mode to endhost failed")
            return obj
        customlogs("\nFibre Channel switching mode configured successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "FC End host mode configured successfully")

        loginfo("waiting for both the fabric interconnects to restart after configuring switching mode")
        ucs_mac_id = inputdict['pri_fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for subordinate FI to reboot\n", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of subordinate FI " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)
        # acknowledge primary fabric interconnect reboot
        loginfo("acknowledge primary fi reboot")
        time.sleep(200)  # time required for subordinate to come from inapplicable state
        mo = FirmwareAck(parent_mo_or_dn="sys/fw-system", admin_state="trigger-immediate")
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Unable to reboot primary FI", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Unable to firmware acknowledge primary FI")
            return obj

        ucs_pri_mac_id = inputdict['sec_fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_pri_mac_id)
        fabric_ip = cred['vipaddress']
        pri_ipaddr = cred['ipaddress']
        customlogs("Waiting for primary FI to reboot\n", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(pri_ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of primary FI " + pri_ipaddr)
            ucsm.verify_ucsm_accessible(pri_ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)
        return obj

    def ucsCreateStorageVSAN(self, inputdict, logfile):
        """
        Create Storage vSAN for UCS Direct connectivity to FlashArray
        :param inputdict: Dictionary (vsan_name,fabric_id,vsan_id,fcoe_vlan)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create_Storage_VSAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("VSAN Name: " + inputdict['vsan_name'])
        loginfo("Fabric ID: " + inputdict['fabric_id'])
        loginfo("VSAN ID: " + inputdict['vsan_id'])
        loginfo("FCoE VLAN ID: " + inputdict['fcoe_vlan'])
        loginfo("Zoning State: " + inputdict['zoning_state'])

        message = "VSAN Name: " + inputdict['vsan_name'] + "\nFabric ID: " + inputdict['fabric_id'] + "\nVSAN Id: " + \
            inputdict['vsan_id'] + "\nFCoE Id: " + inputdict['fcoe_vlan'] + "\nZoning State: " + inputdict['zoning_state']

        customlogs(message, logfile)
        fabric_id = "fabric/fc-estc/" + inputdict['ucs_fabric_id']
        mo = FabricVsan(
            parent_mo_or_dn=fabric_id,
            name=inputdict['vsan_name'],
            fcoe_vlan=inputdict['fcoe_vlan'],
            zoning_state=inputdict['zoning_state'],
            id=inputdict['vsan_id'])
        self.handle.add_mo(mo, True)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nStorage VSAN creation failed\n", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "VSAN creation failed")
            return obj
        customlogs("\nStorage VSAN is created successfully\n", logfile)
        dicts['vsan'] = inputdict['vsan_name']
        dicts['vsan_name'] = fabric_id + \
            "/net-" + inputdict['vsan_name']
        obj.setResult(dicts, PTK_OKAY, "VSAN creation successful")
        return obj

    def ucsDeleteStorageVSAN(self, inputdict, logfile):
        """
        Delete Storage Cloud vSAN
        :param inputdict: Dictionary (vsan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("delete_storage_VSAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = self.handle.query_dn(
            "fabric/fc-estc/" + inputdict['ucs_fabric_id'] + "/net-" + inputdict['vsan_name'])
        if mo is None:
            customlogs(
                "\n VSAN " + inputdict['vsan_name'] + " does not exist\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete VSAN")
            return obj

        self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nStorage VSAN deletion failed\n", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "Storage VSAN deletion failed")
            return obj
        customlogs(
            "\nStorage Cloud VSAN " + inputdict['vsan_name'] + " deleted successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "VSAN deletion successful")
        return obj

    def ucsConfigureAppliancePorts(self, inputdict, logfile):
        """
        Configure Ports connected to storage array as Appliance port
        :param inputdict: Dictionary (vsan_name,fabric_id,vsan_id,fcoe_vlan)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Configure_Appliance_Port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Appliance port: " + inputdict['ports'])

        message = "Appliance port: " + inputdict['ports']

        customlogs(message, logfile)
        parent_mo = "fabric/eth-estc/" + inputdict['ucs_fabric_id']

        ports_list = []
        if 'ports' in inputdict:
            ports_list = inputdict['ports'].split('|')
            for port in ports_list:
                mo = FabricEthEstcEp(
                    parent_mo_or_dn=parent_mo,
                    port_mode="trunk",
                    name="",
                    prio="best-effort",
                    flow_ctrl_policy="default",
                    admin_speed="10gbps",
                    usr_lbl="",
                    auto_negotiate="yes",
                    slot_id="1",
                    admin_state="enabled",
                    pin_group_name="",
                    port_id=port,
                    nw_ctrl_policy_name="default")
                self.handle.add_mo(mo, True)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nAppliance Port configuration failed\n", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR, "Appliance port configuration failed")
            return obj
        customlogs("\nAppliance port configured successfully\n", logfile)
        dicts['ports'] = inputdict['ports']
        obj.setResult(dicts, PTK_OKAY, "Appliance port configured successfully")
        return obj

    def ucsUnconfigureAppliancePorts(self, inputs, outputs, logfile):
        """
        Unconfigure ports connected to storage array(Appliance ports)
        :param inputs: Dictionary (ports)
        :param outputs: Output from task execution
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("UCS Unconfigure Appliance Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        if 'ports' in inputs:
            uplink_ports_list = inputs['ports'].split('|')
            for port in uplink_ports_list:
                mo = self.handle.query_dn(
                    "fabric/eth-estc/" +
                    inputs['ucs_fabric_id'] +
                    "/phys-eth-slot-1-port-" +
                    port)
                self.handle.remove_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to unconfigure appliance ports\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to unconfigure appliance ports")
            return obj
        customlogs(
            "\nAppliance ports " + inputs['ports'] + " for FI " +
            inputs['ucs_fabric_id'] + " unconfigured successfully\n",
            logfile)
        customlogs("\nAppliance ports unconfigured successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Appliance ports unconfigured successfully")
        return obj

    def ucsCreateNCPForAppliancePort(self, inputdict, logfile):
        """
        Create network control policy
        :param inputdict: Dictionary (name,cdp,mac_mode,uplink_fail,forge,lldp_tra,lldp_rec)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Create Network Control Policy for Appliance Port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nCDP: " + inputdict['cdp'] + "\nMAC Register mode: " + inputdict[
            'mac_mode'] + "\nAction on Uplink fail: " + \
            inputdict['uplink_fail'] + "\nForge: " + inputdict['forge'] + "\nLLDP Transmit: " + \
            inputdict['lldp_tra'] + "\nLLDP Receive: " + inputdict['lldp_rec']
        loginfo("Create Network Control Policy parameters = " + message)
        customlogs(message, logfile)

        mo = NwctrlDefinition(
            parent_mo_or_dn="fabric/eth-estc",
            lldp_transmit=inputdict['lldp_tra'],
            name=inputdict['name'],
            lldp_receive=inputdict['lldp_rec'],
            mac_register_mode=inputdict['mac_mode'],
            policy_owner="local",
            cdp=inputdict['cdp'],
            uplink_fail_action=inputdict['uplink_fail'],
            descr=inputdict['descr'])
        DpsecMac(
            parent_mo_or_dn=mo,
            forge=inputdict['forge'],
            policy_owner="local",
            name="",
            descr="")
        self.handle.add_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Create Network Control Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create network control policy")
            return obj

        customlogs("\nNetwork Control Policy for Appliance port created successfully\n", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Network control policy created successfully")
        return obj

    def ucsDeleteNCPForAppliancePorts(self, inputs, outputs, logfile):
        """
        Delete network control policy for appliance ports
        :param inputs: Dictionary (name)
        :param outputs: name : network control policy name
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Delete Network Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
        mo = self.handle.query_dn("fabric/eth-estc/nwctrl-" + outputs['name'])
        self.handle.remove_mo(mo)

        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("\nFailed to Delete Network Control Policy\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to delete network control policy")
            return obj
        customlogs("\nNetwork Control Policy for appliance ports deleted successfully\n", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Network control policy deleted successfully")
        return obj

    def ucsApplyPoliciesToAppliancePorts(self, inputdict, logfile):
        """
        Apply Network Control policy and VLAN to the appliance port
        :param inputdict: Dictionary (ports, ncp_name, vlan)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Apply policies to Appliance Port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Appliance Interfaces: " + inputdict['ports'] + "\nNetwork Control Policy: " + inputdict['ncp_name'] + \
            "\nAppliance VLAN: " + inputdict[
            'vlan']
        loginfo("Apply policies and VLAN to Appliance ports: " + message)
        customlogs(message, logfile)
        ports = inputdict['ports'].split('|')
        for port in ports:
            # Set the appliance VLAN as native in Appliance port
            mo = FabricEthVlanPortEp(
                parent_mo_or_dn="fabric/eth-estc/" +
                inputdict['ucs_fabric_id'] +
                "/net-" +
                inputdict['vlan'],
                name="",
                is_native="yes",
                switch_id=inputdict['ucs_fabric_id'],
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=port)
            self.handle.add_mo(mo, True)
            # Remove the default default vlan
            mo = self.handle.query_dn(
                "fabric/eth-estc/net-default/phys-switch-" +
                inputdict['ucs_fabric_id'] +
                "-slot-1-port-" +
                port)
            self.handle.remove_mo(mo)

            mo = self.handle.query_dn(
                "fabric/eth-estc/" +
                inputdict['ucs_fabric_id'] +
                "/phys-eth-slot-1-port-" +
                port)
            mo.prio = "best-effort"
            mo.flow_ctrl_policy = "default"
            mo.auto_negotiate = "yes"
            mo.admin_state = "enabled"
            mo.pin_group_name = ""
            mo.port_mode = "trunk"
            mo.nw_ctrl_policy_name = inputdict['ncp_name']

            self.handle.set_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to apply network control policy and VLAN to appliance interfaces\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create network control policy")
            return obj

        customlogs(
            "\nNetwork Control Policy and VLAN set to appliance interfaces successfully\n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Policies set to appliance interfaces successfully")
        return obj

    def ucsRemovePoliciesFromAppliancePorts(self, inputdict, logfile):
        """
        Remove Network Control policy and VLAN from the appliance port
        :param inputdict: Dictionary (ports, ncp_name, vlan)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """

        obj = result()
        loginfo("Remove policies from Appliance Port")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Appliance Interfaces: " + inputdict['ports'] + "\nNetwork Control Policy: " + inputdict['ncp_name'] + \
            "\nAppliance VLAN: " + inputdict[
            'vlan']
        loginfo("Remove policies and VLAN from Appliance ports: " + message)
        customlogs(message, logfile)
        ports = inputdict['ports'].split('|')
        for port in ports:
            # Set the  default VLAN as native in Appliance port and remove the Appliance VLAN
            mo = FabricEthVlanPortEp(
                parent_mo_or_dn="fabric/eth-estc/net-default",
                name="",
                is_native="yes",
                switch_id=inputdict['ucs_fabric_id'],
                auto_negotiate="yes",
                slot_id="1",
                admin_state="enabled",
                port_id=port)
            self.handle.add_mo(mo, True)

            mo = self.handle.query_dn(
                "fabric/eth-estc/" +
                inputdict['ucs_fabric_id'] +
                "/net-" +
                inputdict['vlan'] +
                "/phys-switch-" +
                inputdict['ucs_fabric_id'] +
                "-slot-1-port-" +
                port)
            self.handle.remove_mo(mo)

            mo = self.handle.query_dn(
                "fabric/eth-estc/" +
                inputdict['ucs_fabric_id'] +
                "/phys-eth-slot-1-port-" +
                port)
            mo.prio = "best-effort"
            mo.flow_ctrl_policy = "default"
            mo.auto_negotiate = "yes"
            mo.admin_state = "enabled"
            mo.pin_group_name = ""
            mo.port_mode = "trunk"
            mo.nw_ctrl_policy_name = ""

            self.handle.set_mo(mo)
        try:
            self.handle.commit()
        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs(
                "\nFailed to remove network control policy and VLAN from appliance interfaces\n",
                logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Failed to create network control policy")
            return obj

        customlogs(
            "\nNetwork Control Policy and VLAN reset in appliance interfaces successfully\n",
            logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Policies removed from appliance interfaces successfully")
        return obj
