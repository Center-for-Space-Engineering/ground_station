'''
    This class is incharge of collecting and adding all the data 
    types dynamically. Then addes them to the server. 
    It also routs commands from the server to the data base
'''
import time
from commandParent import commandParent
from logging_system_display_python_api.logger import loggerCustom

#pylint disable=c0103
class cmd_dataCollector(commandParent):
    """
        This class goes and dynamcal addes all the data types and then ties them to the server, 
        so that they can be requested by the subscriber.
        In addition it handles all the commands going to the data base
    """
    def __init__(self, CMD, coms, db, max_rows_per_dto = 10000):
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
        dict_cmd = CMD.get_command_dict()
        #this is the name the webserver will see, 
        # so to call the command send a request for this command.
        dict_cmd[self.__comand_name] = self
        CMD.setCommandDict(dict_cmd)
        self.__args ={
            "tables" : self.get_table_html_collector,
            "get_data_type" : self.get_data_type,
            "get_data": self.get_data,
            "get_dto": self.get_dto,
        }

        self.__coms = coms
        self.__logger = loggerCustom("logs/cmd_dataCollector.txt")
        self.__max_rows = max_rows_per_dto
    def run_args(self, args):
        '''
            This function is what allows the server to call function in this class
            ARGS:
                [0] : funciton name
                [1:] ARGS that the function needs. NOTE: can be blank
        '''
        message = f"<prunning command {self.__comand_name} with args {str(args)}<p>"
        message += self.__args[args[0]](args)
        # try:
        #     message += self.__args[args[0]](args) 
        #     #NOTE to make this work we will always pass args even if we dont use it.
        # except : # pylint: disable=w0702
        #     # the above disable is for the warning for not spesifying the exception type
        #     message += "<p> Not vaild arg </p>"
        #     self.__coms.print_message("No valid arg on get request! ", 0)

        self.__logger.send_log("Returned to server: " + message)
        return message
    #NOTE: we add the dont care varible (_) just to make things eaiser to call dynamically
    def get_table_html_collector(self, _): 
        # pylint: disable=missing-function-docstring
        request_num = self.__data_base.make_request('get_tables_html')
        temp = self.__data_base.get_request(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.get_request(request_num)
            time.sleep(0.1) #let other process run
        return temp
    def get_args(self):
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
        self.__logger.send_log("Returned to server: " + message)
        return message
    def get_data_type(self, args):
        # pylint: disable=missing-function-docstring
        request_num = self.__data_base.make_request('get_data_type', [args[1]])
        temp = self.__data_base.get_request(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.get_request(request_num)
            time.sleep(0.1) #let other process run
        return str(temp)
    def get_data(self, args):
        '''
            Gets data from the data base
            Args:
                args[0] is not used in this function, 
                    it is used by the caller function, it should be the function name
                args[1] is the table name
                args[2] is the start index
        '''
        request_num = self.__data_base.make_request('get_data', [args[1], args[2]])
        temp = self.__data_base.get_request(request_num)
        while temp is None: #wait until we get a return value
            temp = self.__data_base.get_request(request_num)
            time.sleep(0.1) #let other process run
        return temp
    def __str__(self):
        return self.__comand_name
    def get_dto(self, args):
        '''
            Gets data from the data base, then convert it to a dto (Data transfer Object)
            Args:
                args[0] is not used in this function, 
                    it is used by the caller function, it should be the function name
                args[1] is the table name
                args[2] is the start index
                args[3] is the feild in the dto to fetch
                args[4] is optional but if passed it will set the max number of rows per dto to the new value
        '''
        #see if we have a new max row
        try :
            self.__max_rows = int(args[4])
        except :
            pass

        #make the data request to the database.
        request_num = self.__data_base.make_request('get_data_large', [args[1], args[2], self.__max_rows])
        temp = self.__data_base.get_request(request_num)

        #wait for the database to return the data
        while temp is None: #wait until we get a return value
            temp = self.__data_base.get_request(request_num)
            time.sleep(0.1) #let other process run
        #if the database returns a string it is an error
        if isinstance(temp, str) : return temp
        data = temp[args[3]] #sperate data out
        last_db_indx = temp['Table Index'].tail(1).iat[0] #get the last row in the dto
        #make dto
        dto = "<! DOCTYPE html>\n<html>\n<body>\n<h1><strong>dto (data transfer object):</strong></h1>\n"
        dto += f"<h1><strong>Data fetched {args[3]}:</strong></h1>\n<data>"
        for data_point in data:
            dto += (str(data_point) + ",")
        dto += f"</data>\n<lastFetchedIndex>{last_db_indx}</lastFetchedIndex>"
        dto += "</body>\n</html>"
        self.__coms.print_message("DTO returned to requester.")
        return dto