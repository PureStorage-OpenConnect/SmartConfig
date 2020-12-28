import urllib3
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.infra.apiresults import *
import re
from purity_fb import PurityFb, NfsRule, rest, FileSystem, Subnet, NetworkInterface
from pure_dir.services.utils.miscellaneous import execute_remote_command, execute_local_command
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
import time

class FlashBladeTasks:
    def __init__(self, ipaddress='', username='', password=''):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.ipaddress = ipaddress
        self.username = username
        self.password = password
        self.handle, self.fb = self.flashblade_handler()

    def flashblade_handler(self):
        handle, fb = None, None
        try:
            token_list = execute_remote_command(self.ipaddress, self.username, self.password,
                                                'pureadmin list --api-token')
            if not token_list[1]:
                loginfo("FlashBlade is not reachable")
                return handle, fb
            if execute_remote_command(self.ipaddress, self.username, self.password,
                                      'pureadmin list --api-token')[1] != "":
                execute_remote_command(self.ipaddress, self.username, self.password,
                                       'pureadmin delete --api-token')
            val = execute_remote_command(self.ipaddress, self.username, self.password,
                                         'pureadmin create --api-token')
            api_token = re.findall(r'(T-[0-9a-zA-Z-]+)',val[1])[0]
            fb = PurityFb(self.ipaddress)
            # Disable SSL verification
            fb.disable_verify_ssl()
            handle = fb.login(api_token)
            return handle, fb
        except rest.ApiException as e:
            loginfo("An Exception occured while logging into the FlashBlade: {}\n".format(str(e.body)))
            return handle, fb
 
    def flash_blade_info(self, ip):
        hw_list = self.fb.hardware.list_hardware()
        details = {}
        for hw in hw_list.items:
            if hw.type == "ch":
                details['serial_no'] = hw.serial
            elif hw.type == "fb":
                if hw.model is not None:
                    details['model'] = hw.model
            if len(details) == 2:
                break
            arr_list = self.fb.arrays.list_arrays()
            for arr in arr_list.items:
                details['id'] = arr.id
                details['name'] = arr.name
                break
        #TODO: Need to find a proper way to get the mac address
        arp_cmd = f'arp {ip}'
        error, output = execute_local_command(arp_cmd)
        op = output.split('\n')[1]
        details['mac_addr'] = re.split(' +', op)[2]
        self.fb.logout()
        return details

    def create_subnet(self, inputs, logfile):
        obj = result()
        subnet_data = {}
        dicts = {}
        loginfo('Create Subnet input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Creating Subnet {}".format(inputs['name'])
            subnet_data = self.fb.subnets.create_subnets(names=[inputs['name']],subnet=Subnet(prefix=inputs['prefix'], 
                                      gateway=inputs['gateway'], vlan=int(inputs['vlan']), mtu=int(inputs['mtu'])))
            if subnet_data:
                dicts['prefix'] = inputs['prefix']
                obj.setResult(dicts, PTK_OKAY, "Created Subnet successfully")
                loginfo("Created Subnet successfully")
                customlogs("Created Subnet successfully\n", logfile)
                return obj
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create Subnet")
            loginfo("Unable to create Subnet")
            customlogs("Unable to create Subnet\n", logfile)
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to create Subnet", logfile)
            loginfo("Error while creating Subnet is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create Subnet")
            return obj
        finally:
            self.fb.logout()

    def delete_subnet(self, inputs, logfile):
        obj = result()
        dicts = {}
        loginfo('Delete Subnet input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Deleting Subnet {}".format(inputs['name'])
            self.fb.subnets.delete_subnets(names=[inputs['name']])
            obj.setResult(dicts, PTK_OKAY, "Deleted Subnet successfully")
            loginfo("Deleted Subnet successfully")
            customlogs("Deleted Subnet successfully\n", logfile)
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to delete Subnet", logfile)
            loginfo("Error while deleting Subnet is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to delete Subnet")
            return obj
        finally:
            self.fb.logout()

    def create_network_interface(self, inputs, logfile):
        obj = result()
        nw_data = {}
        dicts = {}
        loginfo('Create Network Interface input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Creating Network Interface {}".format(inputs['name'])
            nw_interface = NetworkInterface(address=inputs['address'], services=["data"], type="vip")
            nw_data = self.fb.network_interfaces.create_network_interfaces(names=[inputs['name']],
                                                                           network_interface=nw_interface)
            if nw_data:
                obj.setResult(dicts, PTK_OKAY, "Created Network Interface successfully")
                loginfo("Created Network Interface successfully")
                customlogs("Created Network Interface successfully\n", logfile)
                return obj
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create Network Interface")
            loginfo("Unable to create Network Interface")
            customlogs("Unable to create Network Interface\n", logfile)
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to create Network Interface", logfile)
            loginfo("Error while creating Network Interface is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create Network Interface")
            return obj
        finally:
            self.fb.logout()

    def delete_network_interface(self, inputs, logfile):
        obj = result()
        dicts = {}
        loginfo('Delete Network Interface input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Deleting Network Interface {}".format(inputs['name'])
            self.fb.network_interfaces.delete_network_interfaces(names=[inputs['name']])
            obj.setResult(dicts, PTK_OKAY, "Deleted Network Interface successfully")
            loginfo("Deleted Network Interface successfully")
            customlogs("Deleted Network Interface successfully\n", logfile)
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to delete Network Interface", logfile)
            loginfo("Error while deleting Network Interface is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to delete Network Interface")
            return obj
        finally:
            self.fb.logout()

    def create_file_system(self, inputs, logfile):
        obj = result()
        dicts = {}
        fs = None
        export_rule = inputs['export_rule'] + "(rw,no_root_squash)"
        loginfo('Create File System input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Creating NFS {}".format(inputs['name'])
            provisioned_size = eval(inputs['provisioned_set'])
            provisioned_size_bytes = (int(provisioned_size['provisioned_size']['value']) * 
                               int(provisioned_size['provisioned_size_unit']['value']))
            if 'v3' in inputs['nfs_version']:
                fs = FileSystem(name=inputs['name'], 
                                provisioned=provisioned_size_bytes,
                                snapshot_directory_enabled=inputs['snapshot'], 
                                fast_remove_directory_enabled=inputs['fast_remove'],
                                nfs=NfsRule(v3_enabled=True, rules=export_rule))
            elif 'v4' in inputs['nfs_version']:
                fs = FileSystem(name=inputs['name'], 
                                provisioned=provisioned_size_bytes,
                                snapshot_directory_enabled=inputs['snapshot'],
                                fast_remove_directory_enabled=inputs['fast_remove'],
                                nfs=NfsRule(v4_1_enabled=True, rules=export_rule))
            if fs:
                fs_data = self.fb.file_systems.create_file_systems(fs)
            if fs_data:
                obj.setResult(dicts, PTK_OKAY, "Created NFS successfully")
                loginfo("Created NFS successfully")
                customlogs("Created NFS successfully\n", logfile)
                return obj
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create NFS")
            loginfo("Unable to create NFS")
            customlogs("Unable to create NFS\n", logfile)
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to create NFS", logfile)
            loginfo("Error while creating NFS is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to create NFS")
            return obj
        finally:
            self.fb.logout()

    def delete_file_system(self, inputs, logfile):
        obj = result()
        fs = None
        dicts = {}
        loginfo('Delete File System input is: {}'.format(inputs))
        if not self.handle:
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Unable to connect to FlashBlade")
            return obj
        try:
            msg = "Deleting NFS {}".format(inputs['name'])
            ls_fs_data = self.fb.file_systems.list_file_systems(names=[inputs['name']], 
                                                          filter='nfs.v3_enabled or nfs.v4_1_enabled')
            if ls_fs_data.items:
                if ls_fs_data.items[0].nfs.v3_enabled:
                    fs = FileSystem(nfs=NfsRule(v3_enabled=False))   
                    loginfo("Disabling nfsv3")
                elif ls_fs_data.items[0].nfs.v4_1_enabled:
                    fs = FileSystem(nfs=NfsRule(v4_1_enabled=False))
                    loginfo("Disabling nfsv4")
                self.fb.file_systems.update_file_systems(name=inputs['name'], attributes = fs)
            time.sleep(5)
            loginfo("Destroying the file system {}".format(inputs['name']))
            self.fb.file_systems.update_file_systems(name=inputs['name'], attributes = FileSystem(destroyed=True))
            time.sleep(5)
            loginfo("Eradicating the file system {}".format(inputs['name']))
            self.fb.file_systems.delete_file_systems(name=inputs['name'])
            time.sleep(10)
            loginfo("Deleted NFS successfully")
            customlogs("Deleted NFS successfully\n", logfile)
            obj.setResult(dicts, PTK_OKAY, "NFS deleted successfully")
            return obj
        except rest.ApiException as e:
            error = e.body
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(error), logfile)
            customlogs("Unable to delete NFS", logfile)
            loginfo("Error while deleting NFS is {}".format(str(error)))
            obj.setResult(dicts, PTK_INTERNALERROR, "Unable to Delete NFS")
            return obj
        finally:
            self.fb.logout()
