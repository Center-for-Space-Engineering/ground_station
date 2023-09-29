#pre built imports
import sqlite3
import pandas as pd
import time
import sys

#custom imports

from database.dataTypesImporter import dataTypeImporter
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom
from host.taskHandling.threadWrapper import threadWrapper 


class dataBaseHandler(threadWrapper):
    '''
      calling the init function will create the basics for the class and then add the createDataBase to the queue for task to be done,
      when you start the run function. To be clear this class should work just fine in a single thread, just dont call run, makeRequest and getRequest.
      However, when running multi thread, the user must call run FIRST, then they can use the make request and get request to interface with the class. 
      NOTE: When running multi threaded, only the __init__, makeRequest, getRequest, and run function should be called by out side classes and threads. 
    '''
    def __init__(self, coms, dbName = 'database/database_file'):
        #make class matiance vars
        self.__logger = logggerCustom("logs/database_log_file.txt")
        self.__coms = coms
        self.__dbName = dbName

        #make Maps for db creation
        self.__typeMap = { #the point of this dictinary is to map the type names from the dataTypes.dtobj file to 
                           # the sql data base.
            "int" : "INTEGER", 
            "float" : "FLOAT(10)", # NOTE: the (#) is the perscition of the float. 
            "string" : "TEXT",
            "bool" : "BOOLEAN",
            "bigint" : "BIGINT"
        } #  NOTE: this dict makes the .dtobj file syntax match sqlite3 syntax.

        #Start the threaed wrapper for  the process
        super().__init__()

        #send request to parent class to make the data base
        super().makeRequest('createDataBase', [])

    
    def createDataBase(self):
        '''
          Makes the data base.
          NOTE: if you want to change the name of the data base then that needs to be done when you make the class
        '''
        #Make data base (bd)
        self.__conn = sqlite3.connect(self.__dbName) 
        self.__c = self.__conn.cursor()

       #find and create the data tables fro the data base
        tableFinder = dataTypeImporter(self.__coms)
        tableFinder.pasreDataTypes()
        self.__tables = tableFinder.getDataTypes() #this varible will be used for creatig/accessing/parsing the data. 
                                                   #  In other words its super imporatant.  

        #create a table in the data bas for each data type
        for table in self.__tables:
            tableName = self.__tables[table].getDataGroup()
            tableFeilds = self.__tables[table].getFields()
            dbCommand = f"CREATE TABLE IF NOT EXISTS {tableName} ("
            dbCommand += f"[time_stamp] BIGINT PRIMARY KEY" #this line is add as a way to index the data base

            #iter for every feild in this data group. The feilds come from the dataTypes.dtobj file. 
            for feild_name in tableFeilds:
                # NOTE: in the dataTypes class the feilds dict maps to a tuple of (bits, convert_type) the bits is not used here
                #   because it is for collecting the data. The convert typ is, thus we want to access feild 1 of the tuple. In 
                #   addition that is fed into the self.__typeMap to convert it to SQL syntax
                if(feild_name!= "igrnoed feild" and tableFeilds[feild_name][1] != "NONE"): #we dont need feilds for igrnoed data feilds
                  dbCommand += ", " # adding the ", " here means we don't have an extra one on the last line. 
                  dbCommand += f"[{feild_name}] {self.__typeMap[tableFeilds[feild_name][1]]}" 
            dbCommand += ")"

            #try to make the table in the data base
            try :  
              self.__c.execute(dbCommand)
              self.__logger.sendLog("Created table: " + dbCommand)
              self.__coms.printMessage("Created table: " + dbCommand, 2)
            except Exception as error:
              self.__coms.printMessage(str(error) + " Command send to db: " + dbCommand, 0) 
              self.__logger.sendLog("Failed to created table: " + dbCommand + str(error))
              self.__coms.printMessage("Failed to created table: " + dbCommand + str(error), 0)
        self.__logger.sendLog("Created database:\n" + self.getTablesHTML())   
        self.__coms.printMessage("Created database", 2)   
    
    def insertData(self, args):
      '''
      This func takes in the table_name to insert and a list of data, the list must be in the same order that is defined in the .dtobj file.
      args is a list were the fist index is the table name and the second is the data
      '''
      dbCommand = f"INSERT INTO {args[0]} (time_stamp" #args[0] is the table name
      feilds = self.getfeilds([self.getDataType([args[0]])]) #get the data type obj and then get the feilds list
      for feild_name in feilds:
        if(feild_name!= "igrnoed feild" and feilds[feild_name][1] != "NONE"): #we dont need feilds for igrnoed data feilds
          dbCommand += ", "
          dbCommand += f"{feild_name}"
      dbCommand +=  ") "
      dbCommand += f"VALUES ({time.time()}"
      for val in args[1]: #args[1] is the data
         dbCommand += ", "
         # for sql str has a special format so we need the if statment
         if(type(val) != str):
          dbCommand += f"{val}"
         else :
          dbCommand += f"'{val}'"
            
      dbCommand += ")"
      try:
        self.__c.execute(dbCommand)
        self.__conn.commit()
        self.__logger.sendLog("INSERT COMMAND: " + dbCommand)
        self.__coms.printMessage("INSERT COMMAND: " + dbCommand, 2)
      except Exception as error:
              self.__coms(str(error) + " Command send to db: " + dbCommand, 0) 
              self.__logger.sendLog(str(error) + " Command send to db: " + dbCommand) 
              raise Exception
      return "Complete"
    #some  useful getters 
    def getTablesHTML(self):
        message = "<! DOCTYPE html>\n<html>\n<body>\n<h1>DataBase Tables</h1>"
        for table in self.__tables:
            message +=f"<p><strong>Table:</strong> {table}</p>\n"
        message += "</body>\n</html>"
        return message
    def getTables_strLIST(self):
      strList = []
      for table in self.__tables:
         strList.append(table)
      return strList 
    
    def getDataType(self, args):
       '''
        args is a list where the fist index is the table name
        '''
       return self.__tables[args[0]] # the arg is the table name to find
    
    def getfeilds(self, args):
       '''
        args is a list where the fist index is a data type obj 
        '''
       return args[0].getFields() # the args is a data type obj in the first index of the list
    
    def getfeildsList(self, args):
       '''
        args is a list where the fist index is a data type obj 
        '''
       feilds = args[0].getFields()# the args is a data type obj in the first index of the list
       feildsList = []
       for feild in feilds:
          if(feilds[feild][1] != "NONE"): #dont add any feilds that are not in the data base
            feildsList.append(feild)
            
       return feildsList
    
    def getData(self, args):
       '''
        args is a list where the fist index is the table name and the second is the start time for collecting the data
        '''
       message = f"<h1>{args[0]}: " # args[0] is the table name
       try :
        #from and run db command
        dbCommand = f"SELECT * FROM {args[0]} WHERE time_stamp >= {str(args[1])} ORDER BY time_stamp" #args 1 is the time stamp
        self.__c.execute(dbCommand)
        self.__logger.sendLog("Query command recived: "  + dbCommand)          
        self.__coms.printMessage("Query command recived: "  + dbCommand, 2)          
       except Exception as error:
        self.__coms.printMessage(str(error) + " Command send to db: " + dbCommand, 0)
        self.__logger.sendLog(str(error) + " Command send to db: " + dbCommand)
        return "<p> Error getting data </p>"
       #get cols 
       cols = ["Time Stored "] # add time stamp to the cols lis
       cols += self.getfeildsList([self.getDataType([args[0]])])

       message += f"{cols}</h1> "

       #fetch and convert the data into a pandas data frame. 
       data = pd.DataFrame(self.__c.fetchall(), columns=cols)
       
       for x in range(len(data)):
         message += "<p>"
         for i in range(len(cols) - 1): #itrate for all but last col
            message += f"{data.iloc[x,i]}," 
         message += f"{data.iloc[x,len(cols) - 1]}"# add last col with out , 
         message += "</p>"

       self.__logger.sendLog("data collected: " + message)
       return message    