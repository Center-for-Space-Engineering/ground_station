#pre built imports
import sqlite3
import pandas as pd
import time
import sys

#custom imports

from database.dataTypesImporter import dataTypeImporter
# from dataTypesImporter import dataTypeImporter # for running locally.
sys.path.insert(0, "..")
from logger.logger import logggerCustom


class dataBaseHandler():
    def __init__(self, dbName = 'database/database_file'):
        #make class matiance vars
        self.__logger = logggerCustom("logs/database_log_file.txt")
        
        #Make data base (bd)
        self.__conn = sqlite3.connect(dbName) 
        self.__c = self.__conn.cursor()

        #make Maps for db creation
        self.__typeMap = { #the point of this dictinary is to map the type names from the dataTypes.dtobj file to 
                           # the sql data base.
            "int" : "INTEGER", 
            "float" : "FLOAT(10)", # NOTE: the (#) is the perscition of the float. 
            "string" : "TEXT",
            "bool" : "BOOLEAN",
            "bigint" : "BIGINT"
        } #  NOTE: this dict makes the .dtobj file syntax match sqlite3 syntax. 

        #find and create the data tables fro the data base
        tableFinder = dataTypeImporter()
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
            except Exception as error:
              print("Error: " + str(error) + " Command send to db: " + dbCommand) #TODO: replace this line with the reporter class when its made
              self.__logger.sendLog("Failed to created table: " + dbCommand + str(error))
        self.__logger.sendLog("Created database:\n" + self.getTablesHTML())   
    '''This func takes in the table_name to insert and a list of data, the list must be in the same order that is defined in the .dtobj file.'''
    def insertData(self, table_name, data):
      dbCommand = f"INSERT INTO {table_name} (time_stamp"
      feilds = self.getfeilds(self.getDataType(table_name)) #get the data type obj and then get the feilds list
      for feild_name in feilds:
        if(feild_name!= "igrnoed feild" and feilds[feild_name][1] != "NONE"): #we dont need feilds for igrnoed data feilds
          dbCommand += ", "
          dbCommand += f"{feild_name}"
      dbCommand +=  ") "
      dbCommand += f"VALUES ({time.time()}"
      for val in data:
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
      except Exception as error:
              print("Error: " + str(error) + " Command send to db: " + dbCommand) #TODO: replace this line with the reporter class when its made
              raise Exception
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
    def getDataType(self, table_name):
       return self.__tables[table_name]
    def getfeilds(self, dataType):
       return dataType.getFields()
    def getfeildsList(self, dataType):
       feilds = dataType.getFields()
       feildsList = []
       for feild in feilds:
          if(feilds[feild][1] != "NONE"): #dont add any feilds that are not in the data base
            feildsList.append(feild)
            
       return feildsList
    def getData(self, table_name, start_time):
       message = f"<h1>{table_name}: "
       try :
        #from and run db command
        dbCommand = f"SELECT * FROM {table_name} WHERE time_stamp >= {str(start_time)} ORDER BY time_stamp"
        self.__c.execute(dbCommand)
        self.__logger.sendLog("Query command recived: "  + dbCommand)          
       except Exception as error:
        print("Error: " + str(error) + " Command send to db: " + dbCommand) #TODO: replace this line with the reporter class when its made
        return "<p> Error getting data </p>"
       #get cols 
       cols = ["Time Stored "] # add time stamp to the cols lis
       cols += self.getfeildsList(self.getDataType(table_name))

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

if __name__ == "__main__":
    x = dataBaseHandler()
    print(x.getTablesHTML())

    for f in x.getTables_strLIST():
       print(x.getDataType(f))
      
    for f in x.getTables_strLIST():
       print(x.getfeilds(x.getDataType(f)))


    startT = time.time()
    x.insertData("exsample", [10, 1.1, "hello world"])  
    x.insertData("exsample", [10, 1.1, "hello world2"])  
    x.insertData("exsample", [10, 1.1, "hello world3"])  

    print(x.getData("exsample", startT))
