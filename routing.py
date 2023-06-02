"""
Get routing table information from PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Mac
        Connect to a PANOS device and get the routing table

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


class Routing:
    """
    Connect to a PANOS device and get the routing table

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
    routing()
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
        self.raw_routing = None

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
        self.raw_routing = conn.op(xpath='/show/routing/route')

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

    def routing(self):
        """
        Collect the routing table
        Including route, protocol, metric, nexthop, and interface

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        route_list : list
            List of routes
        """

        print(json.dumps(self.raw_routing, indent=4))

        route_list = {
            "entry": [
                {
                    "route": '',
                    "protocol": '',
                    "metric": '',
                    "next-hop": [
                        {
                            "hop": '',
                            "interface": ''
                        }
                    ]
                }
            ]
        }

        return route_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
