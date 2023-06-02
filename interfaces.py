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
import json

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
        self.hardware_int = None
        self.logical_int = None

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

        print(json.dumps(self.hardware_int, indent=4))
        print(json.dumps(self.logical_int, indent=4))

        int_list = {
            "interfaces": [
                {
                    "name": '',
                    "mac": '',
                    "description": '',
                    "family": '',
                    "address": '',
                    "speed": '',
                    "counters": {
                        "bps_in": '',
                        "bps_out": '',
                        "pps_in": '',
                        "pps_out": ''
                    },
                    "subinterfaces": [
                        {
                            "subinterface": '',
                            "family": '',
                            "address": '',
                            "description": '',
                        }
                    ],
                    "poe": {
                        "admin": '',
                        "operational": '',
                        "max": '',
                        "used": ''
                    }
                }
            ]
        }

        return int_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
