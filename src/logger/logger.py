from datetime import datetime

class logggerCustom():
    def __init__(self, file):
        self.__file = open(file, "w+")

    def sendLog(self, text):
        self.__file.write(str(datetime.now()) + ": " + text + "\n")
        self.__file.flush()