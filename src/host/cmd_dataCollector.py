'''
    This class is incharge of collecting and adding all the data 
    types dynamically. Then addes them to the server. 
    It also routs commands from the server to the data base
'''
import time
from commandParent import commandParent
from infoHandling.logger import logggerCustom

#pylint disable=c0103
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
                COMS: Message handler class, this is incharge of passing messages to all 
                    other class in the program
                db: This is the data base
        '''
        # pylint: disable=w0231
        # the above pylint disable turns off the warning for not calling the parent constructor.
        self.__comand_name = 'data_Collector'
        self.__data_base = db
        dict_cmd = CMD.getCommandDict()
        #this is the name the webserver will see, 
        # so to call the command send a request for this command.
        dict_cmd[self.__comand_name] = self
        CMD.setCommandDict(dict_cmd)
        self.__args ={
            "tables" : self.get_table_html_collector,
            "get_data_type" : self.get_data_type,
            "get_data": self.get_data,
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
        message = f"<prunning command {self.__comand_name} with args {str(args)}<p>"
        # message += self.__args[args[0]](args)
        try:
            message += self.__args[args[0]](args) 
            #NOTE to make this work we will always pass args even if we dont use it.
        except : # pylint: disable=w0702
            # the above disable is for the warning for not spesifying the exception type
            message += "<p> Not vaild arg </p>"
            self.__coms.printMessage("No valid arg on get request! ", 0)

        self.__logger.sendLog("Returned to server: " + message)
        return message
    #NOTE: we add the dont care varible (_) just to make things eaiser to call dynamically
    def get_table_html_collector(self, _): 
        # pylint: disable=missing-function-docstring
        request_num = self.__data_base.makeRequest('get_tables_html')
        temp = self.__data_base.getRequest(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.getRequest(request_num)
            time.sleep(0.1) #let other process run
        return temp
    def getArgs(self):
        '''
            This function returns an html obj that explains the args for all the internal
            funciton calls. 
        '''
        message = ""
        for key in self.__args:
            if key == "get_data_type":
                message += f"<p>&emsp;/{self.__comand_name}/{key}/-data type-</p>"
            elif key == "get_data":
                message += f"<p>&emsp;/{self.__comand_name}/{key}/-data group-/-start time-</p>"
            else :
                message += f"<p>&emsp;/{self.__comand_name}/{key}</p>"
        self.__logger.sendLog("Returned to server: " + message)
        return message
    def get_data_type(self, args):
        # pylint: disable=missing-function-docstring
        request_num = self.__data_base.makeRequest('get_data_type', [args[1]])
        temp = self.__data_base.getRequest(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.getRequest(request_num)
            time.sleep(0.1) #let other process run
        return str(temp)
    def get_data(self, args):
        '''
            Gets data from the data base
            Args:
                args[0] is not used in this function, 
                    it is used by the caller function, it should be the function name
                args[1] is the table name
                args[2] is the start time
        '''
        request_num = self.__data_base.makeRequest('get_data', [args[1], args[2]])
        temp = self.__data_base.getRequest(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.getRequest(request_num)
            time.sleep(0.1) #let other process run
        return temp
    def __str__(self):
        return self.__comand_name
    