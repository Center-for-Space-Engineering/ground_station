'''
    This module is tasked with collecting all relavet inforomation form all peripherals the system knows about. 
'''
import requests

class peripheral_hand_shake():
    def __init__(self, list_of_peripheral:list[str], host_url:str) -> None:
        '''
            For ever peripheral we have we are going to go through and get the commands, then set the host url.
        '''
        self.__commands = {}
        self.__list_of_peripheral = list_of_peripheral
        self.__host_url = host_url
        self.__map = {}
        self.__peripheral_serial_interfaces = {}


    def connect_peripherals(self):
        '''
            this function connects to all the peripherals
        '''
        for url in self.__list_of_peripheral:
            # Get the commands from the peripherals
            try :
                response = requests.get('http://' + url + '/Command')
                if response.status_code == 200:
                    self.__commands[url] = (response.json())
                    self.__map[self.__commands[url]['display_name']] = url
                else :
                    self.__commands[url] = ({
                            'table_data' : 'Unable to get commands',
                            'display_name' : 'Unable to get commands',                
                        })
            except :
                print(f'Command hand shake with peripheral {url} failed')


            # set host url
            data = {
                'sender_url' : self.__host_url
            }
            try :
                response = requests.post('http://' + url + '/receive_url', data)
            except :
                print(f"Could not connect to peripheral {url}")

            ### Collect serial interfaces ###
            try :
                response = requests.get('http://' + url + '/get_serial_names')
                if response.status_code == 200:
                    self.__peripheral_serial_interfaces[url] = (response.json())
                else :
                    self.__peripheral_serial_interfaces[url] = ({
                            'listener' : [],
                            'writter' : [],                
                        })
            except :
                print(f'Serial Interface hand shake with peripheral {url} failed')
    def get_commands(self):
        '''
            Get the commands that we have collected.
        '''
        return self.__commands

    def get_url(self, display_name):
        '''
            This funciton takes the display name, then returns the url assotianted with that display name
        '''
        return self.__commands[display_name]
    def get_peripheral_serial_interfaces(self):
        '''
            Returns all the collecteed serial interfaces fro m the peripherals.
        '''
        return self.__peripheral_serial_interfaces