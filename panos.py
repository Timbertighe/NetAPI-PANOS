"""
The PANOS plugin for the Net-API framework

Modules:
    3rd Party: xmlrpc.server, json
    Internal: TBA

Classes:

    None

Functions

    TBA

Exceptions:

    None

Misc Variables:

    TBA

Author:
    Luke Robertson - June 2023
"""

# External imports
import json

# Internal imports
import device
import hardware
import interfaces
import lldp
import vlans
import mac
import routing
import ospf


def device_info(host, token):
    """
    Collect device information

    Parameters
    ----------
    host : str
        Hostname or IP address of the device
    token : str
        The API token

    Raises
    ------
    None

    Returns
    -------
    info : json
        JSON formatted string containing device information
    """

    info = {}
    with device.Device(host=HOST, token=TOKEN) as conn:
        info.update(conn.facts())
        info.update(conn.license())
        info.update(conn.radius())
        info.update(conn.syslog())
        info.update(conn.ntp())
        info.update(conn.dns())
        info.update(conn.snmp())

    return json.dumps(info)


# Run the RPC server
if __name__ == '__main__':
    HOST = 'xxx'
    TOKEN = 'xxx=='

    # Testing for now
    print(device_info(HOST, TOKEN))
