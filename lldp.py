"""
Get LLDP information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Lldp
        Connect to a PANOS device and get a list of connected devices

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


class Lldp:
    """
    Connect to a PANOS device and get a list of LLDP neighbours

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
    interfaces()
        Get a list of interfaces on the device
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
        self.raw_lldp = None

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

        # Collect a list LLDP neighbours
        self.raw_lldp = conn.op(xpath='/show/lldp/neighbors', arg='all')

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

    def interfaces(self):
        """
        Collect LLDP neighbour information
        Including name, mac, system, ip, vendor, description, model, serial
        Note, not all of this will be available,
            it depends on what the neighbour shares

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        lldp_list : list
            List of LLDP neighbours
        """

        lldp_list = {
            "interfaces": []
        }

        neighbour_list = self.raw_lldp['response']['result']['entry']
        if type(neighbour_list) is not list:
            neighbour_list = [neighbour_list]

        for neighbour in neighbour_list:
            # If there are no neighbours, skip
            if neighbour['neighbors'] is None:
                continue

            entry = {}

            # PANOS doesn't provide this information
            entry['model'] = ''
            entry['serial'] = ''
            entry['vendor'] = ''

            # Get general information
            entry['name'] = neighbour['@name']
            entry['system'] = neighbour['neighbors']['entry']['system-name']
            entry['description'] = (
                neighbour['neighbors']['entry']['system-description']
            )

            # Get the MAC and/or the IP address if available
            entry['mac'] = ''
            entry['ip'] = ''
            if 'management-address' in neighbour['neighbors']['entry']:
                mgmt = (
                    neighbour
                    ['neighbors']
                    ['entry']
                    ['management-address']
                    ['entry']
                )
                if type(mgmt) is not list:
                    mgmt = [mgmt]
                for address in mgmt:
                    if address['address-type'] == "MAC":
                        entry['mac'] = address['@name']
                    else:
                        entry['ip'] = address['@name']

            lldp_list['interfaces'].append(entry)

        return lldp_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
