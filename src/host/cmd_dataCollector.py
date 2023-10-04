'''
    This class is incharge of collecting and adding all the data types dynamically. Then addes them to the server. 
    It also routs commands from the server to the data base
'''
from commandParent import commandParent
from infoHandling.logger import logggerCustom
import time

class cmd_dataCollector(commandParent):
    """
        This class goes and dynamcal addes all the data types and then ties them to the server, 
        so that they can be requested by the subscriber.
        In addition it handles all the commands going to the data base
    """
    def __init__(self, CMD, coms, db):
        '''
            ARGS:
                CMD: this is our command handler class 
                COMS: Message handler class, this is incharge of passing messages to all other class in the program
                db: This is the data base
        '''
        # pylint: disable=w0231 
        # the above pylint disable turns off the warning for not calling the parent constructor. 
        self.__comandName = 'data_Collector'
        self.__dataBase = db
        dictCmd = CMD.getCommandDict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__args ={
            "tables" : self.getTableHTML_Collector,
            "getDataType" : self.getDataType,
            "getData": self.getData,
        }

        self.__coms = coms
        self.__logger = logggerCustom("logs/cmd_dataCollector.txt")
    def runArgs(self, args):
        '''
            This function is what allows the server to call function in this class
            ARGS:
                [0] : funciton name
                [1:] ARGS that the function needs. NOTE: can be blank
        '''
        message = f"<prunning command {self.__comandName} with args {str(args)}<p>"
        # message += self.__args[args[0]](args)
        try:
            message += self.__args[args[0]](args) #note to make this work we will always pass args even if we dont use it.
        except : # pylint: disable=w0702
            # the above disable is for the warning for not spesifying the exception type
            message += "<p> Not vaild arg </p>"
            self.__coms.printMessage("No valid arg on get request! ", 0)

        self.__logger.sendLog("Returned to server: " + message)
        return message
    def getTableHTML_Collector(self, _): #NOTE: we add the dont care varible (_) just to make things eaiser to call dynamically
        # pylint: disable=missing-function-docstring
        requestNum = self.__dataBase.makeRequest('getTablesHTML')
        temp = self.__dataBase.getRequest(requestNum)
        while temp is None: #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return temp 
    def getArgs(self):
        '''
            This function returns an html obj that explains the args for all the internal
            funciton calls. 
        '''
        message = ""
        for key in self.__args:
            if key == "getDataType":
                message += f"<p>&emsp;/{self.__comandName}/{key}/-data type-</p>"
            elif key == "getData":
                message += f"<p>&emsp;/{self.__comandName}/{key}/-data group-/-start time-</p>"
            else :
                message += f"<p>&emsp;/{self.__comandName}/{key}</p>"
        self.__logger.sendLog("Returned to server: " + message)
        return message
    def getDataType(self, args):
        # pylint: disable=missing-function-docstring
        requestNum = self.__dataBase.makeRequest('getDataType', [args[1]])
        temp = self.__dataBase.getRequest(requestNum)
        while temp is None: #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return str(temp)
    
    def getData(self, args):
        '''
            Gets data from the data base
            Args:
                args[0] is not used in this function, it is used by the caller function, it should be the function name
                args[1] is the table name
                args[2] is the start time
        '''
        requestNum = self.__dataBase.makeRequest('getData', [args[1], args[2]])
        temp = self.__dataBase.getRequest(requestNum)
        while temp is None: #wait until we get a return value
            temp = self.__dataBase.getRequest(requestNum)
            time.sleep(0.1) #let other process run
        return temp
    def __str__(self):
        return self.__comandName
    