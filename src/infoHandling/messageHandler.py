from infoHandling.graphicsHandler import graphicsHandler
import threading
import time
from host.taskHandling.threadWrapper import threadWrapper # running from server
# from threadWrapper import threadWrapper # running as test for taskHandling
'''
There should only be ONE of these classes! It is meant to have shared access and has threading protection.
'''
class messageHandler(threadWrapper):
    def __init__(self):
        super().__init__()
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
    def sendMessagePrement(self, message, typeM=2):
        with self.__graphicsLock :
            self.__graphics.sendMessagePrement(typeM, message)
    def printMessage(self, message, typeM=2):
        with self.__graphicsLock :
            self.__graphics.sendMessage(typeM, message)
    def reportThread(self,report):
        with self.__graphicsLock :
            self.__graphics.reportThread(report)
    def reportBytes(self, byteCount):
        with self.__graphicsLock :
            self.__graphics.reportByte(byteCount)

    def flush(self):
        with self.__graphicsLock :
            self.__graphics.writeMessageLog()
    def flushPrem(self):
        with self.__graphicsLock :
            self.__graphics.writeMessagePrementLog()
    def flushThreadReport(self):
        with self.__graphicsLock :
            self.__graphics.writeThreadReport()
    def flushBytes(self):
        with self.__graphicsLock :
            self.__graphics.writeByteReport()

    def run(self, refresh = 0.5): #Note if things start getting wired it is cause the refresh rate is too fast for the screen to print it.
        super().setStatus("Running")
        while (super().getRunning()):
            print("\033c", end='') #clears the terminal
            self.flushPrem()
            print()
            self.flushThreadReport()
            print()
            self.flush()
            print()
            self.flushBytes()
            time.sleep(refresh)    