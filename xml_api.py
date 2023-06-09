"""
XML-API functions for connecting to PANOS devices

Modules:
    External: requests, xmltodict

Classes:

    XmlApi
        Connect to a PANOS device using the XML API

Functions

    TBA

Exceptions:

    None

Misc Variables:

    TBA

Author:
    Luke Robertson - June 2023

Enable API access on the device and get an API key
    https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/enable-api-access
    https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-xml-api/get-your-api-key
"""

import requests
import xmltodict


class XmlApi:
    """
    Connect to a PANOS device using XML-API

    Supports being instantiated with the 'with' statement

    Attributes
    ----------
    host : str
        The FQDN of the device to connect to
    token : str
        The API token to use for authentication

    Methods
    -------
    check_response(response)
        Check a response from a device
        Confirm that it was successful

    get_config()
        Get the current configuration
        Use XPath to limit the config
    """

    def __init__(self, host, token):
        """
        Class constructor

        Collects the details needed to connect to the PANOS device
        Requires a valid certificate to be installed on the device
        Does not support being called with the 'with' statement
            This is because the connection is stateless

        Parameters
        ----------
        host : str
            The FQDN of the device to connect to
        token : str
            The API token to use for authentication

        Raises
        ------
        None

        Returns
        -------
        None
        """

        # Store the details needed to connect to the device
        self.host = f'https://{host}/api'
        self.headers = {
            'Content-Type': 'application/xml',
            'X-PAN-KEY': token
        }

    def check_response(self, response):
        """
        Check a response from a device
        Confirm that it was successful

        Parameters
        ----------
        response : dict
            The response, formatted as a dictionary

        Raises
        ------
        None

        Returns
        -------
        bool
            True if the response was successful
        """

        # A dictionary of error codes and their meanings
        err_codes = {
            '400': 'Bad request',
            '403': 'Forbidden',
            '1': 'Unknown command',
            '2': 'Internal error',
            '3': 'Internal error',
            '4': 'Internal error',
            '5': 'Internal error',
            '6': 'Bad Xpath',
            '7': 'Object not present',
            '8': 'Object not unique',
            '10': 'Reference count not zero',
            '11': 'Internal error',
            '12': 'Invalid object',
            '13': 'Object not found',
            '14': 'Operation not possible',
            '15': 'Operation denied',
            '16': 'Unauthorized',
            '17': 'Invalid command',
            '18': 'Malformed command',
            '19': 'Success',
            '20': 'Success',
            '21': 'Internal error',
            '22': 'Session timed out',
        }

        # A failure response will have a status of 'error'
        if response['response']['@status'] == 'error':
            # Get the error code
            code = response['response']['@code']

            # Get the error message
            #   The error message is in a different place
            #   depending on the request type
            if 'msg' in response['response']:
                error = response['response']['msg']
            elif 'result' in response['response']:
                error = response['response']['result']['msg']
            else:
                error = 'Unknown error'

            # Print the error messages
            print("Error accessing the API")
            if code not in err_codes:
                print(f'Unknown error code: {code}')
            else:
                print(f'Error code: {code} ({err_codes[code]})')
            print(f'Error: {error}')

            # Return False to indicate a failure
            return False

        # Return True to indicate a success
        return True

    def get_config(self, xpath):
        """
        Get config information from the device

        Parameters
        ----------
        xpath : str
            The xpath to the config to retrieve
            This an an XML structure as a path

        Raises
        ------
        None

        Returns
        -------
        response_dict : dict
            The response from the device, formatted as a dictionary
        dict
            An error message if the request failed
        """

        # Create the URL to connect to
        url = f'{self.host}/?type=config&action=get&xpath={xpath}'

        # Make the request
        response = requests.get(
            url,
            headers=self.headers,
            verify=True
        )

        # Check the response was successful
        response_dict = xmltodict.parse(response.text)
        if self.check_response(response_dict):
            return response_dict
        else:
            return {
                "error": "Error retrieving config"
            }

    def op(self, xpath, **kwargs):
        """
        Run operational commands on the device

        An xpath for the command is required. This may run on its own
            eg, '/show/system/info' for 'show system info'
        An additional argument may be passed. This is optional
            This is done if there is a target for the command to operate on
            For example, we might want to run a command against an interface
            eg, xpath = '/show/interface' and arg = 'ae1'
            This would run 'show interface ae1'

        Parameters
        ----------
        xpath : str
            The xpath that represents the operational command
        **kwargs : dict
            arg : str
                The argument to pass to the command

        Raises
        ------
        None

        Returns
        -------
        TBA
        """

        # Check if extra arguments were passed
        if 'arg' in kwargs:
            arg = kwargs['arg']
        else:
            arg = ''

        # Convert the xpath to XML
        xml = self.xpath_to_xml(xpath, arg)

        # Create the URL to connect to
        url = f'{self.host}/?type=op&cmd={xml}'

        # Make the request
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=True
            )
        except requests.exceptions.ConnectTimeout:
            return {
                "error": "Timeout while connecting to device",
                "command": xml
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "Error connecting to device",
                "command": xml
            }
        except Exception as e:
            return {
                "error": f"Error while connecting: {e}",
                "command": xml
            }

        # Check the response was successful
        response_dict = xmltodict.parse(response.text)
        if self.check_response(response_dict):
            return response_dict
        else:
            return {
                "error": "Error retrieving config",
                "command": xml
            }

    def xpath_to_xml(self, xpath, argument):
        """
        Convert an xpath to an XML structure

        Parameters
        ----------
        xpath : str
            The xpath to convert

        Raises
        ------
        None

        Returns
        -------
        xml : str
            The XML structure
        """

        # Split the xpath into a list
        x_list = xpath.split('/')
        x_list.pop(0)

        # Create the XML structure
        xml = ''
        for entry in x_list:
            xml += f'<{entry}>'

        # Add the argument
        xml += argument

        for entry in reversed(x_list):
            xml += f'</{entry}>'

        # Return the XML structure
        return xml


# Handle running as a script
if __name__ == '__main__':
    print('This module should not be run as a script')
