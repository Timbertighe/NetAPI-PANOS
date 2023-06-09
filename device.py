"""
Get information about PANOS devices

Modules:
    3rd Party: traceback
    Internal: xml_api

Classes:

    Device
        Connect to a PANOS device and collect information

Functions

    None

Exceptions:

    None

Misc Variables:

    RADIUS_TIMEOUT : int
        RADIUS server default timeout in seconds
    RADIUS_RETRIES : int
        RADIUS server default retries
    RADIUS_ACCPORT : int
        RADIUS server default accounting port

Author:
    Luke Robertson - June 2023
"""

import traceback as tb

import xml_api


RADIUS_TIMEOUT = 5
RADIUS_RETRIES = 3
RADIUS_ACCPORT = 1813


class Device:
    """
    Connect to a PANOS device and collect information

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
    facts()
        Get device facts, including hostname, serial, uptime, model, version
    license()
        Get license information, including license id, name, expiry
    radius()
        Get RADIUS server information, including server, timeout, retries
    syslog()
        Get syslog server information, including server, port, facility
    ntp()
        Get NTP server information, including server, version, authentication
    dns()
        Get DNS server information, including server, domain, search
    snmp()
        Get SNMP server information, including server, community, trap
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
        self.raw_info = None
        self.raw_license = None
        self.raw_radius = None
        self.raw_syslog = None
        self.raw_ntp = None
        self.raw_dns = None
        self.raw_snmp = None

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

        SHARED = '/config/shared'
        DEVICES = '/config/devices/entry'

        # Connect to PANOS
        conn = xml_api.XmlApi(self.host, self.token)

        # Get device facts
        self.raw_info = conn.op(xpath='/show/system/info')

        # Get license information
        self.raw_license = conn.op(xpath='/request/license/info')

        # Get RADIUS server information
        self.raw_radius = conn.get_config(
            xpath=f'{SHARED}/server-profile/radius'
        )

        # Get syslog server information
        self.raw_syslog = conn.get_config(
            xpath=f'{SHARED}/log-settings/syslog'
        )

        # Get NTP and DNS server information
        self.system = conn.get_config(
            xpath=f'{DEVICES}/deviceconfig/system'
        )

        # Get SNMP server information
        self.raw_snmp = conn.get_config(
            xpath=f'{DEVICES}/deviceconfig/system/snmp-setting'
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

    def facts(self):
        """
        Get device facts, including hostname, serial, uptime, model, version

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        facts : dict
            Dictionary containing device facts
        """

        dev_facts = self.raw_info['response']['result']['system']

        info = {
            "hostname": dev_facts['hostname'],
            "serial": dev_facts['serial'],
            "uptime": dev_facts['uptime'],
            "model": dev_facts['model'],
            "version": dev_facts['sw-version']
        }

        return info

    def license(self):
        """
        Get license information, including license id, name, expiry

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        lic : list
            A list of licence dictionaries
        """

        lic = {
            'licenses': []
        }

        dev_lic = self.raw_license['response']['result']['licenses']['entry']
        for license in dev_lic:
            entry = {}
            entry['lic_id'] = license['authcode']
            entry['name'] = license['feature']
            entry['expiry'] = license['expires']
            lic['licenses'].append(entry)

        return lic

    def radius(self):
        """
        Get radius information, including server, port, accounting port,
            timeout, retries, source

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        rad : list
            List of radius dictionaries
        """

        rad = {
            "radius-servers": []
        }

        dev_radius = self.raw_radius['response']['result']['radius']['entry']
        if type(dev_radius) is not list:
            dev_radius = [dev_radius]

        for server_list in dev_radius:
            server = server_list['server']['entry']
            if type(server) is not list:
                server = [server]

            for server_entry in server:
                entry = {}
                entry['server'] = server_entry['ip-address']
                entry['port'] = server_entry['port']

                if 'accounting-port' in server_entry:
                    entry['acc_port'] = server_entry['accounting-port']
                else:
                    entry['acc_port'] = RADIUS_ACCPORT

                if 'auth-timeout' in server_entry:
                    entry['timeout'] = server_entry['auth-timeout']
                else:
                    entry['timeout'] = RADIUS_TIMEOUT

                if 'auth-retries' in server_entry:
                    entry['retry'] = server_entry['auth-retries']
                else:
                    entry['retry'] = RADIUS_RETRIES

                if 'source-ip' in server_entry:
                    entry['source'] = server_entry['source-ip']
                else:
                    entry['source'] = ''

                rad['radius-servers'].append(entry)

        return rad

    def syslog(self):
        """
        Get syslog information, including server, facility, level,
            source, prefix

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        sys : list
            List of syslog dictionaries
        """

        sys = {
            "syslog-servers": []
        }

        dev_syslog = self.raw_syslog['response']['result']['syslog']['entry']
        if type(dev_syslog) is not list:
            dev_syslog = [dev_syslog]

        for server_list in dev_syslog:
            server = server_list['server']['entry']
            if type(server) is not list:
                server = [server]

            for server_entry in server:
                entry = {}
                entry['server'] = server_entry['server']
                entry['facilities'] = server_entry['facility']

                if 'level' in server_entry:
                    entry['level'] = server_entry['level']
                else:
                    entry['level'] = ''

                if 'source' in server_entry:
                    entry['source'] = server_entry['source']
                else:
                    entry['source'] = ''

                if 'prefix' in server_entry:
                    entry['prefix'] = server_entry['prefix']
                else:
                    entry['prefix'] = ''

                sys['syslog-servers'].append(entry)

        return sys

    def ntp(self):
        """
        Get NTP information, including server, and preferred

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        ntp_list : list
            List of NTP dictionaries
        """

        ntp_list = {
            "ntp-servers": []
        }

        if 'ntp-servers' in self.system['response']['result']['system']:
            ntp_servers = (
                self.system['response']['result']['system']['ntp-servers']
            )

            # Get the primary NTP server
            if 'primary-ntp-server' in ntp_servers:
                ntp_list['ntp-servers'].append(
                    {
                        "server": (
                            ntp_servers
                            ['primary-ntp-server']
                            ['ntp-server-address']
                        ),
                        "prefer": True
                    }
                )

            # Get the secondary NTP servers
            if 'secondary-ntp-server' in ntp_servers:
                ntp_list['ntp-servers'].append(
                    {
                        "server": (
                            ntp_servers
                            ['secondary-ntp-server']
                            ['ntp-server-address']
                        ),
                        "prefer": False
                    }
                )
        else:
            ntp_list['ntp-servers'].append(
                {
                    "server": "",
                    "prefer": False
                }
            )

        return ntp_list

    def dns(self):
        """
        Get DNS information, including domain, server, and source

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        dns_list : dict
            Dictionary containing DNS information
        """

        dns_list = {
            'dns-servers': {
                'servers': []
            }
        }
        system = self.system['response']['result']['system']

        # Get the domain name
        if 'domain' in system:
            dns_list['dns-servers']['domain'] = system['domain']

        # Get the primary DNS server
        if 'primary' in system['dns-setting']['servers']:
            dns_list['dns-servers']['servers'].append(
                {
                    'server': system['dns-setting']['servers']['primary'],
                    'source': ''
                }
            )

        # Get the secondary DNS server
        if 'secondary' in system['dns-setting']['servers']:
            dns_list['dns-servers']['servers'].append(
                {
                    'server': system['dns-setting']['servers']['secondary'],
                    'source': ''
                }
            )

        return dns_list

    def snmp(self):
        """
        Get SNMP information, including name, contact, description, community,
            access, and clients

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        snmp_list : dict
            Dictionary containing SNMP information
        """

        snmp_list = {
            "snmp": {
                "communities": [
                ]
            }
        }

        # Check that there is a result (there may not be for a standby device)
        if self.raw_snmp['response']['result'] is not None:
            snmp_servers = self.raw_snmp['response']['result']['snmp-setting']
        else:
            snmp_servers = []

        if 'name' in snmp_servers:
            snmp_list['snmp']['name'] = snmp_servers['name']
        else:
            snmp_list['snmp']['name'] = ''

        if 'contact' in snmp_servers:
            snmp_list['snmp']['contact'] = snmp_servers['contact']
        else:
            snmp_list['snmp']['contact'] = ''

        if 'description' in snmp_servers:
            snmp_list['snmp']['description'] = snmp_servers['description']
        else:
            snmp_list['snmp']['description'] = ''

        if snmp_servers:
            if 'v2c' in snmp_servers['access-setting']['version']:
                entry = {}
                entry['community'] = (
                    snmp_servers
                    ['access-setting']
                    ['version']
                    ['v2c']
                    ['snmp-community-string']
                )
                entry['access'] = ''
                entry['clients'] = ['']
                snmp_list['snmp']['communities'].append(entry)
            else:
                snmp_list['snmp']['communities']['community'] = ''
                snmp_list['snmp']['communities']['access'] = ''
                snmp_list['snmp']['communities']['clients'] = ['']
        else:
            snmp_list['snmp']['communities'] = {}
            snmp_list['snmp']['communities']['community'] = ''
            snmp_list['snmp']['communities']['access'] = ''
            snmp_list['snmp']['communities']['clients'] = ['']

        return snmp_list


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
