from datetime import datetime

'''This class is meant to handel INDIVIDUAL LOGGING for other classes. It has no threading protection. In other words 
classes should not share access to one of these objects. '''
class logggerCustom():
    def __init__(self, file):
        self.__file = open(file, "w+")

    def sendLog(self, text):
        self.__file.write(str(datetime.now()) + ": " + text + "\n")
        self.__file.flush()
