import sys
from database.dataType import dataType #this import is to run this file from the server. 
# from dataType import dataType  #if you want to just run this file, NOTE: run this from the host folder. command: python3 database/dataTypesImporter.py 
from colorama import Fore

sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom


#TODO: add try except statements 


class dataTypeImporter():
    def __init__(self, coms):
        self.__dataTypes = {}
        self.__logger = logggerCustom("logs/dataTypeImporter.txt")
        self.__coms = coms
        try:
            self.__dataFile = open("database/dataTypes.dtobj")
            self.__logger.sendLog("data types file found.")
            self.__coms.printMessage("data types file found.", 2)
        except:
            self.__coms(" No database/dataTypes.dtobj file detected!", 0)   
            self.__logger.sendLog(" No database/dataTypes.dtobj file detected!")   
    def pasreDataTypes(self):
        currentDataGroup = ""
        for line in self.__dataFile:
            if "//" in line:
                pass
            else :
                if '    ' in line:
                    if('@' in line): # this is a discontinuos type
                        processed = line.replace('  ', "")
                        processed = processed.replace("\n", "")
                        processed = processed.split(":")
                        temp = processed[1].split(">")
                        processed[1] = temp[0]
                        feild = temp[1].split("@")
                        processed.append(feild[0])
                        disCon = feild[1].split('<')

                        self.__logger.sendLog(f"Decoded type for group {currentDataGroup} : feild name {processed[0].strip()}, bit length {processed[1].strip()}, convertion typ {processed[2].strip()}")
                        self.__dataTypes[currentDataGroup].addFeild(processed[0].strip(), processed[1].strip(), processed[2].strip())
                        #because this is a discontinuos type we need to add it to the list of discontinuos types
                        self.__dataTypes[currentDataGroup].addConverMap(disCon[0], disCon[1])
                    else :
                        processed = line.replace('  ', "")
                        processed = processed.replace("\n", "")
                        processed = processed.split(":")
                        temp = processed[1].split(">")
                        processed[1] = temp[0]
                        if (len(temp) > 1):
                            processed.append(temp[1])
                        else :
                            processed.append("NONE")
                        
                        self.__logger.sendLog(f"Decoded type for group {currentDataGroup} : feild name {processed[0].strip()}, bit length {processed[1].strip()}, convertion typ {processed[2].strip()}")
                        self.__dataTypes[currentDataGroup].addFeild(processed[0].strip(), processed[1].strip(), processed[2].strip())
                elif "#" in line:
                    processed = line.replace('  ', "")
                    processed = processed.replace("\n", "")
                    processed = processed.split(":")
                    self.__logger.sendLog(f"Decoded type for group {currentDataGroup} : feild name ignored bits, bit length {processed[1]}")
                    self.__dataTypes[currentDataGroup].addFeild("igrnoed feild", processed[1].strip(), "NONE")
                else :
                    processed = line.replace('  ', "")
                    processed = processed.replace("\n", "")
                    currentDataGroup = processed.strip()
                    self.__dataTypes[currentDataGroup] = dataType(currentDataGroup, self.__coms)
                    self.__logger.sendLog(f"Created data group {currentDataGroup}")

        self.__logger.sendLog(f"Created data types:\n {self}")   
        self.__coms.printMessage(f"Created data types.", 2)   
    def get_data_types(self):
        return self.__dataTypes
    def __str__(self):
        message = ""
        for group in self.__dataTypes:
            message += str(self.__dataTypes[group]) + "\n"

        return message
        

if __name__ == "__main__":
    x = dataTypeImporter()
    x.pasreDataTypes()
    print(x)



