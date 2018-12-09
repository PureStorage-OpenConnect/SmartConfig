from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs import *
from pure_dir.components.common import *
from pure_dir.services.utils import *
from ucsmsdk.mometa.ls.LsVConAssign import LsVConAssign
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
import datetime


class UCSTasks:

    def __init__(self, ipaddress='', username='', password=''):
        try:
	    if ipaddress:
                self.handle = UcsHandle(ipaddress, username, password)
                self.handle_status = self.handle.login()
        except:
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

    def deletebootpolicy(self, inputdict, logfile):
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
                   inputdict['boot_policy_name'] + " deletion successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Boot Policy deletion successful")
        return obj

    def createbootpolicy(self, inputdict, logfile):
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

        customlogs("Create Boot Policy....\n", logfile)
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

        customlogs("\nBoot Policy creation successful\n", logfile)
        dicts['bootpolicyname'] = "org-root/boot-policy-" + \
                                  inputdict['boot_policy_name']
        obj.setResult(dicts, PTK_OKAY, "Boot Policy creation successful")
        return obj

    def deleteRemoteDiskToBootPolicies(self, inputdict, logfile):
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
            "\n Delete remote disk to boot policy is successful \n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "delete Remote Disk To Boot Policies  successful")
        return obj

    def addRemoteDiskToBootPolicies(self, inputdict, logfile):
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
            customlogs("\nBoot Policy creation failed\n", logfile)
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Boot Policy creation failed")
            return obj

        obj.setResult(dicts, PTK_OKAY, "Boot Policy creation successful")
        return obj

    def deleteSanBootToBootPolicy(self, inputdict, logfile):
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
            "\nDelete SAN Boot of type " +
            inputdict['type'] + "  with vhba " +
            inputdict['vhba'] + " is successful \n",
            logfile)
        res_obj.setResult(
            dicts, PTK_OKAY, "Delete SAN Boot to boot policy successful")
        return res_obj

    def addSanBootToBootPolicy(self, inputdict, logfile):
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
        customlogs("\nAdding san boot to boot policy successful\n", logfile)
        dicts['type'] = inputdict['type']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Adding san boot to boot policy successful")
        return obj

    def deleteSanBootTarget(self, inputdict, logfile):
        obj = result()
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo_obj = self.handle.query_dn(inputdict['bootpolicyname'])
        mo = LsbootSan(parent_mo_or_dn=mo_obj, order="2")
        mo_1 = LsbootSanCatSanImage(
            parent_mo_or_dn=mo, type=inputdict['san_type'])
        mo_1_1 = self.handle.query_dn(
            inputdict['bootpolicyname'] + "/san/sanimg-" + inputdict['san_type'] + "/sanimgpath-" + inputdict['type'])
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
        customlogs("\nDelete SAN Boot Target of type " + inputdict['type'] + "for the SAN Boot type " + inputdict[
            'san_type'] + " successful \n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Delete SAN Boot Target successful")
        return obj

    def addSanBootTarget(self, inputdict, logfile):
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

        customlogs("\nAdd San Boot Target successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Add San Boot Target successful")
        return obj

    def deleteiSCSIBoot(self, inputdict, logfile):
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

        customlogs("\nDelete ISCSI Boot Target successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Delete ISCSI Boot Target successful")
        return obj

    def addiSCSIBoot(self, inputdict, logfile):
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

        customlogs("\nAdd iSCSI Boot to boot policy successful\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Add iSCSI Boot to boot policy successful")
        return obj

    def deleteCimcMountedDisk(self, inputdict, logfile):
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

        customlogs("\nDelete cimc mounted disc successful\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Delete cimc mounted disc successful")
        return obj

    def addCimcMountedDisk(self, inputdict, logfile):
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
        customlogs("\nCimc Mounted Disk added successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Cimc Mounted Disk added successfully")
        return obj

    def acknowledgeUcsChassis(self, inputdict, logfile):
        obj = result()
        loginfo("Acknowledge Cisco UCS Chassis")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Acknowledge state = " + inputdict['state'])
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
        for attempts in range(10):
            try:
                self.handle.commit()
            except UcsException as e:
                customlogs(str(e), logfile)
                customlogs(
                    "\nFailed to Acknowledge Cisco UCS Chassis\n", logfile)
                continue
                obj.setResult(
                    dicts,
                    PTK_INTERNALERROR,
                    "Acknowledge UCS Chassis failed")
                return obj
            else:
                break

	# Sleep for blade servers to be discovered
	time.sleep(120)

        customlogs("\nAcknowledge Cisco UCS Chassis successful\n", logfile)
        dicts['state'] = inputdict['state']
        obj.setResult(dicts, PTK_OKAY, "Acknowledge UCS Chassis successful")
        return obj

    def addBlockIPAddForKVMAccess(self, inputdict, logfile):
        obj = result()
        loginfo("Add Block of IP Addresses for KVM Access")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "KVM Console IP Range: " + inputdict['kvm_console_ip'] + "\nSubnet mask" + inputdict[
            'mask'] + \
            "\nGateway" + inputdict['gateway'] + "\nPrimary DNS" + \
            inputdict['pri_dns'] + "\nSecondary DNS" + \
            inputdict['sec_dns']
        loginfo(
            "Add Block of IP Addresses for KVM Access parameters = " +
            message)
        customlogs("Add Block of IP Addresses for KVM Access started", logfile)
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
            "\nAdd Block of IP Addresses for KVM Access successful\n",
            logfile)
        dicts['name'] = "org-root/ip-pool-ext-mgmt/block-" + \
                        kvm_ip_from + "-" + kvm_ip_to
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Add block of IP Addresses for KVM Access successful")
        return obj

    def ucsDeleteKVMIPAddresses(self, inputs, outputs, logfile):
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
        obj = result()
        loginfo("UCS Anonymous reporting")
        dicts = {}
        if self.handle == None or self.handle_status != True:
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
        customlogs("UCS Anonymous reporting started\n", logfile)
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
            'rack_action'] + "\nScrub Policy: " + inputdict['scrub'] + "\nRack Management Connection Policy" + \
            inputdict['mgmt_action'] + "\nPower Policy" + inputdict['redundancy'] + "\nMAC Address Table Aging" + \
            inputdict['mac_aging'] + "\nGlobal Power Allocation Policy" + inputdict['style'] + \
            "\nFirmware Auto Sync Server Policy" + \
            inputdict['sync_state'] + "\nGlobal Power Profiling Policy" + \
            inputdict['profiling'] + "\nInfo Policy" + \
            inputdict['info_enable']
        loginfo("Chassis discovery policy parameters = " + message)
        customlogs("Chassis discovery policy started", logfile)

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
        customlogs("Chassis discovery policy updated successfully", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Chassis discovery policy updated successfully")
        return obj

    def ucsConfigureUnifiedPorts(self, inputdict, logfile):
        obj = result()
        loginfo("Configure_Unified_ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Switch ID =" + inputdict['fabric_id'])
        loginfo("No of Ports to be configured =" + inputdict['no_of_ports'])

        message = "Switch ID: " + \
                  inputdict['fabric_id'] + \
                  "\nNo of Ports to be configured:" + inputdict['no_of_ports']

        customlogs("Configuring Unified Ports....\n", logfile)
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

        customlogs("\nConfiguring Unified Ports successful\n", logfile)
        dicts['no_of_ports'] = inputdict['no_of_ports']
        dicts['fabric_id'] = inputdict['ucs_fabric_id']
        obj.setResult(dicts, PTK_OKAY, "Configuring Unified ports successful")

        loginfo("waiting for fabric to reboot after unified ports configuration")
        ucs_mac_id = inputdict['fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for Fabric " + ipaddr +
                   " to reboot after unified ports configuration", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of UCS " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)

        return obj

    def ucsUnConfigureUnifiedPorts(self, inputdict, logfile):
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

        customlogs("\nUnConfiguring Unified Ports successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "UnConfiguring Unified ports successful")
        loginfo("waiting for fabric to reboot after unified ports configuration")
        ucs_mac_id = inputdict['fabric_id']
        cred = get_device_credentials(key="mac", value=ucs_mac_id)
        fabric_ip = cred['vipaddress']
        ipaddr = cred['ipaddress']
        customlogs("Waiting for Fabric " + ipaddr +
                   " to reboot after unified ports configuration", logfile)

        ucsm = UCSManager()
        ucs_status = ucsm.is_ucsm_up(ipaddr)
        if ucs_status == "ucs down":
            loginfo("Verifying the reachability of UCS " + ipaddr)
            ucsm.verify_ucsm_accessible(ipaddr)
            ucsm.verify_ucsm_accessible(fabric_ip)

        return obj

    def ucsCreateApplicationvNICTemplate(self, inputdict, logfile):
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
            'application_vnic_templ_desc'] + "\nFabric ID:" + inputdict[
            'fabric_id'] + "\nRedundancy Pair Type:" + inputdict[
            'redundancy_pair_type'] + "\nTemplate Type:" + \
            inputdict['templ_type'] + "\nCDN SDource:" + inputdict['cdn_source'] + "\nIdent Pool Name:" + \
            inputdict['ident_pool_name'] + "\nNetwork Control Policy:" + \
            inputdict['nw_ctrl_policy_name'] + "\nStats Threshold Policy:" + \
            "" + "\nMTU:" + inputdict['mtu']

        customlogs("Create Application vNIC Template....", logfile)
        customlogs(message, logfile)

        mo = VnicLanConnTempl(
            parent_mo_or_dn="org-root",
            redundancy_pair_type=inputdict['redundancy_pair_type'],
            name=inputdict['application_vnic_templ_name'],
            descr=inputdict['application_vnic_templ_desc'],
            stats_policy_name="",  # inputdict['stats_policy_name'],
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

        customlogs("Application vNIC creation successful", logfile)
        dicts['application_vnic_templ_name'] = inputdict['application_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "Application vNIC creation successful")
        return obj

    def ucsDeleteApplicationvNICTemplate(self, inputs, outputs, logfile):
        obj = result()
        loginfo("Delete Application vNIC template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn(
            "org-root/lan-conn-templ-" + inputs['application_vnic_templ_name'])
        if mo is None:
            customlogs("\nApplication vNIC template " + inputs['application_vnic_templ_name'] + " does not exist\n",
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
        customlogs("\n Application vNIC template " + inputs['application_vnic_templ_name'] + " deleted successfully\n",
                   logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Application vNIC template deleted successfully")
        return obj

    def ucsCreateFCPortChannels(self, inputdict, logfile):
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
            inputdict['port_id'] + "\nVSAN Name:" + \
            inputdict['vsan_name']
        customlogs("Create FC Port Channels....\n", logfile)
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

        self.handle.logout()
        customlogs("\nCreated FC Port Channel successfully\n", logfile)
        dicts['fc_port_channel_name'] = parent_mo + \
            "/" + inputdict['fc_port_channel_name']
        obj.setResult(dicts, PTK_OKAY, "Created FC Port Channel successfully")
        return obj

    def ucsDeleteFCPortChannels(self, inputdict, logfile):
        obj = result()
        loginfo("Deleting_FC_Port_Channel")
        customlogs("UCS rollback FC Port Channel", logfile)
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
                fill_pattern="arbff",
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
        obj = result()
        loginfo("Create Host Firmware Package")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Host firmware package = " + inputdict['name'])
        loginfo("Blade Package = " + inputdict['blade_pkg'])
        loginfo("Excluded components = " + inputdict['excluded_comp'])
        message = "Blade Package: " + inputdict['blade_pkg']
        loginfo("Create Host Firmware Package started")
        customlogs("Create host firmware package started", logfile)
        customlogs(message, logfile)

        if inputdict['blade_pkg'] == "not-set":
            inputdict['blade_pkg'] = ""
        if inputdict['rack_pkg'] == "not-set":
            inputdict['rack_pkg'] = ""

	if inputdict['blade_pkg']:
	    image = "ucs-k9-bundle-b-series." + inputdict['blade_pkg'].replace('(','.').replace(')','.') + ".bin"
	    if not is_image_available_on_ucsm(self.handle, image):
		customlogs("Blade image is not present in UCS. Uploading blade image to UCS", logfile)
		if not upload_image_to_ucs([image], self.handle, "/mnt/system/uploads"):
		    customlogs("Failed to upload blade image to UCS", logfile)
		    self.handle.logout()
		    obj.setResult(dicts, PTK_INTERNALERROR,"Failed to update host firmware package")
		    return obj
	        customlogs("Blade image upload done", logfile)
	    else:
	        customlogs("Blade image is present in UCS", logfile)

	    customlogs("Waiting for blades to complete discovery", logfile)
            blades_list = self.handle.query_classid("computeBlade")
            for blade in blades_list:
                self.verify_blade_discovery(self.handle, blade, logfile)
	    time.sleep(60)

        mo = FirmwareComputeHostPack(parent_mo_or_dn="org-root", ignore_comp_check="yes", name=inputdict['name'],
                                     descr=inputdict['desc'], stage_size="0", rack_bundle_version=inputdict[
            'rack_pkg'], update_trigger="immediate", policy_owner="local", mode="staged",
            blade_bundle_version=inputdict['blade_pkg'], override_default_exclusion="yes")
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
	#Waiting for blades to complete upgrade
	time.sleep(600)
        customlogs("\nHost Firmware Package Created Successfully\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Host Firmware Package Created Successfully")
        return obj

    def ucsResetHostFirmwarePackage(self, inputs, outputs, logfile):
        dicts = {}
        obj = result()
        loginfo("Resetting Host Firmware Blade and Rack package ")
        customlogs("Resetting Host Firmware Blade and Rack package", logfile)
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = FirmwareComputeHostPack(parent_mo_or_dn="org-root", ignore_comp_check="yes", name=inputs['name'],
                                     descr=inputs['desc'], stage_size="0", rack_bundle_version='',
                                     update_trigger="immediate", policy_owner="local", mode="staged",
                                     blade_bundle_version='', override_default_exclusion="yes")

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
            "Reset host firmware blade and rack package successfully", logfile)
        obj.setResult(
            None, PTK_OKAY, "Reset host firmware blade and rack package successfully")
        return obj

    def ucsCreateLANConnectivityPolicy(self, inputdict, logfile):
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
                  "\n LAN Connectivity policy Description" + \
                  inputdict['lan_conn_policy_desc']
        customlogs("Create LAN Connectivity Policy....", logfile)
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

        customlogs("LAN Connectivity policy creation successful", logfile)
        dicts['lan_conn_policy_name'] = "org-root/lan-conn-pol-" + \
                                        inputdict['lan_conn_policy_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "LAN connectivity policy creation successful")
        return obj

    def ucsDeleteLANConnectivityPolicy(self, inputs, outputs, logfile):
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
        obj = result()
        loginfo("Create vNIC")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Create vNIC parameters = ")
        customlogs("Create vNIC ", logfile)
        loginfo(inputdict)
        message = "Name: " + inputdict['vnic_name'] + "\npolicyname" + inputdict['policy_name'] + "\nvNIC Template" + \
                  inputdict['nw_templ_name'] + "\nAdapter policy" + \
                  inputdict['adaptor_policy_name']
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
        customlogs("vNIC creation successful", logfile)
        dicts['vnic_name'] = inputdict['vnic_name']
        obj.setResult(dicts, PTK_OKAY, "vNIC creation successful")
        return obj

    def ucsDeleteiSCSIvNIC(self, inputdict, logfile):
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

        customlogs("Delete iSCSI vNIC  successful", logfile)
        obj.setResult(dicts, PTK_OKAY, "Delete iSCSI vNIC successful")
        return obj

    def ucsCreateiSCSIvNIC(self, inputdict, logfile):
        obj = result()
        loginfo("Create iSCSI vNIC")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Create iSCSI vNIC parameters = ")
        customlogs("Create vNIC ", logfile)
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
        customlogs("vNIC creation successful", logfile)
        dicts['vnic_name'] = policy_name + "/ether-" + inputdict['vnic_name']
        obj.setResult(dicts, PTK_OKAY, "iSCSI vNIC creation successful")
        return obj

    def ucsDeletevNIC(self, inputs, outputs, logfile):
        obj = result()
        dicts = {}
        loginfo("Deleting vNIC " + inputs['vnic_name'])
        customlogs("Deleting vNIC " + inputs['vnic_name'], logfile)
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
                   " deleted successfully", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY, "vNIC deleted successfully")
        return obj

    def ucsCreateLocalDiskConfigurationPolicy(
            self, inputdict, logfile):
        obj = result()
        loginfo("Create Local Disk Configuration Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nMode: " + inputdict['mode'] + "\nFlexFlash: " + \
                  inputdict['flash_state'] + \
                  "\nFlexFlash RAID Reporting state: " + \
            inputdict['raid_state']
        loginfo("Create Local Disk Configuration Policy parameters = " + message)
        customlogs("Create Local Disk Configuration Policy started", logfile)
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
                  inputdict['mac_order'] + " MAC Address size: " + inputdict['size'] + \
                  "MAC Start Address " + inputdict['mac_start']
        customlogs("Create MAC Address Pools started", logfile)
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
        customlogs("MAC Address pool" +
                   outputs['mac_name'] + " deleted successfully", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "MAC Address Pool" +
            outputs['mac_name'] +
            " deleted successfully")
        return obj

    def ucsCreateMgmtvNiCTemplate(self, inputdict, logfile):
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
                  inputdict['mgmt_vnic_templ_desc'] + "\nFabric ID:" + inputdict[
                      'fabric_id'] + "\nRedundancy Pair Type:" + inputdict['redundancy_pair_type'] + \
                  "\nTemplate Type:" + inputdict['templ_type'] + "\nCDN SDource:" + inputdict[
                      'cdn_source'] + "\nIdent Pool Name:" + inputdict['ident_pool_name'] + \
                  "\nNetwork Control Policy:" + \
                  inputdict['nw_ctrl_policy_name'] + "\nMTU:" + \
                  inputdict['mtu'] + "\nDefault Native LAN:"

        customlogs("Create Management vNIC Template....", logfile)
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
        customlogs("Management vNIC creation successful", logfile)
        dicts['mgmt_vnic_templ_name'] = inputdict['mgmt_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "Management vNIC creation successfull")
        return obj

    def ucsDeleteMgmtvNiCTemplate(self, inputs, outputs, logfile):
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
                  inputdict['iSCSI_vnic_templ_desc'] + "\nFabric ID:" + inputdict[
                      'fabric_id'] + "\nRedundancy Pair Type:" + inputdict['redundancy_pair_type'] + \
                  "\nTemplate Type:" + inputdict['templ_type'] + "\nIdent Pool Name:" + inputdict['ident_pool_name'] + \
                  "\nNetwork Control Policy:" + \
                  inputdict['nw_ctrl_policy_name'] + "\nMTU:" + \
                  inputdict['mtu']

        customlogs("Create iSCSI vNIC Template....", logfile)
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
        customlogs("iSCSI vNIC creation successful", logfile)
        dicts['iSCSI_vnic_templ_name'] = inputdict['iSCSI_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "iSCSI vNIC creation successfull")
        return obj

    def ucsCreatePowerControlPolicy(self, inputdict, logfile):
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
        customlogs("Create Power Control Policy started", logfile)
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
                   inputs['name'] + " deleted successfully", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Power control policy deleted successfully")
        return obj

    def ucsCreateSANConnectivityPolicy(self, inputdict, logfile):
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
            'san_conn_policy_name'] + "\n SAN Connectivity policy Description:" + \
            inputdict['san_conn_policy_desc'] + \
            "\nIdent Pool Name:" + inputdict['ident_pool_name']

        customlogs("create SAN Connectivity Policy....\n", logfile)
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
        customlogs("\nSAN Connectivity policy creation successful\n", logfile)
        dicts['san_conn_policy_name'] = inputdict['san_conn_policy_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "SAN Connectivity policy creation successful")
        return obj

    def ucsDeleteSANConnectivityPolicy(self, inputdict, logfile):
        obj = result()
        loginfo("delete_SAN_connectivity_policy")
        customlogs("Rollback UCS SAN connectivity policy", logfile)
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
        customlogs("\nSAN Connectivity policy" +
                   inputdict['san_conn_policy_name'] + " deletion successful\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "SAN Connectivity policy deletion successful")
        return obj

    def ucsCreateServerBIOSPolicy(self, inputdict, logfile):
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
        customlogs("Create Server BIOS Policy \n", logfile)
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
        BiosVfIntelVTForDirectedIO(parent_mo_or_dn=mo, vp_intel_vtd_pass_through_dma_support="platform-default",
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
            "\nServer BIOS Policy Created Successfully \n",
            logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server BIOS Policy Created Successfully ")
        return obj

    def ucsDeleteServerBIOSPolicy(self, inputs, outputs, logfile):
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
        obj = result()
        loginfo("Create Server Pool")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + \
                  "\nSelected servers: " + inputdict['servers']
        customlogs("Create Server Pool started\n", logfile)
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
                # o_1 = ComputePooledSlot(parent_mo_or_dn=mo, slot_id="1",
                # chassis_id="3")
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
        customlogs(
            "\nServer Pool Qualification Policy Creation Started",
            logfile)
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

        customlogs("\nService profile creation successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Service profile creation successful")
        return obj

    def ucsServerReset(self, inputdict, logfile):
        obj = result()
        dicts = {}
        loginfo("Resetting the Blade server")
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
                mo_1 = LsPower(parent_mo_or_dn=mo,
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

        customlogs("\nReset server successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Reset server successful")
        return obj

    def wait_assoc_completion(self, handle, sp_dn, server_dn, logfile):
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
            loginfo('Server %s fsmStatus: %s, elapsed=%ds' % (server_dn,
                                                              phys_mo.fsm_status,
                                                              (datetime.datetime.now() - start).total_seconds()))
            # Query again to update association state
            phys_mo = handle.query_dn(server_dn)

        if phys_mo.association == 'associated':
            loginfo('Server %s has completed association' % (
                server_dn))
            customlogs('Server %s has completed association' % (
                server_dn), logfile)

    def verify_blade_discovery(self, handle, blade, logfile):
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
            loginfo('Server %s fsmStatus: %s, elapsed=%ds' % (blade.dn,
                                                              blade.fsm_status,
                                                              (datetime.datetime.now() - start).total_seconds()))
            # Query again to update discovery state
            mo = handle.query_dn(blade.dn)
        if mo.discovery == 'complete':
            loginfo('Server %s has completed discovery' % (blade.dn))
            customlogs('Server %s has completed discovery' %
                       (blade.dn), logfile)

    def ucsCreateServiceProfilesFromTemplate(self, inputdict, logfile):
        obj = result()
        loginfo("create_service_profile_from_template")
        instances = int(inputdict['instances'])
        count = int(inputdict['suffix_starting_number'])
        loginfo("Service profile instances =" + inputdict['instances'])
        loginfo("Suffix start =" + inputdict['suffix_starting_number'])
        customlogs("Create service profile started....\n", logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        dn_set = DnSet()
        cnt = 0
        for suffix in range(0, instances):
            dn = Dn()
            cnt += count
            dn.attr_set("value", inputdict['profile_prefix'] + str(cnt))
            dn_set.child_add(dn)
        elem = ls_instantiate_n_named_template(cookie=self.handle.cookie, dn="org-root/ls-" +
                                                                             inputdict['template_name'],
                                               in_error_on_existing="true", in_name_set=dn_set,
                                               in_target_org="org-root", in_hierarchical="false")
        self.handle.process_xml_elem(elem)
        customlogs(
            "\nWaiting for Service profile association to be completed\n", logfile)
        time.sleep(60)

        blades_list = self.handle.query_classid("computeBlade")
        for blade in blades_list:
            self.verify_blade_discovery(self.handle, blade, logfile)

        # Waiting because it takes sometime for service profile to get associated with the server once it is up
        time.sleep(120)

        service_profiles = self.handle.query_classid("lsServer")
        for sp in service_profiles:
            if sp.type != "updating-template" and sp.dn != '' and sp.pn_dn != '':
                self.wait_assoc_completion(
                    self.handle, sp.dn, sp.pn_dn, logfile)
        # Waiting for sh flogi database entries to be displayed during MDS Zoning
        time.sleep(230)
        customlogs("\nService profile creation successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY, "Service profiles creation successful")
        return obj

    def ucsCloneServiceProfileTemplate(self, inputdict, logfile):
        obj = result()
        loginfo("clone_service_profile_template")
        customlogs(
            "Create vMedia service profile template started....\n", logfile)

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

        mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name=inputdict['vmedia_policy_name'],
                      ext_ip_state="none", bios_profile_name=inputdict['biospolicy'], mgmt_fw_policy_name="",
                      agent_policy_name="", mgmt_access_policy_name="", dynamic_con_policy_name="",
                      kvm_mgmt_policy_name="", sol_policy_name="", uuid="0", descr="", stats_policy_name="default",
                      policy_owner="local",
                      ext_ip_pool_name="ext-mgmt", boot_policy_name=inputdict['boot_policy_name'], usr_lbl="",
                      host_fw_policy_name="", vcon_profile_name="", ident_pool_name=inputdict['ident_pool_name'],
                      src_templ_name="", local_disk_policy_name=inputdict['local_disk_policy_name'],
                      scrub_policy_name="", power_policy_name=inputdict['power_policy_name'],
                      maint_policy_name="default",
                      name=inputdict['vmedia_template'], power_sync_policy_name="", resolve_remote="yes")

        self.handle.add_mo(mo, True)
        self.handle.commit()
        dicts['vmedia_template'] = inputdict['vmedia_template']
        customlogs(
            "\nCreating vMedia Service profile template successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "vMedia Service profile template created successfully")
        return obj

    def ucsCreateServiceProfileTemplate(self, inputdict, logfile):
        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        loginfo("template_description =" + inputdict['template_desc'])
        message = "Template name: " + \
                  inputdict['template_name'] + \
                  "\nTemplate_description: " + inputdict['template_desc']
        customlogs("Create service profile template started....\n", logfile)
        customlogs(message, logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}

        mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name="", descr=inputdict['template_desc'],
                      stats_policy_name="default", policy_owner="local",
                      ext_ip_pool_name="ext-mgmt", boot_policy_name=inputdict['boot_policy_name'],
                      ident_pool_name=inputdict['ident_pool_name'], type=inputdict['type'],
                      local_disk_policy_name=inputdict['local_disk_policy_name'],
                      power_policy_name=inputdict['power_policy_name'],
                      name=inputdict['template_name'], resolve_remote="yes",
                      maint_policy_name=inputdict['maint_policy_name'], bios_profile_name=inputdict['biospolicy'])
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
                VnicEther(parent_mo_or_dn=mo, cdn_prop_in_sync="yes", nw_ctrl_policy_name="", admin_host_port="ANY",
                          admin_vcon="any", stats_policy_name="default", admin_cdn_name="", switch_id="A",
                          pin_to_group_name="", name=vnic_name, order=str(order), qos_policy_name="",
                          adaptor_profile_name="", ident_pool_name="", cdn_source="vnic-name", mtu="1500",
                          nw_templ_name="", addr="derived")
        san_dn = "san-conn-pol-" + inputdict['san_conn_policy_name']
        fc_list = self.handle.query_classid("vnicFc")
        for fc in fc_list:
            if fc.dn.split("/")[1] == san_dn:
                order += 1
                vnic_name = fc.name
                LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", admin_host_port="ANY",
                             order=str(order), transport="fc", vnic_name=vnic_name)
                VnicFc(parent_mo_or_dn=mo, cdn_prop_in_sync="yes", addr="derived", admin_host_port="ANY",
                       admin_vcon="any", stats_policy_name="default", admin_cdn_name="", switch_id="A",
                       pin_to_group_name="", pers_bind="disabled", order=str(order), pers_bind_clear="no",
                       qos_policy_name="", adaptor_profile_name="", ident_pool_name="", cdn_source="vnic-name",
                       max_data_field_size="2048", nw_templ_name="", name=vnic_name)

        VnicFcNode(parent_mo_or_dn=mo,
                   ident_pool_name="node-default", addr="pool-derived")
        # mo_15 = LsRequirement(parent_mo_or_dn=mo, restrict_migration="no", name=inputdict['pool_assignment'], qualifier=inputdict['qualifier'])
        LsRequirement(parent_mo_or_dn=mo, restrict_migration="no",
                      name=inputdict['pool_assignment'], qualifier="")
        LsPower(parent_mo_or_dn=mo, state="admin-up")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all",
                   transport="ethernet,fc", id="1", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all",
                   transport="ethernet,fc", id="2", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all",
                   transport="ethernet,fc", id="3", inst_type="auto")
        FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE", share="shared", select="all",
                   transport="ethernet,fc", id="4", inst_type="auto")

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
        customlogs("\nService profile template creation successful\n", logfile)
        dicts['serviceprofilename'] = inputdict['template_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profile template creation successful")
        return obj

    def ucsCreateServiceProfileTemplateForiSCSI(self, inputdict, logfile):
        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        loginfo("template_description =" + inputdict['template_desc'])
        message = "Template name: " + \
                  inputdict['template_name'] + \
                  "\nTemplate_description: " + inputdict['template_desc']
        customlogs(
            "Create service profile template for iSCSI started....\n", logfile)
        customlogs(message, logfile)

        if self.handle == None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name="", ext_ip_state="none",
                      bios_profile_name=inputdict["biospolicy"], mgmt_fw_policy_name="", agent_policy_name="",
                      mgmt_access_policy_name="", dynamic_con_policy_name="", kvm_mgmt_policy_name="",
                      sol_policy_name="", uuid="0", descr="", stats_policy_name="default", policy_owner="local",
                      ext_ip_pool_name="ext-mgmt", boot_policy_name=inputdict[
                          "boot_policy_name"], usr_lbl="", host_fw_policy_name="", vcon_profile_name="",
                      ident_pool_name=inputdict["ident_pool_name"], src_templ_name="", type=inputdict["type"],
                      local_disk_policy_name=inputdict["local_disk_policy_name"], scrub_policy_name="",
                      power_policy_name=inputdict['power_policy_name'], maint_policy_name="default",
                      name=inputdict['template_name'], power_sync_policy_name="", resolve_remote="yes")

        vnic_list = self.handle.query_classid("vnicEther")
        lan_dn = "lan-conn-pol-" + inputdict['lan_conn_policy_name']
        order = 0
        for vnic in vnic_list:
            if vnic.dn.split("/")[1] == lan_dn:
                order += 1
                vnic_name = vnic.name
                LsVConAssign(parent_mo_or_dn=mo, admin_vcon="any", admin_host_port="ANY",
                             order=str(order), transport="ethernet", vnic_name=vnic_name)
                VnicEther(parent_mo_or_dn=mo, cdn_prop_in_sync="yes", nw_ctrl_policy_name="", admin_host_port="ANY",
                          admin_vcon="any", stats_policy_name="default", admin_cdn_name="", switch_id="A",
                          pin_to_group_name="", name=vnic_name, order=str(order), qos_policy_name="",
                          adaptor_profile_name="", ident_pool_name="", cdn_source="vnic-name", mtu="1500",
                          nw_templ_name="", addr="derived")

        mo_9 = VnicConnDef(parent_mo_or_dn=mo, san_conn_policy_name="",
                           lan_conn_policy_name=inputdict['lan_conn_policy_name'])

        mo_10 = VnicDefBeh(parent_mo_or_dn=mo, name="", descr="",
                           policy_owner="local", action="none", type="vhba", nw_templ_name="")
        VnicFcNode(parent_mo_or_dn=mo,
                   ident_pool_name="node-default", addr="pool-derived")
        mo_21 = VnicIScsi(parent_mo_or_dn=mo, cdn_prop_in_sync="yes", addr="derived", iqn_ident_pool_name="",
                          admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", admin_cdn_name="",
                          adaptor_profile_name="", switch_id="A",
                          pin_to_group_name="", vnic_name="", ext_ip_state="none", qos_policy_name="",
                          auth_profile_name="", ident_pool_name="", cdn_source="vnic-name", order="unspecified",
                          name=inputdict['iSCSI_vNIC_A'], nw_templ_name="", initiator_name="")
        mo_21_1 = VnicVlan(parent_mo_or_dn=mo_21, name="", vlan_name="default")
        mo_22 = VnicIScsi(parent_mo_or_dn=mo, cdn_prop_in_sync="yes", addr="derived", iqn_ident_pool_name="",
                          admin_host_port="ANY", admin_vcon="any", stats_policy_name="default", admin_cdn_name="",
                          adaptor_profile_name="", switch_id="A",
                          pin_to_group_name="", vnic_name="", ext_ip_state="none", qos_policy_name="",
                          auth_profile_name="", ident_pool_name="", cdn_source="vnic-name", order="unspecified",
                          name=inputdict['iSCSI_vNIC_B'], nw_templ_name="", initiator_name="")
        mo_22_1 = VnicVlan(parent_mo_or_dn=mo_22, name="", vlan_name="default")
        mo_23 = VnicIScsiNode(parent_mo_or_dn=mo, initiator_policy_name="",
                              iqn_ident_pool_name=inputdict['iqn_ident_pool_name'], initiator_name="")
        mo_24 = LsPower(parent_mo_or_dn=mo, state="admin-up")
        mo_25 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                           share="shared", select="all", transport="ethernet,fc", id="1", inst_type="auto")
        mo_26 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                           share="shared", select="all", transport="ethernet,fc", id="2", inst_type="auto")
        mo_27 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
                           share="shared", select="all", transport="ethernet,fc", id="3", inst_type="auto")
        mo_28 = FabricVCon(parent_mo_or_dn=mo, placement="physical", fabric="NONE",
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
        customlogs("\nService profile template creation successful\n", logfile)
        dicts['serviceprofilename'] = inputdict['template_name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profile template creation successful")
        return obj

    def ucsSetiSCSIBootParameters(self, inputdict, logfile):
        obj = result()
        loginfo("template_name =" + inputdict['template_name'])
        message = "Template name: " + \
                  inputdict['template_name']
        customlogs(
            "Set iSCSI Boot parameters for iSCSI vNIC started....\n", logfile)
        customlogs(message, logfile)

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        dicts = {}
        if inputdict['iSCSI_Boot'] == "A":
            mo = VnicIScsiBootParams(
                parent_mo_or_dn="org-root/ls-" + inputdict['template_name'], policy_owner="local", descr="")
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
                "\nSet iSCSI Boot parameters for iSCSI vNIC started failed\n", logfile)
            loginfo("\nSet iSCSI Boot parameters for iSCSI vNIC started failed\n")
            obj.setResult(
                dicts,
                PTK_INTERNALERROR,
                "Set iSCSI Boot parameters for iSCSI vNIC started failed")
            return obj
        self.handle.logout()
        customlogs(
            "\nSet iSCSI Boot parameters for iSCSI vNIC started successful\n", logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Set iSCSI Boot parameters for iSCSI vNIC started successful")
        return obj

    def ucsDeleteiSCSIBootParams(self, inputs, outputs, logfile):
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

            mo_1 = VnicIScsiBootVnic(parent_mo_or_dn=mo, initiator_name="", iqn_ident_pool_name="",
                                     auth_profile_name="", policy_owner="local", descr="", name=inputs['iSCSI_vNIC_name'])
            for instance in range(1, 3):
                mo_1_1 = self.handle.query_dn(
                    "org-root/ls-" + inputs['template_name'] + "/" + "iscsi-boot-params/boot-vnic-" + inputs['iSCSI_vNIC_name']+"/"+str(instance))
                self.handle.remove_mo(mo_1_1)

            mo_1_1 = VnicIPv4If(parent_mo_or_dn=mo_1, name="")
            mo_1_1_2 = VnicIPv4PooledIscsiAddr(
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
        obj = result()
        loginfo("Create Uplink Port Channels")
        dicts = {}

        if self.handle == None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(inputdict)
        message = "Name: " + inputdict['name'] + "\nID: " + \
                  inputdict['id'] + "\nSelected ports: " + inputdict['ports']
        customlogs("Create Uplink Port Channels started\n", logfile)
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

        customlogs("Uplink Port Channels Created Successfully", logfile)
        dicts['name'] = inputdict['name']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Uplink Port Channels Created Successfully")
        return obj

    def ucsDeleteUplinkPortChannel(self, inputs, outputs, logfile):
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
        customlogs("Uplink Port Channel " +
                   inputs['name'] + " deleted successfully", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY,
                      "Uplink Port Channel deleted successfully")
        return obj

    def ucsCreateUUIDSuffixPool(self, inputdict, logfile):
        obj = result()
        loginfo("Create UUID Suffix Pool")
        dicts = {}

        if self.handle == None or self.handle_status != True:
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
                  inputdict['order'] + "\nUUID From" + \
                  inputdict['uuid_from'] + "\nSize" + inputdict['size']
        customlogs("Create UUID Suffix Pool", logfile)
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
        customlogs("UUID Suffix pool " +
                   inputs['name'] + " deleted successfully", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "UUID Suffix pool deleted successfully")
        return obj

    def ucsCreatevHBA(self, inputdict, logfile):
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
                  inputdict['vhba_template'] + "\nvSAN Name:" + \
                  inputdict['vsan_con_policy']

        customlogs("Create vHBA Template....\n", logfile)
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

        customlogs("\nvHBA Template creation successful\n", logfile)
        dicts['vhba_name'] = inputdict['vhba_name']
        objs.setResult(dicts, PTK_OKAY, "vHBA creation successful")
        return objs

    def ucsCreatevHBATemplate(self, inputdict, logfile):
        obj = result()
        loginfo("create_vHBA")
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
            'vhba_description'] + "\nIndent Pool Name:" + inputdict['ident_pool_name'] + \
            "\nSwitch ID:" + inputdict['ucs_fabric_id'] + "\nMax data field size: " + \
            inputdict['max_data_field_size'] + \
            "\nVSAN Name:" + inputdict['vsan_name']

        customlogs("Create vHBA Template....\n", logfile)
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

        customlogs("\nvHBA Template creation successful\n", logfile)
        dicts['vhba_name'] = inputdict['vhba_name']
        obj.setResult(dicts, PTK_OKAY, "vHBA Template creation successful")
        return obj

    def ucsDeleteServiceProfilesFromTemplate(self, inputdict, logfile):
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
        customlogs("\nAll Service profiles with prefix " + inputdict['profile_prefix'] + " deleted successfully\n",
                   logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Service profiles deletion successful")
        return obj

    def ucsDeleteServerPool(self, inputdict, logfile):
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
        obj = result()
        customlogs("Delete service profile template started....\n", logfile)

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
        customlogs("\n vMedia Service profile template " + inputdict['vmedia_template'] + " deleted successfully\n",
                   logfile)
        obj.setResult(
            dicts,
            PTK_OKAY,
            "vMedia Service profile template deletion successful")
        return obj

    def ucsDeletevHBATemplate(self, inputdict, logfile):
        obj = result()
        loginfo("delete_vHBA")
        customlogs("UCS rollback vHBA template", logfile)
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
        obj = result()
        loginfo("UCS Delete_vHBA")
        customlogs("Rollback UCS vHBA", logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        mo = self.handle.query_dn(
            "org-root/san-conn-pol-" + inputdict['vsan_con_policy'] + "/fc-" + inputdict['vhba_name'])

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

        message = "VLAN Name: " + inputdict['vlan_name'] + "\nVLAN ID:" + inputdict['vlan_id'] + \
                  "\nSharing:" + inputdict['sharing']

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

        customlogs("VLAN creation successful", logfile)
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
        obj = result()
        loginfo("UCS Delete VLAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")

        mo = self.handle.query_dn("fabric/lan/net-" + inputs['vlan_name'])
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
        customlogs("Create vMedia Policy started\n", logfile)
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
        obj = result()
        loginfo("create_vMotion_vNIC_Template")
        dicts = {}

        if self.handle == None or self.handle_status != True:
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
            'vmotion_vnic_templ_desc'] + "\nFabric ID:" + inputdict['fabric_id'] + "\nRedundancy Pair Type:" + \
            inputdict['redundancy_pair_type'] + \
            "\nTemplate Type:" + inputdict['templ_type'] + "\nCDN SDource:" + inputdict[
            'cdn_source'] + "\nIdent Pool Name:" + inputdict['ident_pool_name'] + \
            "\nNetwork Control Policy:" + \
            inputdict['nw_ctrl_policy_name'] + "\nMTU:" + \
            inputdict['mtu'] + "\nDefault Native LAN:"

        customlogs("Create vMotion vNIC Template....", logfile)
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

        customlogs("vMotion vNIC creation successful", logfile)
        dicts['vmotion_vnic_templ_name'] = inputdict['vmotion_vnic_templ_name']
        obj.setResult(dicts, PTK_OKAY, "vMotion vNIC creation successful")
        return obj

    def ucsDeletevMotionvNICTemplate(self, inputs, outputs, logfile):
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
        obj = result()
        loginfo("Create vNIC/vHBA Placement Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name" + inputdict['name'] + "\nVirtual slot mapping scheme" + inputdict['scheme'] + \
                  "\nVirtual Slot" + \
                  inputdict['port_id'] + "\nSelection preference" + \
                  inputdict['preference']
        loginfo("Create vNIC/vHBA Placement Policy parameters = " + message)
        customlogs("Create vNIC/vHBA Placement Policy", logfile)
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
        obj = result()
        loginfo("Deleting vNIC vHBA Placement policy" + outputs['name'])
        customlogs("Deleting vNIC vHBA placement policy" +
                   outputs['name'], logfile)

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
        obj.setResult(None, PTK_OKAY,
                      "vNIC/vHBA placement policy deleted successfully")
        return obj

    def ucsDeleteVSANs(self, inputdict, logfile):
        obj = result()
        loginfo("delete_VSAN")
        customlogs("UCS rollback VSAN", logfile)
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
        obj = result()
        loginfo("Create_VSAN")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo(inputdict)
        loginfo("VSAN Name =" + inputdict['vsan_name'])
        loginfo("Fabric ID =" + inputdict['fabric_id'])
        loginfo("VSAN ID =" + inputdict['vsan_id'])
        loginfo("FCoE VLAN ID =" + inputdict['fcoe_vlan'])

        message = "VSAN Name: " + inputdict['vsan_name'] + "\nFabric ID: " + inputdict['fabric_id'] + \
                  "\nVSAN Id: " + inputdict['vsan_id'] + \
                  "\nFCoE Id:" + inputdict['fcoe_vlan']

        customlogs("Create VSANs....\n", logfile)
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
        customlogs("\nVSAN creation successful\n", logfile)
        dicts['vsan'] = inputdict['vsan_name']
        dicts['vsan_name'] = fabric_id + \
            "/net-" + inputdict['vsan_name']
        obj.setResult(dicts, PTK_OKAY, "VSAN creation successful")
        return obj

    def ucsCreateWWNNPool(self, inputdict, logfile):
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
        customlogs("Create WWNN Pool started\n", logfile)
        customlogs(message, logfile)

        wwnn_start_addr = str(inputdict['from_ip'])
        wwnn_size = int(inputdict['size'])
        wwnn_int = int(wwnn_start_addr.translate(None, ":.- "), 16)
        wwnn_end_int = wwnn_int + (wwnn_size - 1)
        wwnn_hex = "{:012X}".format(wwnn_end_int)
        wwnn_end = ":".join(wwnn_hex[i:i + 2]
                            for i in range(0, len(wwnn_hex), 2))

        loginfo("WWNN End Block= " + wwnn_end)

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
        customlogs("Create WWPN Pool started\n", logfile)
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
        obj = result()
        loginfo("Enable Server Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        customlogs("Enable Server ports started", logfile)

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

        customlogs("\nServer Ports enabled successfully\n", logfile)
        if 'ports' in inputdict:
            dicts['ports'] = inputdict['ports']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Server Ports enabled successfully")
        return obj

    def ucsEnableUplinkPorts(self, inputdict, logfile):
        obj = result()
        loginfo("Enable Uplink Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        customlogs("Enable uplink ports started", logfile)

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
                self.handle.add_mo(mo)
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

        customlogs("\nUplink Ports enabled successfully\n", logfile)
        if 'ports' in inputdict:
            dicts['ports'] = inputdict['ports']
        obj.setResult(
            dicts,
            PTK_OKAY,
            "Uplink Ports enabled successfully")
        return obj

    def ucsDisableServerPorts(self, inputs, outputs, logfile):
        obj = result()
        loginfo("UCS Disable Server Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        customlogs("UCS Disable Server ports", logfile)

        ports_list = []
        if 'ports' in inputs:
            ports_list = inputs['ports'].split('|')
            for port in ports_list:
                parent_mo = "sys/switch-" + \
                    inputs['ucs_fabric_id']+"/slot-1/switch-ether/port-"+port
                mo = self.handle.query_dn(parent_mo)
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
        obj = result()
        loginfo("UCS Disable Uplink Ports")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        customlogs("UCS disable uplink ports", logfile)

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
        obj = result()
        loginfo("Set_Jumbo_Frames")
        dicts = {}
        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("MTU =" + inputdict['mtu'])

        message = "MTU: " + inputdict['mtu']

        customlogs("Setting Jumbo Frames....\n", logfile)
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
        customlogs("\nSetting jumbo frames successful\n", logfile)
        dicts['mtu'] = inputdict['mtu']
        obj.setResult(dicts, PTK_OKAY, "Setting jumbo frames successful")
        return obj

    def ucsResetJumboFrames(self, inputs, outputs, logfile):
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

            mo_1 = QosclassEthBE(
                parent_mo_or_dn=mo, multicast_optimize="no", name="", weight="5", mtu="normal")
            self.handle.set_mo(mo)
            self.handle.commit()

        except UcsException as e:
            customlogs(str(e), logfile)
            customlogs("Failed to reset Jumbo frames MTU", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to reset Jumbo frames MTU")
            return obj
        customlogs("Jumbo frames MTU reset successfully", logfile)
        self.handle.logout()
        obj.setResult(None, PTK_OKAY, "Jumbo frames mtu reset successfully")
        return obj

    def ucsSynchronizeUCStoNTP(self, inputdict, logfile):
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
        customlogs("Synchronize UCS to NTP started", logfile)
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
        customlogs("\nChanged the Time Zone successfully\n", logfile)

        # mo = CommNtpProvider(parent_mo_or_dn="sys/svc-ext/datetime-svc", name="10.132.242.53", descr="")
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
        customlogs("\nNTP server details updated\n", logfile)

        customlogs("\nSynchronize UCS to NTP successful\n", logfile)
        # dicts['zone'] = mo.timezone
        obj.setResult(dicts, PTK_OKAY, "Synchronize UCS to NTP successful")
        return obj

    def ucsRollbackSynchronizeUCStoNTP(self, inputs, outputs, logfile):
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
        obj = result()
        loginfo("Update Default Maintenance Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        loginfo("Update Default Maintenance Policy parameters")
        customlogs("Update Default Maintenance Policy started\n", logfile)

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
                      "\nOn next boot: " + \
                      inputdict['trigger'] + \
                "\nSchedule: " + inputdict['sched']
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
        obj = result()
        loginfo("Reset Default Maintenance Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
        mo = LsmaintMaintPolicy(parent_mo_or_dn="org-root", uptime_disr="immediate", name="default",
                                descr="Default maintenance policy", trigger_config="", soft_shutdown_timer="150-secs",
                                sched_name="", policy_owner="local")
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
        customlogs("Default Maintenance policy reset successfully", logfile)
        obj.setResult(
            None,
            PTK_OKAY,
            "Default maintenance policy resetted successfully")
        return obj

    def ucsCreateNetworkControlPolicy(self, inputdict, logfile):
        obj = result()
        loginfo("Create Network Control Policy")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "\nCDP: " + inputdict['cdp'] + "\nMAC Register mode: " + inputdict[
            'mac_mode'] + "Action on Uplink fail\n: " + \
            inputdict['uplink_fail'] + "\nForge: " + inputdict['forge'] + "LLDP Transmit\n: " + \
            inputdict['lldp_tra'] + "\nLLDP Receive: " + inputdict['lldp_rec']
        loginfo("Create Network Control Policy parameters = " + message)
        customlogs("Create Network Control Policy Started", logfile)
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

        obj.setResult(
            None,
            PTK_OKAY,
            "Network control policy deleted successfully")
        return obj

    def ucsCreateIQNPoolsForiSCSIBoot(self, inputdict, logfile):
        obj = result()
        loginfo("Create IQN Pools for iSCSI Boot")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['name'] + "Description: " + inputdict['desc'] + \
                  "Assignment order: " + inputdict['order'] + "Prefix: " + inputdict['prefix'] + "\nIQN Suffix: " + \
                  inputdict['suffix'] + "From: " + inputdict['suffix_from'] + \
                  "To: " + inputdict['suffix_to']
        loginfo("Create IQN Pools for iSCSI Boot parameters = " + message)
        customlogs("Create IQN Pools for iSCSI Boot started", logfile)
        customlogs(message, logfile)

        mo = IqnpoolPool(parent_mo_or_dn="org-root", policy_owner="local",
                         prefix=inputdict['prefix'], descr=inputdict['desc'], assignment_order=inputdict['order'],
                         name=inputdict['name'])
        IqnpoolBlock(
            parent_mo_or_dn=mo, to=inputdict['suffix_to'], r_from=inputdict['suffix_from'], suffix=inputdict['suffix'])
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
        obj = result()
        loginfo("Delete IP Pools for iSCSI Boot")
        dicts = {}

        if self.handle == None or self.handle_status != True:
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
        obj = result()
        loginfo("Create IP Pools for iSCSI Boot")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj

        message = "Name: " + inputdict['ip_pool_name'] + "Description: " + inputdict['desc'] + \
                  "Assignment order: " + inputdict['order'] + "From IP: " + inputdict['ip_from'] + "\nSize: " + \
                  inputdict['size']
        loginfo("Create IP Pools for iSCSI Boot parameters = " + message)
        customlogs("Create IP Pools for iSCSI Boot started", logfile)
        customlogs(message, logfile)

        ip_from = inputdict['ip_from']
        ip_addr_split = ip_from.split('.')
        ip_increment = int(ip_addr_split[3]) + int(inputdict['size']) - 1
        ip_addr_split[3] = str(ip_increment)
        to_ip_addr = '.'.join(ip_addr_split)

        mo = IppoolPool(parent_mo_or_dn="org-root", is_net_bios_enabled="disabled",
                        name=inputdict['ip_pool_name'], descr=inputdict['desc'], policy_owner="local",
                        ext_managed="internal", supports_dhcp="disabled", assignment_order=inputdict['order'])
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

        customlogs("\nIP Pools for iSCSI Boot Created Successfully\n", logfile)
        dicts['ip_pool_name'] = inputdict['ip_pool_name']

        obj.setResult(
            dicts,
            PTK_OKAY,
            "IP Pools for iSCSI Boot created successfully")
        return obj

    def ucsunbindfromthetemplate(self, inputdict, logfile):
        obj = result()
        loginfo("UCS unbind from the template")
        customlogs("Unbind service profile from template", logfile)
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name=inputdict['vmedia_policy_name'],
                      ext_ip_state="none", bios_profile_name=inputdict['bios_profile_name'],
                      mgmt_fw_policy_name="", agent_policy_name="", mgmt_access_policy_name="",
                      dynamic_con_policy_name="", kvm_mgmt_policy_name="", sol_policy_name="", uuid="", descr="",
                      stats_policy_name="default", policy_owner="local", ext_ip_pool_name="ext-mgmt",
                      boot_policy_name=inputdict['boot_policy_name'], usr_lbl="", host_fw_policy_name="",
                      vcon_profile_name="", ident_pool_name=inputdict['ident_pool_name'], src_templ_name="",
                      local_disk_policy_name=inputdict['local_disk_policy_name'],
                      scrub_policy_name="", power_policy_name=inputdict['power_policy_name'],
                      maint_policy_name="default", name=inputdict['service_profile_name'], power_sync_policy_name="",
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
        obj = result()
        loginfo("UCS bind to a  template")
        dicts = {}

        if self.handle is None or self.handle_status != True:
            obj.setResult(None, PTK_INTERNALERROR,
                          "Unable to connect to UCS")
            return obj
        mo = LsServer(parent_mo_or_dn="org-root", vmedia_policy_name=inputdict['vmedia_policy_name'],
                      ext_ip_state="none", bios_profile_name=inputdict['bios_profile_name'],
                      mgmt_fw_policy_name="", agent_policy_name="", mgmt_access_policy_name="",
                      dynamic_con_policy_name="", kvm_mgmt_policy_name="", sol_policy_name="", uuid="", descr="",
                      stats_policy_name="default", policy_owner="local", ext_ip_pool_name="ext-mgmt",
                      boot_policy_name=inputdict['boot_policy_name'], usr_lbl="", host_fw_policy_name="",
                      vcon_profile_name="", ident_pool_name=inputdict['ident_pool_name'],
                      src_templ_name=inputdict['service_profile_template'],
                      local_disk_policy_name=inputdict['local_disk_policy_name'],
                      scrub_policy_name="", power_policy_name=inputdict['power_policy_name'],
                      maint_policy_name="default", name=inputdict['service_profile_name'], power_sync_policy_name="",
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
        obj = result()
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

	blade_upg = eval(inputdict['blade_upg'])
	if blade_upg['upgrade']['value'] == "Yes" and blade_upg['firmware']['value'] != "":
            customlogs("Blade server firmware upgrade started", logfile)
            status, msg = ucsm_upgrade(ip=ipaddress, username=username, password=password, blade=blade_upg['firmware']['value'], logfile=logfile)
            if not status:
		dicts['status'] = "FAILURE"
                customlogs("Failed to upgrade blade server package", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR, "Blade server firmware upgrade failed")
                return obj
            customlogs("Blade server firmware upgrade completed", logfile)

        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      "Blade firmware task completed")
        return obj


    def get_sp_wwpn(self, keys):
	"""
	Return the fibre channel wwpn addresses
    	of a service profile
        """
        wwpn_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(wwpn_list, PTK_OKAY, "success")
            return ret
        res = self.get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        sps = handle.query_classid("lsServer")
	for sp in sps:
	    if sp.type != "updating-template" and sp.dn != '' and sp.pn_dn != '':
		mo = handle.query_dn(sp.dn)
		vnic_data = handle.query_children(in_mo=mo,class_id='VnicFc')
		for fc_vnic in vnic_data:
		    wwpn_list.append(fc_vnic.addr)
        handle.logout()
        res.setResult(wwpn_list, PTK_OKAY, "success")
        return res
