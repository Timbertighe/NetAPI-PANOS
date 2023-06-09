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
from xmlrpc.server import SimpleXMLRPCServer

# Internal imports
import device
import hardware
import interfaces
import lldp
import vlans
import mac
import routing
import ospf


# RPC settings
#   Use 'localhost' to only allow connections from the local machine
#   Use '0.0.0.0' to allow connections from any machine
#   Use a specific IP to bind to a specific NIC
HOSTNAME = '0.0.0.0'
PORT = 8011


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
    with device.Device(host=host, token=token) as conn:
        info.update(conn.facts())
        info.update(conn.license())
        info.update(conn.radius())
        info.update(conn.syslog())
        info.update(conn.ntp())
        info.update(conn.dns())
        info.update(conn.snmp())

    return json.dumps(info)


def hardware_info(host, token):
    """
    Collect device hardware information

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
    with hardware.Hardware(host=host, token=token) as conn:
        info.update(conn.cpu())
        info.update(conn.memory())
        info.update(conn.disk())
        info.update(conn.temperature())
        info.update(conn.fans())

    return json.dumps(info)


def interface_info(host, token):
    """
    Collects a list of interfaces and their details

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
    with interfaces.Interfaces(host=host, token=token) as conn:
        info.update(conn.interfaces())

    return json.dumps(info)


def lldp_info(host, token):
    """
    Collects a list of connected devices and their details

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
    with lldp.Lldp(host=host, token=token) as conn:
        info.update(conn.interfaces())

    return json.dumps(info)


def vlan_info(host, token):
    """
    Collects a list of VLANs

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
    with vlans.Vlan(host=host, token=token) as conn:
        info.update(conn.vlans())

    return json.dumps(info)


def mac_info(host, token):
    """
    Collects the MAC address table

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
    with mac.Mac(host=host, token=token) as conn:
        info.update(conn.mac())

    return json.dumps(info)


def routing_info(host, token):
    """
    Collects the routing table

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
    with routing.Routing(host=host, token=token) as conn:
        info.update(conn.routing())

    return json.dumps(info)


def ospf_info(host, token):
    """
    Collects OSPF information

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
    with ospf.Ospf(host=host, token=token) as conn:
        info.update(conn.summary())

    return json.dumps(info)


def rpc_server():
    """
    Start the XML-RPC server, and exposes functions to the client

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

    # Create the server
    print('Starting server...')
    server = SimpleXMLRPCServer((HOSTNAME, PORT))

    # Register the functions
    server.register_function(device_info, 'device_info')
    server.register_function(hardware_info, 'hardware')
    server.register_function(interface_info, 'interfaces')
    server.register_function(lldp_info, 'lldp')
    server.register_function(vlan_info, 'vlans')
    server.register_function(mac_info, 'mac')
    server.register_function(routing_info, 'routing')
    server.register_function(ospf_info, 'ospf')

    # Start the server
    server.serve_forever()


# Run the server
if __name__ == '__main__':
    # Nicely handle keyboard interrupts
    try:
        rpc_server()
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        print('Exiting...')
