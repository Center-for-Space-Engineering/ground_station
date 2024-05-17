'''
    This Modules job is to go and get all the class that are named cmd_<name> and turn 
    them into code that can be used by the server. It is a way to dynamically import modules
    and give control of the module to the server. 
'''

from dynamicImporter import dynamicImporter # pylint: disable=e0401
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401

#print DTO
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class cmd_inter():
    '''
        This class takes all the commands that have been dynamically imported and maps them to the server. 
        NOTE: every command must have a unique name.
    '''
    def __init__(self, coms, db):
        '''
            args: coms is the message handler class
        '''
        self.__logger = loggerCustom("logs/cmd_inter_log.txt")
        self.__commandDict = {}
        self.__coms = coms
        self.collect_commands(db)
        
    def parse_cmd(self, message):
        '''
            This func will look through the __commandDict to see if there is a map from the get request to a command.
        '''
        if message[0] in self.__commandDict:
            self.__logger.send_log("Command Action: " + str(self.__commandDict[message[0]]) + str(message))
            dto = print_message_dto("Command Action: " + str(self.__commandDict[message[0]]) + str(message))
            self.__coms.print_message(dto)
            if len(message) == 1:
                returnVal = self.__commandDict[message[0]].run()
            else :
                returnVal = self.__commandDict[message[0]].run_args(message[1:])
            return returnVal
            
        #if no command received return list of commands that can be run
        message = "<h1> <strong>Supported Commands</strong></h1>"
        for key in self.__commandDict:
            message += f"{self.__commandDict[key].get_args()}"            
        return message
    def get_command_dict(self):
        # pylint: disable=missing-function-docstring
        return self.__commandDict       
    def setCommandDict(self, new):
        # pylint: disable=missing-function-docstring
        self.__commandDict = new
    def collect_commands(self, db):
        '''
            This fuc creates the dynamicImporter (spelled wrong, call it my programming style), after the dynamicImporter goes through the folder searching for any extra commands it adds them into the __commandDict so that the server can leverage them.
        '''
        x = dynamicImporter(self.__coms)
        moduleList = x.get_mod_list()

        for obj in moduleList: #if you want to add any args to the __init__ function other than cmd you will have to change the code in this for loop. I recommend you just use setters. Or find a way not to use them at all.  
            if 'cmd_data_collector' in str(obj):
                _ = obj(self, self.__coms, db) #Here I need the data base reference for the data base collector class
            else :
                _ = obj(self, self.__coms) #the reason why I pass cmd into the new class is so that the class can define its own command names and structures.
            
        self.__logger.send_log("Commands added to the server: " + str(self.__commandDict))
        dto = print_message_dto(str(self.__commandDict))
        self.__coms.print_message(dto, 8)
    
    def get_commands_webpage(self):
        '''
          This function collects all the commands and how to run them, then returns that info to the server in a dictionary so that it can be displayed to the user.
        '''
        message = []
        for key in self.__commandDict:
            message += self.__commandDict[key].get_args_server()
        return message
