'''
    This command is tasked with collecting data and then publishing it to port.
'''
#imports for python
import socket
from datetime import datetime
import time

#custom python imports
from commandParent import commandParent # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto # pylint: disable=e0401
from DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

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
            #In this case I dont want any other fuctions
        }
        # super(threadWrapper, self).__init__(self.__function_dict)
        threadWrapper.__init__(self, self.__function_dict)
        
        ############ set up the commandParent stuff ############
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'data_publisher'
        self.__args ={
            "start_data_pubisher" : self.start_data_pubisher
        }
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__coms = coms
        self.__port = -1
        self.__server_socket = None

    def run_args(self, args):
        '''
            This function is what allows the server to call function in this class
            ARGS:
                [0] : funciton name
                [1:] ARGS that the function needs. NOTE: can be blank
        '''
        try:
            message = self.__args[args[0]](args[1:])
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except Exception as e: # pylint: disable=w0718
            message += f"<p> Not vaild arg Error {e}</p>"
        return message
    def start_data_pubisher(self, arg):
        '''
            Creates a pip object then asks the thread handler to start the pip on its own thread. 
        '''
        #get the port from args
        self.__port = int(arg[0])

        #request the host name from the coms
        host = self.__coms.get_host_name()

        #create a socket object
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.__server_socket.bind((host, self.__port))
            self.__coms.send_request('task_handler', ['add_thread_request_func', self.run_publisher ,'publisher', self])
            return f"<h3> Started data publisher on port:{self.__port} </h3>"
        except Exception as e: # pylint: disable=w0718
            return f"<p>Error {e}<p>"

    def run_publisher(self):
        '''
            This is the function the runs the pipe on its own thread. 
        '''
        #wait for clinet to subscribe.
        self.__server_socket.listen()
        # Accept a connection from a client
        client_socket, client_address = self.__server_socket.accept()
        
        #file_path = 'synthetic_data_profiles/TestAAFF00BB.bin'
        file_path = 'synthetic_data_profiles/SyntheticFPP2_1000packets_CSEkw.bin'
        try :
            file = open(file_path, 'rb') # pylint: disable=R1732
        except Exception as e: # pylint: disable=w0718
            print(f'Failed to open file {e}')

        try:
            while True:
                try:
                    # Send data to the connected client
                    message = file.read(519)
                    if len(message) == 0:
                        file.close()
                        time.sleep(30)
                        file = open(file_path, 'rb')
                    else :
                        print(message)
                        client_socket.sendall(message)
                        #time.sleep(10)
                except Exception as e: # pylint: disable=w0718
                    print("Waiting for connection")
                    print(f"Error {e}")
                    self.__server_socket.listen()
                    # Accept a connection from a client
                    client_socket, client_address = self.__server_socket.accept()
                    dto = logger_dto(message=f"Connection established with {client_address}", time=str(datetime.now()))
                    self.__coms.print_message(dto)
                    #repone file
                    file = open(file_path, 'rb') # pylint: disable=R1732


        except Exception as e: # pylint: disable=w0718
            return f"<p>Error  Server side {e}<p>"
    def get_args(self):
        '''
            This function returns an html obj that explains the args for all the internal
            funciton calls. 
        '''
        message = ""
        for key in self.__args:
            if key == "start_data_pubisher":
                message += f"<url>/{self.__comandName}/{key}/-port-</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
        return message
    def __str__(self):
        return self.__comandName
    def get_args_server(self):
        '''
            This function returns an html obj that explains the args for all the internal
            funciton calls. 
        '''
        message = []
        for key in self.__args:
            if key == "start_data_pubisher":
                message.append({ 
                    'Name' : key,
                    'Path' : f'/{self.__comandName}/{key}/-port number-',
                    'Discription' : 'This command starts a publisher on the port that is given to it. Should be above 5000 and cann\'t be in use.'    
                    })
        return message
