"""
Get MAC table information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Mac
        Connect to a PANOS device and get the MAC table

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


class Mac:
    """
    Connect to a PANOS device and get the MAC table

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
    mac()
        Get a the MAC address table
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
        self.raw_mac = None

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

        # Collect the MAC table
        self.raw_mac = conn.op(xpath='/show/mac', arg='all')

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

    def mac(self):
        """
        Collect the MAC table
        Including mac, vlan, interface

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        mac_list : list
            List of MAC addresses
        """

        table = self.raw_mac['response']['result']['entries']
        if type(table) is not list:
            table = [table]

        # If the FW is in L3 mode, there won't be any entries
        # Remember, this is not ARP, its the MAC table
        if table[0] is None:
            mac_list = {
                "entry": [
                    {
                        "mac": '',
                        "vlan": '',
                        "interface": '',
                    }
                ]
            }

        # Otherwise, get all the entries
        # This has not been fully tested
        else:
            for item in table:
                entry = {}
                entry['mac'] = item['mac']
                entry['vlan'] = item['vlan']
                entry['interface'] = item['interface']
                mac_list.append(entry)

        return mac_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
