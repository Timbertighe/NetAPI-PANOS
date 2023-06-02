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
import json

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

        print(json.dumps(self.ospf_summary, indent=4))

        ospf = {
            "id": "",
            "reference": "",
        }

        return ospf

    def area(self):
        """
        OSPF area information

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        ospf : dict
            Dictionary of area information
        """

        print(json.dumps(self.ospf_area, indent=4))

        ospf = {
            "areas": [
                {
                    "id": "",
                    "type": "",
                    "authentication": "",
                    "neigboours": "",
                }
            ]
        }

        return ospf

    def neighbor(self):
        """
        OSPF neighbour information

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        ospf : dict
            Dictionary of OSPF neighbour information
        """

        print(json.dumps(self.ospf_neighbor, indent=4))

        ospf = {
            "neighbor": [
                {
                    "address": "",
                    "interface": "",
                    "state": "",
                    "id": "",
                }
            ],
        }

        return ospf

    def interface(self):
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

        print(json.dumps(self.ospf_interface, indent=4))

        ospf = {
            "interface": [
                {
                    "name": "",
                    "area": "",
                    "state": "",
                    "neighbors": ""
                }
            ]
        }

        return ospf


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
