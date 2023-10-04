import os
import sys
sys.path.insert(0, "..")
from logging_system_display_python_api.logger import logggerCustom



class dinamicImporter:
    def __init__(self, coms):
        self.__logger = logggerCustom("logs/dynamicaImporter_log.txt")
        l_files = os.listdir()
        self.__mods = []
        for file in l_files:
            if "cmd_" in file:
                module = __import__(file.strip(".py"))
                self.__mods.append(getattr(module, file.strip(".py")))
                self.__logger.sendLog("Found Module: " + file.strip(".py"))
        self.__logger.sendLog("Collected Modules: " + str(self.__mods))
        coms.printMessage("Collected Modules: " + str(self.__mods), 2)
        

    def getModList(self):
        return self.__mods
        
                