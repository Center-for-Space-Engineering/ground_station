import sys
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom


class dataType():
    def __init__(self, dataGroup, coms):
        self.__feilds = {} #this dict contains all the data types that will be saved to the data base
        self.__bitMap = []# this list contains info on how to collect the bits from the bit stream. 
        self.__convertMap = {} #this dict contatins types that need to be mapped together. The MSB is the key.  
        self.__dataGroup = dataGroup
        self.__logger = logggerCustom(f"logs/dataType_{self.__dataGroup}.txt") 
        self.__coms = coms 
    def addFeild(self, name, bits, convert):
        self.__feilds[name] = (bits, convert)
        self.__logger.sendLog(f"{self.__dataGroup} added a feild: {name} : bit length {bits} > converter type {convert}")
        self.addBitMap(name, bits) # add the type to the bit map     
    def addBitMap(self, name, bits):    
        self.__bitMap.append((name, bits))
        self.__logger.sendLog(f"{self.__dataGroup} added a bit map step: {name} : bit length {bits}")
    def addConverMap(self, type1, type2):
        self.__convertMap[type1] = type2
        self.__logger.sendLog(f"{self.__dataGroup} added a discontiunous data type: {type1} < {type2}")
    def __str__(self):
        message = f"<! DOCTYPE html>\n<html>\n<body>\n<h1><strong>Data Type:</strong> {self.__dataGroup}</h1>\n"
        message += f"<h1><strong>Feilds in database:</strong></h1>\n"

        for field in self.__feilds:
            if(self.__feilds[field][1] != "NONE"):
                message +=f"<p>&emsp;<strong>Feild:</strong> {field} <strong>Bit lenght:</strong> {self.__feilds[field][0]} <strong>Converter type:</strong> {self.__feilds[field][1]} </p>\n"
        message += f"<h2><strong>Bit Map:</strong></h2>\n"
        for map in self.__bitMap:
            message +=f"<p>&emsp;<strong>Feild:</strong> {map[0]} <strong>Bit lenght:</strong> {map[1]} </p>\n"
        message += f"<h3><strong>Discontinuous Mappings:</strong></h3>\n"
        for typeC in self.__convertMap:
            message +=f"<p>&emsp;<strong>Feild MSB:</strong> {typeC} <strong>Feild LSB</strong> {self.__convertMap[typeC]} </p>\n"
        message += "</body>\n</html>"
        return message
    def get_fields(self):
        return self.__feilds  
    def get_data_group(self):
        return self.__dataGroup
        