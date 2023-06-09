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

        route_list = {
            "entry": []
        }

        routes = self.raw_routing['response']['result']['entry']
        if type(routes) is not list:
            routes = [routes]

        for route in routes:
            # Only supporting the default routing instance
            if route['virtual-router'] != 'default':
                continue

            # Only supporting unicast
            if route['route-table'] != 'unicast':
                continue

            entry = {}
            entry['route'] = route['destination']
            entry['metric'] = route['metric']

            # Parse the flags to get the prococol
            route_type = route['flags'].replace('A', '')
            route_type = route_type.replace('?', '')
            route_type = route_type.replace('E', '')
            route_type = route_type.replace('M', '')
            route_type = route_type.replace('~', '')
            route_type = route_type.replace(' ', '')

            match route_type:
                case 'H':
                    entry['protocol'] = 'host'
                case 'C':
                    entry['protocol'] = 'connected'
                case 'S':
                    entry['protocol'] = 'static'
                case 'B':
                    entry['protocol'] = 'bgp'
                case 'R':
                    entry['protocol'] = 'rip'
                case 'Oi':
                    entry['protocol'] = 'ospf intra-area'
                case 'Oo':
                    entry['protocol'] = 'ospf inter-area'
                case 'O1':
                    entry['protocol'] = 'ospf external type 1'
                case 'O2':
                    entry['protocol'] = 'ospf external type 2'
                case 'O':
                    entry['protocol'] = 'ospf'
                case _:
                    entry['protocol'] = route_type

            entry['next-hop'] = [
                {
                    "hop": route['nexthop'],
                    "interface": route['interface']
                }
            ]

            route_list['entry'].append(entry)

        return route_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
