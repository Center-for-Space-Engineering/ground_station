'''
    This command is tasked with collecting data and then publishing it to port.
'''
#imports for python
import socket
from datetime import datetime
import time
import threading
import copy

#custom python imports
from commandParent import commandParent # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto # pylint: disable=e0401
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

import system_constants as config # pylint: disable=e0401

class cmd_data_publisher(commandParent, threadWrapper):
    '''
        This module collects data and then publishes it ever so often to a port. 
    '''
    def __init__(self, CMD, coms):
        #call parent __init__
        # init the parent
        super().__init__(CMD, coms=coms, called_by_child=True)
        ############ set up the threadWrapper stuff ############
        # We need the threadWrapper so that the publisher can send a request to start a new thread.
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs
            #In this case I dont want any other functions
        }
        # super(threadWrapper, self).__init__(self.__function_dict)
        threadWrapper.__init__(self, self.__function_dict)
        
        ############ set up the commandParent stuff ############
        #CMD is the cmd class and we are using it to hold all the command class
        self.__commandName = 'data_publisher'
        self.__args ={
            "start_data_publisher" : self.start_data_publisher,
            "kill_data_publisher" : self.kill_data_publisher
        }
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__commandName] = self #this is the name the web server will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__coms = coms
        self.__port = -1
        self.__server_socket = None
        self.__Running = True
        self.__Running_lock = threading.Lock()
        self.__data_received = []
        self.__data_lock = threading.Lock()
        self.__live_feed = config.board_serial_listener_name

    def run_args(self, args):
        '''
            This function is what allows the server to call function in this class
            ARGS:
                [0] : function name
                [1:] ARGS that the function needs. NOTE: can be blank
        '''
        try:
            message = self.__args[args[0]](args[1:])
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except Exception as e: # pylint: disable=w0718
            message += f"<p> Not valid arg Error {e}</p>"
        return message
    def start_data_publisher(self, arg):
        '''
            Creates a pip object then asks the thread handler to start the pip on its own thread. 
        '''
        self.__Running = True
        threadWrapper.set_status(self, 'Running')

        #get the port from args
        self.__port = int(arg[0])
        source = arg[1]

        #request the host name from the coms
        host = self.__coms.get_host_name()

        #create a socket object
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set the SO_REUSEADDR option
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #set a time out
        self.__server_socket.settimeout(30)  # Set timeout to 30 seconds 

        try:
            self.__server_socket.bind((host, self.__port))
            self.__coms.send_request('task_handler', ['add_thread_request_func', self.run_publisher ,'publisher', self, [source]])
            return f"Started data publisher on port:{self.__port}"
        except Exception as e: # pylint: disable=w0718
            return f"<p>Error {e}<p>"
        
    def kill_data_publisher(self, _): #the args is not used here so we use the _ indicator. 
        '''
            This function simply tells the data publisher to shut down. 
            It does this by setting the self.__Running variable to false. 
        '''
        with self.__Running_lock:
            self.__Running = False
        return "Commanded publisher to terminate."
        

    def run_publisher(self, source):
        '''
            This is the function the runs the pipe on its own thread. 
        '''
        connected = False
        try :
            #wait for client to subscribe.
            self.__server_socket.listen()
            # Accept a connection from a client
            client_socket, client_address = self.__server_socket.accept()
            connected = True
        except socket.timeout:
            dto = logger_dto(message="Timeout occurred while waiting for a connection.", time=str(datetime.now()))
            self.__coms.print_message(dto)
            connected = False

        is_live = False
        
        if source != 'live':
            file_path = f'synthetic_data_profiles/{source}'
            #file_path = 'synthetic_data_profiles/SyntheticFPP2_1000packets_CSEkw_with_garbage.bin'
            #file_path = 'synthetic_data_profiles/FPP2Packetx10.bin'
            #file_path = 'synthetic_data_profiles/SyntheticFPP2_1000packets_CSEkw.bin'
            try :
                file = open(file_path, 'rb') # pylint: disable=R1732
            except Exception as e: # pylint: disable=w0718
                print(f'Failed to open file {e}')
        else : 
            self.__coms.send_request(self.__live_feed, ['create_tap', self.send_tap, 'data publisher']) #create a tap to the serial listener so it will send its data here. 
            is_live = True

        try:
            running = True
            while running:
                if connected:
                    try:
                        with self.__data_lock:
                            length_data_received = len(self.__data_received)
                        # Send data to the connected client
                        if not is_live:
                            message = file.read(-1)
                            if len(message) == 0:
                                file.close()
                                time.sleep(1)
                                file = open(file_path, 'rb')
                            else :
                                print(message)
                                client_socket.sendall(message)
                        elif length_data_received > 0: # If we are live and we have data
                            with self.__data_lock:
                                message = b''.join(self.__data_received)
                                self.__data_received.clear()
                            print(message)
                            client_socket.sendall(message)
                    except Exception as e: # pylint: disable=w0718
                        print("Waiting for connection")
                        print(f"Error {e}")

                        #try and reconnect
                        try :
                            #wait for client to subscribe.
                            self.__server_socket.listen()
                            # Accept a connection from a client
                            client_socket, client_address = self.__server_socket.accept()
                            dto = logger_dto(message=f"Connection established with {client_address}", time=str(datetime.now()))
                            self.__coms.print_message(dto)
                            connected = True
                        except socket.timeout:
                            dto = logger_dto(message="Timeout occurred while waiting for a connection.", time=str(datetime.now()))
                            self.__coms.print_message(dto)
                            connected = False
                with self.__Running_lock:
                    running = self.__Running
            try :
                self.__server_socket.close()
                threadWrapper.set_status(self, 'Complete')
                dto = logger_dto(message="Socket Closed", time=str(datetime.now()))
                self.__coms.print_message(dto)
            except Exception as e: # pylint: disable=w0718
                print("Waiting for connection")
                print(f"Error {e}")
            return "<p>Pip closed <p>"
        except Exception as e: # pylint: disable=w0718
            return f"<p>Error  Server side {e}<p>"

    def send_tap(self, data, _):
        '''
            This is the function that is called by the class you asked to make a tap.
        '''
        with self.__data_lock:
            self.__data_received = copy.deepcopy(data) #NOTE: This could make things really slow, depending on the data rate.

    def get_args(self):
        '''
            This function returns an html obj that explains the args for all the internal
            function calls. 
        '''
        message = ""
        for key in self.__args:
            if key == "start_data_publisher":
                message += f"<url>/{self.__commandName}/{key}/-port-</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
            else:
                message += f"<url>/{self.__commandName}/{key}"
        return message
    def __str__(self):
        return self.__commandName
    def get_args_server(self):
        '''
            This function returns an html obj that explains the args for all the internal
            function calls. 
        '''
        message = []
        for key in self.__args:
            if key == "start_data_publisher":
                message.append({ 
                    'Name' : key,
                    'Path' : f'/{self.__commandName}/{key}/-port number-/-publish source-',
                    'Description' : 'This command starts a publisher on the port that is given to it. Should be above 5000 and cann\'t be in use. You can use any file in synthetic_data_profiles (just type the file name) or pass the key word live,  '    
                    })
            if key == "kill_data_publisher":
                message.append({ 
                    'Name' : key,
                    'Path' : f'/{self.__commandName}/{key}',
                    'Description' : 'This command kills the publisher.'    
                    })
        return message
