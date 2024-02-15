'''
    This class finds the user defined commands (cmd) then gives those to the server. 
'''
#python imports
import os

#custom python imports
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401

#import DTO for communicating internally
from DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class dynamicImporter:
    '''
        When this class is initialized it searches for files that have the cmd_ prefix then imports the class
        and gives those to the server. 
    '''
    def __init__(self, coms):
        self.__logger = loggerCustom("logs/dynamicImporter_log.txt")
        l_files = os.listdir()
        self.__mods = []
        for file in l_files:
            if ("cmd_" in file) and ("cmd_inter" not in file):
                module = __import__(file.strip(".py"))
                self.__mods.append(getattr(module, file.strip(".py")))
                self.__logger.send_log("Found Module: " + file.strip(".py"))
        self.__logger.send_log("Collected Modules: " + str(self.__mods))
        dto = print_message_dto("Collected Modules: " + str(self.__mods))
        coms.print_message(dto, 2)
        

    def get_mod_list(self):
        '''
            Returns the list of modules that it found
        '''
        return self.__mods
        