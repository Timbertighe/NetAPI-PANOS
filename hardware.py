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

        top = self.raw_resources['response']['result']
        top = top.split('\n')
        cpu_avg = top[0].split(',')
        cpu_stats = top[2].split(',')

        cpu_list = {
            "cpu": [
                {
                    "used": float(
                        cpu_stats[0].replace('%Cpu(s):  ', '')
                        .replace(' us', '')
                    ),
                    "idle": float(
                        cpu_stats[3].replace(' id', '').replace(' ', '')
                    ),
                    "1_min": float(
                        cpu_avg[3].replace('  load average: ', '')
                    ),
                    "5_min": float(
                        cpu_avg[4].replace(' ', '')
                    ),
                    "15_min": float(
                        cpu_avg[5].replace(' ', '')
                    ),
                }
            ]
        }

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

        top = self.raw_resources['response']['result']
        top = top.split('\n')
        mem_stats = top[3].split(',')

        total = (
            mem_stats[0]
            .replace('KiB Mem : ', '')
            .replace(' total', '')
            .replace(' ', '')
        )
        used = (
            mem_stats[2]
            .replace(' used', '')
            .replace(' ', '')
        )

        info = {
            "memory": [
                {
                    "total": int(total),
                    "used": int(used)
                }
            ]
        }

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

        storage = {
            "disk": [
            ]
        }

        disk_list = self.raw_disk['response']['result'].split('\n')
        for item in disk_list[1::]:
            entry = {}
            entry['disk'] = item.split()[0]
            entry['size'] = item.split()[1]
            entry['used'] = item.split()[2]
            storage['disk'].append(entry)

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

        info = {
            "temperature": [
                {
                    "cpu": '',
                    "chassis": '',
                }
            ]
        }

        dev_temp = (
            self.raw_env['response']['result']['thermal']['Slot1']['entry']
        )

        for item in dev_temp:
            entry = {}
            entry['cpu'] = item['DegreesC']
            entry['chassis'] = item['description']
            info['temperature'].append(entry)

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

        info = {
            'fan': [
            ]
        }

        fan_data = self.raw_env['response']['result']['fan']['Slot1']['entry']

        for item in fan_data:
            entry = {}
            entry['fan'] = item['description']

            if item['alarm'] == 'False':
                entry['status'] = 'OK'
            else:
                entry['status'] = 'Alert'

            entry['rpm'] = item['RPMs']
            entry['detail'] = ''
            info['fan'].append(entry)

        return info


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
