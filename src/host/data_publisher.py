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
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto # pylint: disable=e0401


class data_publisher(threadWrapper):
    '''
        This module collects data and then publishes it ever so often to a port. 
    '''
    def __init__(self, coms, live_feed:str):
        ############ set up the threadWrapper stuff ############
        # We need the threadWrapper so that the publisher can send a request to start a new thread.
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs
            #In this case I dont want any other functions
        }
        threadWrapper.__init__(self, self.__function_dict)
        
        self.__coms = coms
        self.__port = -1
        self.__server_socket = None
        self.__Running = True
        self.__Running_lock = threading.Lock()
        self.__data_received = []
        self.__data_lock = threading.Lock()
        self.__live_feed = live_feed
        self.__connected = False
        self.__connected_lock = threading.Lock()

    def start_data_publisher(self, arg):
        '''
            Creates a pip object then asks the thread handler to start the pip on its own thread.

            ARGS:
                args[0] : port
                args[1] : 'live' or file path
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
            return f"Starting data publisher at {host}:{self.__port}"
        except Exception as e: # pylint: disable=w0718
            return f"<p>Error {e}<p>"
        
    def kill_data_publisher(self): #the args is not used here so we use the _ indicator. 
        '''
            This function simply tells the data publisher to shut down. 
            It does this by setting the self.__Running variable to false. 
        '''
        print("Got kill command")
        with self.__Running_lock:
            self.__Running = False
        return "Commanded publisher to terminate."
        

    def run_publisher(self, source): # pylint: disable=r0915
        '''
            This is the function the runs the pipe on its own thread. 
        '''
        connected = False
        is_live = False
        
        if source != 'live':
            file_path = f'synthetic_data_profiles/{source}'
            try :
                file = open(file_path, 'rb') # pylint: disable=R1732
            except Exception as e: # pylint: disable=w0718
                print(f'Failed to open file {e}')
        else : 
            self.__coms.send_request(self.__live_feed, ['create_tap', self.send_tap, 'data publisher']) #create a tap to the serial listener so it will send its data here. 
            is_live = True
        
        print(f"Waiting for connection port {self.__port}")

        client_socket, connected = self.get_connection()

        print(f"Got connection port {self.__port}")

        try: # pylint: disable=r1702
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
                                file = open(file_path, 'rb') # pylint: disable=r1732
                            else :
                                client_socket.sendall(message)
                        elif length_data_received > 0: # If we are live and we have data
                            with self.__data_lock:
                                message = b''.join(self.__data_received)
                                self.__data_received.clear()
                            client_socket.sendall(message)
                        else :
                            sleep = True
                    except Exception as e: # pylint: disable=w0718
                        print("Waiting for connection")
                        print(f"Error {e}")

                        connected = False

                        with self.__connected_lock:
                            self.__connected = connected

                        #try and reconnect
                        client_socket, connected = self.get_connection()
                with self.__Running_lock:
                    running = self.__Running
                if sleep:
                    time.sleep(0.01)
                    sleep = False
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
    def get_connection(self):
        '''
            This function waits for someone to connect to the port, then publishes the data. 
        '''
        # Disable the timeout on the socket
        self.__server_socket.settimeout(None)
        
        #wait for client to subscribe.
        self.__server_socket.listen()

        # Accept a connection from a client
        client_socket, client_address = self.__server_socket.accept()
        dto = logger_dto(message=f"Connection established with {client_address}", time=str(datetime.now()))
        self.__coms.print_message(dto)

        connected = True
        
        with self.__connected_lock:
            self.__connected = connected
        
        return client_socket, connected
    def send_tap(self, data, _):
        '''
            This is the function that is called by the class you asked to make a tap.
        '''
        with self.__connected_lock:
            connected = self.__connected
        with self.__data_lock:
            if connected:
                self.__data_received.append(copy.deepcopy(data)) #NOTE: This could make things really slow, depending on the data rate.
    def kill_Task(self):
        '''
            Small modification here to make sure the serial port gets closed. 
        '''
        self.kill_data_publisher()
        threadWrapper.kill_Task(self)
