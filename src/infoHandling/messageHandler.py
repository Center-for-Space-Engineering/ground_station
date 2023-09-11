from infoHandling.graphicsHandler import graphicsHandler
import threading

'''There should only be ONE of these classes! It is meant to have shared access and has threading protection.'''
class messageHandler():
    def __init__(self):
        self.__graphics = graphicsHandler()
        self.__graphicsLock = threading.Lock()

    '''
        0  : 'red' : Error
        1  : 'magenta' : warning
        2  : 'blue' : Log 
        3  : 'green' : get request
        4  : 'cyan' : data type found
        5  : 'yellow' : Sensor connected
        6  : 'light_cyan' : thread created
        7  : 'white' : info
        8  : 'light_magenta' : Command Mapped
        9  : 'light_blue' : reserved
    '''
    def printMessage(self, message, typeM=2):
        with self.__graphicsLock :
            self.__graphics.sendMessage(typeM, message)
            self.flushMessages()

    def flushMessages(self):
        self.__graphics.writeMessageLog()