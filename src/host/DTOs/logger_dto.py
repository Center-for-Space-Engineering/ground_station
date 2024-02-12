'''
    This is the dto (data transfer object) for sending a time and a message to the logging systems in the code with a time stamp
'''

from termcolor import colored

class logger_dto():
    '''
        Just give it a time stamp and messgae
    '''
    def __init__(self, time:str, message:str):
        self.__time = time
        self.__message = message
    def get_time(self):
        '''
            get the time stamp
        '''
        return self.__time
    def get_message(self):
        '''
            get the message
        '''
        return self.__message
    def __str__(self) -> str:
        '''
            to string over load
        '''
        return "[" + colored(self.__time, 'blue') + "]: " + str(self.__message)
