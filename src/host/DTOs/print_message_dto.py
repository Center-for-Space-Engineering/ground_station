'''
    This is the dto (data transfer object) for sending a time and a message to the logging systems in the code 
'''
class print_message_dto():
    '''
        Just give it a time messgae
    '''
    def __init__(self, message:str):
        self.__message = message
    def get_message(self):
        '''
            get the message
        '''
        return self.__message
    def __str__(self) -> str:
        return self.__message