
import threading
import time
import sys
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom
from infoHandling.messageHandler import messageHandler
from taskHandling.threadWrapper import threadWrapper # running from server
# from threadWrapper import threadWrapper # running alone
from termcolor import colored
import datetime

class taskHandler():
    def __init__(self, coms):
        self.__threads = {}
        self.__coms = coms 
        self.__logger = logggerCustom("logs/taskHandler.txt")
        self.addThread(self.__coms.run, "Coms/Graphics_Handler", self.__coms)


    ''''
    This function takes a taskID (string) and a run function (function to start the thread)
    It then starts a theard and adds it to the dictionary of threads. 
    In side the dictionary it holds the threads. 
    '''
    def addThread(self, runFunction, taskID, wrapper, args = None):
        if(args == None):
            self.__threads[taskID] = (threading.Thread(target=runFunction), wrapper)
            self.__coms.printMessage(f"Thread {taskID} created with no args. ")
            self.__logger.sendLog(f"Thread {taskID} created with no args. ")
        else :
            self.__threads[taskID] = (threading.Thread(target=runFunction, args=args), wrapper)
            self.__coms.printMessage(f"Thread {taskID} created with args {args}. ")
            self.__logger.sendLog(f"Thread {taskID} created with args {args}. ")

    
    '''
    starts all the threads in the threads dictinary
    '''
    def start(self):
        for thread in self.__threads:
            if(self.__threads[thread][1].getStatus() == "NOT STARTED"):
                self.__threads[thread][0].start() #start thread
                self.__coms.printMessage(f"Thread {thread} started. ")
                self.__logger.sendLog(f"Thread {thread} started. ")


    def getThreadStatus(self):
        reports = [] # we need to pass a list of reports so the all get displayed at the same time. 
        for thread in self.__threads:
            if self.__threads[thread][0].is_alive():
                reports.append((thread, "Running", colored(f"[{datetime.datetime.now()}]", 'light_blue')))
                self.__logger.sendLog(f"Thread {thread} is Running. ")
            else :
                if(self.__threads[thread][1].getStatus() == "Complete"):
                    reports.append((thread, "Complete", colored(f"[{datetime.datetime.now()}]", 'light_blue')))
                    self.__logger.sendLog(f"Thread {thread} is Complete. ")
                else :
                    reports.append((thread, "Error", colored(f"[{datetime.datetime.now()}]", 'light_blue')))
                    self.__logger.sendLog(f"Thread {thread} had an Error. ")
        self.__coms.reportThread(reports)

    def killTasks(self):
        for thread in self.__threads:
            self.__threads[thread][1].kill_Task() 
            self.__logger.sendLog(f"Thread {thread} has been killed. ")

    def passRequest(self, thread, request):
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
        with self.__requestLock:
            if(len(request) > 0):
                temp = self.__threads[thread][1].makeRequest(request[0], args = request[1:])
            else :
                temp = self.__threads[thread][1].makeRequest(request[0])
        return temp
            
    def passReturn(self, thread, requestNum):
        '''
            This function is ment to pass the return values form a thread to another thread, without the threads having explicit knowlage of eachother. 
            ARGS:
                thread: The name of the thread as you see it on the gui, or as it is set in main.py
                requestNum: the number that you got from passReequests, this is basically your ticket to map info back and forth.
        '''
        with self.__requestLock:
            temp = self.__threads[thread][1].getRequest(requestNum)
        return temp