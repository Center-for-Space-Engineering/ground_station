'''
    This modules is for reporting how many bytes a thread has received.
'''

from termcolor import colored

class byte_report_dto():
    '''
        ARGS:
            thread_name : thread named (str)
            time : time the bytes were received.
            byte_count : how many bytes were received.
    '''
    def __init__(self, thread_name:str, time:str, byte_count:int) -> None:
        self.__thread_name = thread_name
        self.__time = time
        self.__byte_count = byte_count
    def get_time(self):
        '''
            get the time stamp
        '''
        return self.__time
    def get_thread_name(self):
        '''
            get the thread name that made this report
        '''
        return self.__thread_name
    def get_byte_count(self):
        '''
            get the byte count for this report
        '''
        return self.__byte_count
    def __str__(self) -> str:
        return colored(f"Bytes received at: [{self.__time}]", 'light_blue') + " |" + colored(self.__byte_count, 'magenta')
