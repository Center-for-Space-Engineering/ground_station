from infoHandling.graphicsHandler import graphicsHandler
import threading
import time
from host.taskHandling.threadWrapper import threadWrapper 

'''
There should only be ONE of these classes! It is meant to have shared access and has threading protection.
'''
class messageHandler(threadWrapper):
    '''
        This class is the mail man of our code. Any message that needs to be sent to other threads, needs to go through here.
        This class is in charge of send info to the graphics handler (systemEmuo) witch displays it to the user.
        It also is in charge of sending request to unknow threads. 
        For example:
            The systemEmuo does need to know about the matlab_disbacter, but it does want info from it. So it will send a request
                through this class to get that info.
            A data base handler should use this class, because it is handling the data base class it should have direct knowlage 
                of the database. 

            It is completely possible to handle either example with or with out this class, however to maintain a clear code struct 
                here is the rule.

            RULE: IF a class is directly controling another class (A.K.A Do this thing now), do not use the coms class for sending request.
                  If a class is requesting information, or send indrect reqests (A.K.A process this when you have time) it should go through this class.
    '''
    def __init__(self, threadHandler = None):
        super().__init__()
        self.__graphics = graphicsHandler(coms=self)
        self.__graphicsLock = threading.Lock()
        self.__threadHandlerLock = threading.Lock()
        self.__threadHandler = threadHandler

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
    def clearDisp(self):
        with self.__graphicsLock :
            self.__graphics.clear()

    def run(self, refresh = 0.5): #Note if things start getting wired it is cause the refresh rate is too fast for the screen to print it.
        pass
        super().setStatus("Running")
        while (super().getRunning()):
            self.clearDisp()
            self.flushPrem()
            self.flushThreadReport()
            self.flush()
            self.flushBytes()
            time.sleep(refresh)    

    def getSystemEmuo(self):
        return self.__graphics
    
    def sendRequest(self, thread, request):
        '''
            This function is ment to pass information to other threads with out the two threads knowing about each other.
            Bassically the requester say I want to talk to thread x and here is my request. This funct then pass on that requeset. 
            NOTE: threads go by the same name that you see on the display, NOT their class name. This is ment to be easier for the user,
            as they could run the code and see the name they need to send a request to.

            ARGS: 
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                request: index 0 is the function name, 
                        index 1 to the end is the args for that function.
                NOTE: even if  you are only passing one thing it needs to be a list! 
                    EX: ['funcName']
        '''
        #NOTE: We still need a mutex lock here, even thought the taskHandler is doing locking as well, the taskHandler
        #   pointer (self.__taskHandler) is a varible that needs to be protected.
        with self.__threadHandlerLock:
            temp = self.__threadHandler.passRequest(thread, request)
        return temp
    
    def getReturn(self, thread, requestNum):
        '''
            This function is ment to pass the return values form a thread to another thread, without the threads having explicit knowlage of eachother. 
            ARGS:
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                requestNum: the number that you got from passReequests, this is basically your ticket to map info back and forth.
        '''
        with self.__graphicsLock:
            temp = self.__threadHandler.passReturn(thread, requestNum)
        return temp