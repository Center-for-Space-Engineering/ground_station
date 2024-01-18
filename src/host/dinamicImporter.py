'''
    
'''
import os
from logging_system_display_python_api.logger import loggerCustom

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto

class dinamicImporter:
    def __init__(self, coms):
        self.__logger = loggerCustom("logs/dynamicaImporter_log.txt")
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
        return self.__mods
        
                