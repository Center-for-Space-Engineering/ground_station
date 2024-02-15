'''
    This module handles messages passed by other threads to talk with the server 
'''
#python imports
from threading import Lock
import datetime

#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401

class serverMessageHandler(threadWrapper):
    '''
        This class is tasked with handling messages sent to the server, because the server is 
        already busy, and there is a high volume of messages that need to go to the server. Thus we 
        have a class that runs on its own thread tasked with collecting the information for the server. 
    '''
    def __init__(self, coms):
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs
            'write_message_log' : self.write_message_log,
            'get_messages' : self.get_messages,
            'write_prem_message_log' : self.write_prem_message_log,
            'get_prem_message_log' : self.get_prem_message_log,
            'thread_report': self.thread_report,
            'get_thread_report':self.get_thread_report,
            'report_status': self.report_status,
            'get_report_status':self.get_report_status,
            'report_byte_status':self.report_byte_status,
            'get_byte_report':self.get_byte_report,
        }
        super().__init__(self.__function_dict)
        _ = loggerCustom("logs/internal_coms_with_server.txt") # Not used at this time

        #data structs for storing messages
        self.__messages = []
        self.__prem_messages = []
        self.__report = []
        self.__status = {"Not available" : "No reports at this time"}
        self.__byte_status = []

        #threading safety 
        self.__message_lock = Lock()
        self.__prem_message_lock = Lock()
        self.__thread_report_lock = Lock()
        self.__status_lock = Lock()
        self.__byte_status_lock = Lock()

        #included this because it is standard at this point
        _= coms # Not used at this time

    def write_message_log(self, message):
        '''
            this function adds a message to the log that the server will then display.
        '''
        with self.__message_lock:
            self.__messages = message
    def write_prem_message_log(self, message):
        '''
            this function adds a message to the permanent log that the server will then display.
        '''
        with self.__prem_message_lock:
            self.__prem_messages = message
    def thread_report(self, report):
        '''
            this function adds a message to the threading report that the server will then display.
        '''
        with self.__thread_report_lock:
            self.__report = report
    def report_status(self, report):
        '''
            this function adds a message the status report that the server will then display.
        '''
        with self.__status_lock:
            self.__status = report
    def report_byte_status(self, data):
        '''
            this function adds a message to the log that contains the number of bytes received that the server will then display.
        '''
        with self.__byte_status_lock:
            self.__byte_status = data 
    def get_messages(self):
        '''
            Server uses this function to pull the message log.
        '''
        with self.__message_lock:
            data = self.__messages
        return data
    def get_prem_message_log(self):
        '''
            Server uses this Function to pull the prem message log.
        '''
        with self.__prem_message_lock:
            data = self.__prem_messages
        return data
    def get_thread_report(self):
        '''
            Server uses this Function to pull the threading report log.
        '''
        with self.__thread_report_lock:
            data = self.__report
        return data
    def get_report_status(self):
        '''
            Server uses this function to pull the status message log.
        '''
        with self.__status_lock:
            data = self.__status
        return data
    def get_byte_report(self):
        '''
            Server uses this function to pull byte report log.
        '''
        with self.__byte_status_lock:
            if len(self.__byte_status) <= 0:
                data = [
                    {
                        'time' : datetime.datetime.now(),
                        'bytes' : 0,
                    }
                ]
            else : data = self.__byte_status
            self.__byte_status = {}
        return data
    
    
    