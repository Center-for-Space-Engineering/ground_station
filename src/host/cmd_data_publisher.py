#imports for python
import socket
from datetime import datetime

#custom python imports
from commandParent import commandParent
from threading_python_api.threadWrapper import threadWrapper

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto

class cmd_data_publisher(commandParent, threadWrapper):
    """The init function gose to the cmd class and then pouplates its self into its command dict so that it is dynamically added to the command repo"""
    def __init__(self, CMD, coms):
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

        ############ set up the threadWrapper stuff ############
        # We need the threadWrapper so that we can send a request to start the publisher can send a request to start a new thread.
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs
            #In this case I dont want any other fuctions
        }
        # super(threadWrapper, self).__init__(self.__function_dict)
    def run_args(self, args):
        try:
            message = self.__args[args[0]](args[1:])
            print(f"ran command {str(args[0])} with args {str(args[1:])}")
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except :
            message += "<p> Not vaild arg </p>"
        return message
    def start_data_pubisher(self, arg):
        #get the port from args
        self.__port = arg[0]

        #request the host name from the coms
        host = self.__coms.get_host_name()

        #create a socket object
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.__server_socket.bind((host, self.__port))
            self.__coms.send_request('task_handler', ['add_thread_request_func', self.run_publisher ,'publisher', self])
            return f"<h3> Started data publisher on port:{self.__port} </h3>"
        except Exception as e:
            return f"<p>Error {e}<p>"
    def run_publisher(self):
        try:
            self.__server_socket.listen()
            while True:
                # Accept a connection from a client
                client_socket, client_address = self.__server_socket.accept()
                dto = logger_dto(message=f"Connection established with {client_address}", time=str(datetime.now()))
                self.__coms.print_message(dto)

                # Send data to the connected client
                message = "Hello, client! This is a message from the server."
                client_socket.sendall(message.encode('utf-8'))

                # Close the connection with the client
                client_socket.close()
                dto = logger_dto(message=f"Connection with {client_address} closed", time=str(datetime.now()))
                self.__coms.print_message(dto)
        except Exception as e:
            return f"<p>Error {e}<p>"
    def get_args(self):
        message = ""
        for key in self.__args:
            if key == "start_data_pubisher":
                message += f"<url>/{self.__comandName}/{key}/-port-</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
        return message
    def __str__(self):
        return self.__comandName
    def get_args_server(self):
        message = []
        for key in self.__args:
           if key == "start_data_pubisher":
            message.append({ 
                'Name' : key,
                'Path' : f'/{self.__comandName}/{key}/-port number-',
                'Discription' : 'This command starts a publisher on the port that is given to it. Should be above 5000 and cann\'t be in use.'    
                })
        return message