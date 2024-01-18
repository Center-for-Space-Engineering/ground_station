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
            'write_prem_message_log' : self.write_prem_message_log,
            'get_prem_message_log' : self.get_prem_message_log,
            'thread_report': self.thread_report,
            'get_thread_report':self.get_thread_report,
            'report_status': self.report_status,
            'get_report_status':self.get_report_status,
        }
        super().__init__(self.__function_dict)
        self.__log = loggerCustom("logs/interal_coms_with_server.txt")

        #data structs for storing messages
        self.__messages = []
        self.__prem_messages = []
        self.__report = []
        self.__status = {"Not available" : "No reports at this time"}

        #threading saftey 
        self.__message_lock = Lock()
        self.__prem_message_lock = Lock()
        self.__thread_report_lock = Lock()
        self.__status_lock = Lock()

        #included this because it is standared at this point
        self.__coms = coms

    def write_message_log(self, message):
        with self.__message_lock:
            self.__messages = message
    def write_prem_message_log(self, message):
        with self.__prem_message_lock:
            self.__prem_messages = message
    def thread_report(self, report):
        with self.__thread_report_lock:
            self.__report = report
    def report_status(self, report):
        with self.__status_lock:
            if len(report) < 1 : self.__status = {"Not available" : "No reports at this time"}
            else : self.__status = report
    def get_messages(self):
        print("HEREERE2")

        with self.__message_lock:
            data = self.__messages
        return data
    def get_prem_message_log(self):
        print("HEREERE3")
        with self.__prem_message_lock:
            data = self.__prem_messages 
        return data
    def get_thread_report(self):
        print("HEREERE4")

        with self.__thread_report_lock:
            data = self.__report
        return data
    def get_report_status(self):
        print("HEREERE5")
        with self.__status_lock:
            data = self.__status
        return data
    
    