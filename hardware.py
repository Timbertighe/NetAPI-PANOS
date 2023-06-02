"""
Get hardware information about PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Hardware
        Connect to a PANOS device and collect hardware information

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


class Hardware:
    """
    Connect to a PANOS device and collect hardware information

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
    cpu()
        Get CPU information
    memory()
        Get memory information
    disk()
        Get disk information
    temperature()
        Get temperature information
    fan()
        Get fan information
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
        self.raw_resources = None
        self.raw_disk = None
        self.raw_env = None

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

        # Get CPU and memory information
        self.raw_resources = conn.op(xpath='/show/system/resources')

        # Get disk information
        self.raw_disk = conn.op(xpath='/show/system/disk-space')

        # Get environmental information
        self.raw_env = conn.op(xpath='/show/system/environmentals')

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

    def cpu(self):
        """
        Collect CPU information
        Including usage, idle, 1 min average, 5 min average, 15 min average

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        cpu_list : list
            List of dictionaries containing CPU information
        """

        print(json.dumps(self.raw_resources, indent=4))

        cpu_list = [
            {
                "used": '',
                "idle": '',
                "1_min": '',
                "5_min": '',
                "15_min": ''
            }
        ]

        return cpu_list

    def memory(self):
        """
        Collect memory information
        Including total and used

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        mem : list
            List of dictionaries containing memory information
        """

        print(json.dumps(self.raw_resources, indent=4))

        info = [
            {
                "total": '',
                "used": '',
            }
        ]

        return info

    def disk(self):
        """
        Collect disk information
        Including disk name, size, used

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        storage : list
            List of dictionaries containing disk information
        """

        print(json.dumps(self.raw_disk, indent=4))

        storage = [
            {
                "disk": '',
                "size": '',
                "used": '',
            }
        ]

        return storage

    def temperature(self):
        """
        Collect temperature information
        Including cpu temp and chassic temp

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        temp : list
            List of dictionaries containing temperature information
        """

        print(json.dumps(self.raw_env, indent=4))

        info = [
            {
                "cpu": '',
                "chassis": '',
            }
        ]

        return info

    def fans(self):
        """
        Collect fan information
        Including fan name, status, rpm, and additional detail

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        fan_info : list
            List of dictionaries containing fan information
        """

        print(json.dumps(self.raw_env, indent=4))

        info = [
            {
                "fan": '',
                "status": '',
                "rpm": '',
                "detail": '',
            }
        ]

        return info


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
