"""
Get VLAN information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Vlan
        Connect to a PANOS device and get a list of VLANs

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


class Vlan:
    """
    Connect to a PANOS device and get VLAN information

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
    vlans()
        Get a list of vlans on the device
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
        self.raw_vlans = None

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

        # Collect a list of VLANs
        self.raw_vlans = conn.op(xpath='/show/vlan', arg='all')

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

    def vlans(self):
        """
        Collect VLAN information
        Including id, name, description, logical interface

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        vlan_list : list
            List of VLANs
        """

        vlan_list = {
            "vlans": []
        }

        vlans = self.raw_vlans['response']['result']['entries']['entry']
        if type(vlans) is not list:
            vlans = [vlans]

        for vlan in vlans:
            if vlan['vif'] is not None:
                entry = {}
                entry['id'] = vlan['vif'].split('.')[1]
                entry['name'] = vlan['name']
                entry['description'] = ''
                entry['irb'] = vlan['vif']
                vlan_list['vlans'].append(entry)

        return vlan_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
