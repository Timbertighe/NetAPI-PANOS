"""
Get inferface information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Interfaces
        Connect to a PANOS device and a list of interfaces
            and information about them

Functions

    None

Exceptions:

    None

Misc Variables:

    None

Author:
    Luke Robertson - June 2023
"""

import traceback as tb

import xml_api


class Interfaces:
    """
    Connect to a PANOS device and a list of interfaces
    Collect information about these interfaces

    Supports being instantiated with the 'with' statement

    Attributes
    ----------
    host : str
        IP address or FQDN of the device to connect to
    token : str
        API token to use for authentication

    Methods
    -------
    __init__(host, user, password)
        Class constructor
    __enter__()
        Called when the 'with' statement is used
    __exit__(exc_type, exc_value, traceback)
        Called when the 'with' statement is finished
    raw_interfaces()
        Collect raw interface information
    interfaces()
        Get a list of interfaces on the device
    sub_interfaces()
        Collect subinterface information
    sub_description()
        Collect descriptions for subinterfaces
    phy_description()
        Collect descriptions for physical interfaces
    """

    def __init__(self, host, token):
        """
        Class constructor

        Parameters
        ----------
        host : str
            IP address or FQDN of the device to connect to
        token : str
            API token to use for authentication

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Authentication information
        self.host = host
        self.token = token

        # Device information
        self.hardware_int = None
        self.logical_int = None
        self.raw_data = None
        self.descriptions = None

    def __enter__(self):
        """
        Called when the 'with' statement is used

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        self
            The instantiated object
        """

        # Connect to PANOS
        conn = xml_api.XmlApi(self.host, self.token)

        # Collect a list of hardware and logical interfaces
        #   We can get more detail on each as needed later
        self.hardware_int = conn.op(xpath='/show/interface', arg='hardware')
        self.logical_int = conn.op(xpath='/show/interface', arg='logical')

        # Get interface config
        config = conn.get_config(
            xpath='/config/devices/entry/network/interface'
        )
        self.int_config = config['response']['result']['interface']
        self.log_int = self.logical_int['response']['result']['ifnet']['entry']

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when the 'with' statement is finished

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        self
            None
        """

        # handle errors that were raised
        if exc_type:
            print(
                f"Exception of type {exc_type.__name__} occurred: {exc_value}"
            )
            if traceback:
                print("Traceback:")
                print(tb.format_tb(traceback))

    def sub_interfaces(self):
        """
        Collect subinterface information
        Align this with the parent interfaces

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Look at each entry in the logical interface list
        for sub in self.log_int:
            # If there is a '.' in the name, it is a subinterface
            if '.' in sub['name']:
                # Get the parent interface name by splitting on the '.'
                parent = sub['name'].split('.')[0]
                # Look at each entry in the hardware interface list for a match
                for iface in self.raw_data['interfaces']:
                    if iface['phy']['name'] == parent:
                        if 'sub' not in iface:
                            iface['sub'] = []
                        iface['sub'].append(sub)
                        break

    def sub_description(self):
        """
        Collect descriptions for subinterfaces
        This is only in the config, which makes it trickier

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Get descriptions for subinterfaces
        descriptions = {
            'interface': []
        }

        interfaces = self.int_config['ethernet']['entry']
        if type(interfaces) is not list:
            interfaces = [interfaces]
        for ethernet in interfaces:
            if 'layer2' in ethernet and 'units' in ethernet['layer2']:
                units = ethernet['layer2']['units']['entry']
                if type(units) is not list:
                    units = [units]
                for unit in units:
                    if 'comment' in unit:
                        desc = unit['comment']
                    else:
                        desc = ''
                    entry = {}
                    entry['name'] = unit['@name']
                    entry['description'] = desc
                    descriptions['interface'].append(entry)
            if 'layer3' in ethernet and 'units' in ethernet['layer3']:
                units = ethernet['layer3']['units']['entry']
                if type(units) is not list:
                    units = [units]
                for unit in units:
                    if 'comment' in unit:
                        desc = unit['comment']
                    else:
                        desc = ''
                    entry = {}
                    entry['name'] = unit['@name']
                    entry['description'] = desc
                    descriptions['interface'].append(entry)

        interfaces = self.int_config['loopback']['units']['entry']
        if type(interfaces) is not list:
            interfaces = [interfaces]
        for loopback in interfaces:
            if '.' in loopback['@name']:
                if 'comment' in loopback:
                    desc = loopback['comment']
                else:
                    desc = ''
                entry = {}
                entry['name'] = loopback['@name']
                entry['description'] = desc
                descriptions['interface'].append(entry)

        if self.int_config['vlan']['units'] is not None:
            interfaces = self.int_config['vlan']['units']['entry']
            if type(interfaces) is not list:
                interfaces = [interfaces]
            for vlan in interfaces:
                if '.' in vlan['@name']:
                    if 'comment' in vlan:
                        desc = vlan['comment']
                    else:
                        desc = ''
                    entry = {}
                    entry['name'] = vlan['@name']
                    entry['description'] = desc
                    descriptions['interface'].append(entry)

        interfaces = self.int_config['tunnel']['units']['entry']
        if type(interfaces) is not list:
            interfaces = [interfaces]
        for tunnel in interfaces:
            if '.' in tunnel['@name']:
                if 'comment' in tunnel:
                    desc = tunnel['comment']
                else:
                    desc = ''
                entry = {}
                entry['name'] = tunnel['@name']
                entry['description'] = desc
                descriptions['interface'].append(entry)

        interfaces = self.int_config['aggregate-ethernet']['entry']
        if type(interfaces) is not list:
            interfaces = [interfaces]
        for ae in interfaces:
            if 'layer2' in ae and 'units' in ae['layer2']:
                units = ae['layer2']['units']['entry']
                if type(units) is not list:
                    units = [units]
                for unit in units:
                    if 'comment' in unit:
                        desc = unit['comment']
                    else:
                        desc = ''
                    entry = {}
                    entry['name'] = unit['@name']
                    entry['description'] = desc
                    descriptions['interface'].append(entry)
            if 'layer3' in ae and 'units' in ae['layer3']:
                units = ae['layer3']['units']['entry']
                if type(units) is not list:
                    units = [units]
                for unit in units:
                    if 'comment' in unit:
                        desc = unit['comment']
                    else:
                        desc = ''
                    entry = {}
                    entry['name'] = unit['@name']
                    entry['description'] = desc
                    descriptions['interface'].append(entry)

        self.descriptions = descriptions

    def phy_description(self, iface):
        """
        Collect descriptions for parent interfaces
        This is only in the config, which makes it trickier

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Get physical descriptions - Much harder than it should be
        description = ''
        if 'ethernet' in iface['name']:
            for item in self.int_config['ethernet']['entry']:
                if item['@name'] == iface['name']:
                    if 'comment' in item:
                        description = item['comment']

        elif 'loopback' in iface['name']:
            for item in self.int_config['loopback']['units']['entry']:
                if item['@name'] == iface['name']:
                    if 'comment' in item:
                        description = item['comment']

        elif 'tunnel' in iface['name']:
            for item in self.int_config['tunnel']['units']['entry']:
                if item['@name'] == iface['name']:
                    if 'comment' in item:
                        description = item['comment']

        elif 'vlan' in iface['name']:
            if self.int_config['vlan']['units'] is not None:
                the_interface = self.int_config['vlan']['units']['entry']
                if type(the_interface) is not list:
                    the_interface = [the_interface]
                for item in the_interface:
                    if item['@name'] == iface['name']:
                        if 'comment' in item:
                            description = item['comment']

        elif 'ae' in iface['name']:
            the_interface = self.int_config['aggregate-ethernet']['entry']
            if type(the_interface) is not list:
                the_interface = [the_interface]
            for item in the_interface:
                if item['@name'] == iface['name']:
                    if 'comment' in item:
                        description = item['comment']

        return description

    def raw_interfaces(self):
        """
        Collect raw interface information
        This will be formatted later

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Collect operational information about interfaces
        # In PANOS, interfaces are split into physical and logical components
        # Logical interfaces are not the same thing as subinterfaces
        phy_int = self.hardware_int['response']['result']['hw']['entry']
        raw_data = {
            "interfaces": []
        }

        # Loop through physical interfaces, record this information
        for iface in phy_int:
            entry = {}
            entry['phy'] = iface

            # Align logical interfaces (not subinterfaces) with physical
            for log in self.log_int:
                if log['name'] == iface['name']:
                    entry['log'] = log
                    break

            # Collect detailed information for this specific interface
            conn = xml_api.XmlApi(self.host, self.token)
            interface = conn.op(xpath='/show/interface', arg=iface['name'])
            entry['detail'] = interface

            entry['description'] = self.phy_description(iface)

            raw_data['interfaces'].append(entry)

        self.raw_data = raw_data

    def interfaces(self):
        """
        Collect detailed interface information
        Including name, mac, description, family, address, speed,
            counters, and subinterfaces

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        int_list : list
            List of interfaces and their information
        """

        # Collect raw interface data
        self.raw_interfaces()

        # Connect subinterfaces to their parent interfaces
        self.sub_interfaces()

        # Collect sub-interface descriptions
        self.sub_description()

        int_list = {
            "interfaces": [
            ]
        }

        # We have a lot of interface data availble
        # Let's parse it into a more usable format
        for iface in self.raw_data['interfaces']:
            entry = {}
            entry['name'] = iface['phy']['name']
            entry['mac'] = iface['phy']['mac']
            entry['description'] = iface['description']

            if 'log' not in iface:
                entry['family'] = "None"
            elif iface['log']['ip'] == "N/A":
                entry['family'] = "Ethernet"
            else:
                entry['family'] = "inet"
                entry['address'] = iface['log']['ip']

            if iface['phy']['state'] == "down":
                entry['speed'] = "None"
            else:
                entry['speed'] = iface['phy']['speed']

            # Get Counters
            entry['counters'] = {}
            entry['counters']['bps_in'] = ''
            entry['counters']['bps_out'] = ''
            entry['counters']['pps_in'] = ''
            entry['counters']['pps_out'] = ''

            # Get subinterfaces
            entry['subinterfaces'] = []
            if 'sub' in iface:
                for sub_iface in iface['sub']:
                    sub_entry = {}
                    sub_entry['subinterface'] = sub_iface['name']

                    if sub_iface['ip'] == "N/A":
                        sub_entry['family'] = "Ethernet"
                    else:
                        sub_entry['family'] = "inet"
                        sub_entry['address'] = sub_iface['ip']

                    for desc in self.descriptions['interface']:
                        if desc['name'] == sub_iface['name']:
                            sub_entry['description'] = desc['description']
                            break
                    # sub_entry['description'] = ''
                    entry['subinterfaces'].append(sub_entry)

            # No PoE on these firewalls
            entry['poe'] = {}
            entry['poe']['admin'] = 'N/A'
            entry['poe']['operational'] = 'N/A'
            entry['poe']['max'] = 'N/A'
            entry['poe']['used'] = 'N/A'

            # Append to list
            int_list['interfaces'].append(entry)

        return int_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
