
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




if __name__ == "__main__":
    coms = messageHandler()
    x = taskHandler(coms)
    y = threadWrapper(coms)
    z = threadWrapper(coms)

    x.addThread(y.test1, 'task 1', y)
    x.addThread(z.test2, 'task2', z)

    x.start()
    for i in range (15):
        x.getThreadStatus()
        time.sleep(0.5)

    x.getThreadStatus()
    x.killTasks()
        
    