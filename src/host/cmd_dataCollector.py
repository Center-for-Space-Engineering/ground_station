from commandParent import commandParent
from database.databaseControl import dataBaseHandler
from infoHandling.logger import logggerCustom

class cmd_dataCollector(commandParent):
    """This class goes and dynamcal addes all the data types and then ties them to the server, so that they can be requested by the subscriber."""
    def __init__(self, CMD, coms):
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'data_Collector'
        self.__dataBase = dataBaseHandler(coms)
        dictCmd = CMD.getCommandDict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__args ={
            "tables" : self.getTableHTML_Collector,
            "getDataType" : self.getDataType,
            "saveDummyData" : self.saveDummyData,
            "getData": self.getData,
        }

        self.__coms = coms
        self.__logger = logggerCustom("logs/cmd_dataCollector.txt")

    # def run(self):
    #     print("Ran command")

    def runArgs(self, args):
        message = f"<prunning command {self.__comandName} with args {str(args)}<p>"
        # message += self.__args[args[0]](args)
        try:
            message += self.__args[args[0]](args) #note to make this work we will always pass args even if we dont use it.
        except :
            message += "<p> Not vaild arg </p>"
            self.__coms.printMessage("No valid arg on get request! ", 0)

        self.__logger.sendLog("Returned to server: " + message)
        return message
    def getTableHTML_Collector(self, args):
        return self.__dataBase.getTablesHTML()  
    def getArgs(self):
        message = ""
        for key in self.__args:
            if(key == "getDataType"):
                message += f"<p>&emsp;/{self.__comandName}/{key}/-data type-</p>"
            elif (key == "getData"):
                message += f"<p>&emsp;/{self.__comandName}/{key}/-data group-/-start time-</p>"
            else :
                message += f"<p>&emsp;/{self.__comandName}/{key}</p>"
        self.__logger.sendLog("Returned to server: " + message)
        return message
    def getDataType(self, args):
        return str(self.__dataBase.getDataType(args[1]))
    def saveDummyData(self, args):
        try :
            self.__dataBase.insertData("exsample", [10, 1.1, "hello world"])  
            self.__dataBase.insertData("exsample", [10, 1.1, "hello world2"])  
            self.__dataBase.insertData("exsample", [10, 1.1, "hello world3"])
            return "<p>Saved data</p>"
        except :
            self.__coms.printMessage("Failed to save data to the data base! ", 0)
            return "<p>Failed to save data</p>"
    def getData(self, args):
        return self.__dataBase.getData(args[1], args[2])
    def __str__(self):
        return self.__comandName

