import sys
from dinamicImporter import dinamicImporter
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom



'''This class takes all the commands that have been dynamically imported and maps them to the server. 
NOTE: every command must have a unqie name.'''
class cmd():
    def __init__(self, coms):
        self.__logger = logggerCustom("logs/cmd_log.txt")
        self.__commandDict = {}
        self.__coms = coms
        
    
    '''This func will look through the __commandDict to see if there is a map from the get request to a command.'''
    def parseCmd(self, message):
        if message[0] in self.__commandDict:
            self.__logger.sendLog("Command Action: " + str(self.__commandDict[message[0]]) + str(message))
            self.__coms.printMessage("Command Action: " + str(self.__commandDict[message[0]]) + str(message), 2)
            if(len(message) == 1):
                return self.__commandDict[message[0]].run()
            else :
                return self.__commandDict[message[0]].runArgs(message[1:])
            
        #if no command recived return list of commands that can be run
        message = "<h1> <strong>Supported Commands</strong></h1>"
        for key in self.__commandDict:
            message += f"<p>/{key}</p>"
            message += f"{self.__commandDict[key].getArgs()}"            
        return message
    def getCommandDict(self):
        return self.__commandDict       
    def setCommandDict(self, new):
        self.__commandDict = new
    '''This fuc creats the dynamicImporter (spelled wrong, call it my programing style), after the dynamicImporter goes through the folder searching for any extra commands it adds them into the __commandDict so that the server can levrage them.'''
    def collectCommands(self, db):
        x = dinamicImporter(self.__coms)
        moduleList = x.getModList()

        for obj in moduleList: #if you want to add any args to the __init__ function other than cmd you will have to change the code in this for loop. I recomend you just use setters. Or find a way not to use them at all.  
            if('cmd_dataCollector' in str(obj)):
                 myc_obj = obj(self, self.__coms, db) #Here I need the data base refrance for the data base collector class
            else :
                myc_obj = obj(self, self.__coms) #the reason why I pass cmd into the new class is so that the class can define its own command names and structures.
            
        self.__logger.sendLog("Commands added to the server: " + str(self.__commandDict))
        self.__coms.printMessage(str(self.__commandDict), 8)
if __name__ == "__main__":
    x = cmd()
    print(x.getCommandDict())
    x.parseCmd(["exsample"])

    


