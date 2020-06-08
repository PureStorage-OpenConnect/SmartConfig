
def get_fs_components(fs_con_data):
    devices_list = [{'name':'Name', 'mac':'MAC Address', 'model':'Model', 'serial_no':'Serial Number', 'leadership':'Leadership', 'ip_address':'IP Address', 'vip_address':'Virtual IP Address'}]
    components_name = ['MDS', 'Nexus 9k', 'Nexus 5k', 'PURE', 'UCSM']
    components_dict = {}
    device_name_dict = {}
    if fs_con_data.get('components') != {}:
        components = fs_con_data['components']
    else:
        return devices_list, components_dict
    for comp_data in components.iteritems():
        name_list = []
        device_dict = {'ip_address' : "", 'leadership' : "", 'mac' : "", 'model' : "", 'name' : "", 'serial_no' : "", 'vip_address' : ""}
        if comp_data[0] in components_name:
           for comp_count in range(len(comp_data[1])):
               device_dict['name'] = comp_data[1][comp_count]['name']
               device_dict['mac'] = comp_data[1][comp_count]['mac']
               device_dict['model'] = comp_data[1][comp_count]['model']
               device_dict['serial_no'] = comp_data[1][comp_count]['serial_no'] 
               if 'leadership' in comp_data[1][comp_count].keys():
                   device_dict['leadership'] = comp_data[1][comp_count]['leadership']
               device_dict['ip_address'] = comp_data[1][comp_count]['ipaddress']
               if 'vipaddress' in comp_data[1][comp_count].keys():
                   device_dict['vip_address'] = comp_data[1][comp_count]['vipaddress']
               devices_list.append(device_dict.copy())
               name_list.append(device_dict['name'])
               device_name_dict[device_dict['name']] = device_dict['model'] + " " + device_dict['name']
           components_dict[comp_data[0]] = name_list
           
    return devices_list, components_dict, device_name_dict


def get_fs_connections(fs_con_data, component, component_name):
    connection_list = [{'device':"Local Device", 'lport': "Local Port", 'connection': "Connection", 'r_device': "Remote Device", 'r_port': "Remote Port"}]
    connection_dict = {'device':component_name, 'connection': "", 'lport':"", 'r_device':"", 'r_port':""}
    if fs_con_data.get('connections') != {}:
        connections_info = fs_con_data['connections']
    else:
         return connection_list

    for connections in connections_info.iteritems():
        if connections[0] == component:
            if connections[1] == []:
                connection_list.append(connection_dict.copy())
                return connection_list
            for connection in connections[1]:
                if connection.get('connection') != None:
                    connection_dict['connection'] = connection['connection']
                connection_dict['lport'] = connection['local_interface']
                connection_dict['r_device'] = connection['remote_device']
                connection_dict['r_port'] = connection['remote_interface']
                connection_list.append(connection_dict.copy())
                connection_dict = {'device' : "", 'connection': "", 'lport': "", 'r_device': "", 'r_port': ""}
    return connection_list


