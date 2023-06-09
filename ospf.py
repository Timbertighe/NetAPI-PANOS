"""
Get OSPF information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Mac
        Connect to a PANOS device and get OSPF information

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


class Ospf:
    """
    Connect to a PANOS device and get OSPF information

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
    summary()
        Get the OSPF summary
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
        self.ospf_summary = None
        self.ospf_area = None
        self.ospf_neighbor = None
        self.ospf_interface = None

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

        # Collect general OSPF information
        self.ospf_summary = conn.op(
            xpath='/show/routing/protocol/ospf/summary'
        )

        # Collect OSPF area information
        self.ospf_area = conn.op(
            xpath='/show/routing/protocol/ospf/area'
        )

        # Collect OSPF neighbor information
        self.ospf_neighbor = conn.op(
            xpath='/show/routing/protocol/ospf/neighbor'
        )

        # Collect OSPF interface information
        self.ospf_interface = conn.op(
            xpath='/show/routing/protocol/ospf/interface'
        )

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

    def summary(self):
        """
        General OSPF information

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        ospf : dict
            Dictionary of OSPF information
        """

        ospf = {
            "areas": [],
            "neighbor": [],
            "interface": [],
        }

        # Prepare the source information
        general_ospf = self.ospf_summary['response']['result']['entry']
        if type(general_ospf) is not list:
            general_ospf = [general_ospf]

        area_list = self.ospf_area['response']['result']['entry']
        if type(area_list) is not list:
            area_list = [area_list]

        if 'entry' in self.ospf_neighbor['response']['result']:
            neighbour_list = self.ospf_neighbor['response']['result']['entry']
            if type(neighbour_list) is not list:
                neighbour_list = [neighbour_list]
        else:
            neighbour_list = []

        interface_list = self.ospf_interface['response']['result']['entry']
        if type(interface_list) is not list:
            interface_list = [interface_list]

        # Collect general OSPF information
        for ospf_entry in general_ospf:
            # Only support the default instance
            if ospf_entry['virtual-router'] != 'default':
                continue

            ospf['id'] = ospf_entry['router-id']
            ospf['reference'] = "100m"

        # Collect area information
        for area in area_list:
            # Only support the default instance
            if area['virtual-router'] != 'default':
                continue

            entry = {}
            entry['id'] = area['area-id']
            entry['type'] = area['area-type']

            # Authentication is interface based in PANOS
            entry['authentication'] = None

            # Collect the neighbour count per area
            counter = 0
            for neighbour in neighbour_list:
                if neighbour['area-id'] == entry['id']:
                    counter += 1
            entry['neighbours'] = counter

            ospf['areas'].append(entry)

        # Collect neighbor information
        for neighbour in neighbour_list:
            # Only support the default instance
            if neighbour['virtual-router'] != 'default':
                continue

            entry = {}
            entry['address'] = neighbour['neighbor-address']
            entry['interface'] = ''
            entry['state'] = neighbour['status']
            entry['id'] = neighbour['neighbor-router-id']
            ospf['neighbor'].append(entry)

        # Collect interface information
        for interface in interface_list:
            # Only support the default instance
            if interface['virtual-router'] != 'default':
                continue

            entry = {}
            entry['name'] = interface['interface-name']
            entry['state'] = interface['status']
            entry['area'] = interface['area-id']
            entry['neighbors'] = ''
            ospf['interface'].append(entry)

        return ospf


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
