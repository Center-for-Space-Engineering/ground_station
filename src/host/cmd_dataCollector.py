from commandParent import commandParent
from infoHandling.logger import logggerCustom
import time

class cmd_dataCollector(commandParent):
    """This class goes and dynamcal addes all the data types and then ties them to the server, so that they can be requested by the subscriber."""
    def __init__(self, CMD, coms, db):
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'data_Collector'
        self.__dataBase = db
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
        requestNum = self.__dataBase.makeRequest('getTablesHTML', [])
        temp = self.__dataBase.getRequest(requestNum)
        while(temp == None): #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return temp 
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
        requestNum = self.__dataBase.makeRequest('getDataType', [args[1]])
        temp = self.__dataBase.getRequest(requestNum)
        while(temp == None): #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return str(temp)
    def saveDummyData(self, args):
        try :
            requesetNum1 = self.__dataBase.makeRequest('insertData', ["exsample", [10, 1.1, "hello world"]])  
            requesetNum2 = self.__dataBase.makeRequest('insertData', ["exsample", [10, 1.1, "hello world"]])  
            requesetNum3 = self.__dataBase.makeRequest('insertData', ["exsample", [10, 1.1, "hello world"]])  
            return "<p>Saved data</p>"
        except :
            self.__coms.printMessage("Failed to save data to the data base! ", 0)
            return "<p>Failed to save data</p>"
    def getData(self, args):
        requestNum = self.__dataBase.makeRequest('getData', [args[1], args[2]])
        temp = self.__dataBase.getRequest(requestNum)
        while(temp == None): #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return temp
    def __str__(self):
        return self.__comandName