'''
    This module handles messages passed by other threads to talk with the server 
'''
#python imports
from threading import Lock
#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom
from threading_python_api.threadWrapper import threadWrapper

class serverMessageHandler(threadWrapper):
    def __init__(self, coms):
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs
            'write_message_log' : self.write_message_log,
            'get_messages' : self.get_messages,
        }
        super().__init__(self.__function_dict)
        self.__log = loggerCustom("logs/interal_coms_with_server.txt")

        #data structs for storing messages
        self.__messages = []

        #threading saftey 
        self.__message_lock = Lock()

        #included this because it is standared at this point
        self.__coms = coms

    def write_message_log(self, message):
        with self.__message_lock:
            self.__messages = message
    
    def get_messages(self):
        with self.__message_lock:
            data = self.__messages
        return data