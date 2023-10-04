import time
import threading
import random
import sys

class threadWrapper():
    def __init__(self, coms = None):
        self.__status = "NOT STARTED"
        self.__RUNNING = True
        self.__coms = coms
        self.__lockStatus = threading.Lock()
        self.__lockRunning = threading.Lock()
        self.__request = []
        # this is how we handle task in this class, the format is a list [func name, list of args, bool to mark when its been served, returned time, request num]
        self.__requestLock = threading.Lock()
        # this is how we keep track of requsts
        self.__requetNum = 0
        self.__completedRequestes = {}


    def test1(self):
        self.__status = "Running"
        for i in range(5):
            if self.__coms != None:
                self.__coms.printMessage("Test 1 working...")
                time.sleep(1)
        if self.__coms != None:
            self.__coms.printMessage("Test 1 complete")
        self.__status = "Complete"

    def test2(self):
        self.__status = "Running"
        for i in range(40):
            if self.__coms != None:
                # self.__coms.printMessage("Test 2 dummy bytres received...")
                self.__coms.reportBytes(random.randint(1, 11) * 1000)
                time.sleep(0.25)
        if self.__coms != None:
            self.__coms.printMessage("Test 2 complete")
        self.__status = "Complete"

    def getStatus(self):
        with self.__lockStatus:
            return self.__status
    def setStatus(self, status):
        with self.__lockStatus:
            self.__status = status

    def getRunning(self):
        with self.__lockRunning:
            return self.__RUNNING
    def kill_Task(self):
        with self.__lockRunning:
            self.__RUNNING = False
    
    def makeRequest(self, type, args=[]):
        '''
            Make a request to to the THREAD, it then returns the task number that you can pass to get Request to see if your task has been completed. 
        '''
        with self.__requestLock:
            self.__requetNum += 1
            self.__request.append([type, args, False, None, self.__requetNum])
            temp = self.__requetNum # set a local var to the reqest num so we can relase the mutex
        return temp
    
    
    def getRequest(self, requestNum):
        '''
            Check to see if the task has been complete, if it returns None then it has not been completed. 
        '''
        with self.__requestLock:
            try :
                temp = self.__completedRequestes[requestNum] #this check to see if it is complete or not, because if it is not it just fails and goes to the except block. 
                del self.__completedRequestes[requestNum] # delete the completed task to save space
                return temp
            except :
                return None 
    
    def getNextRequest(self):
        with self.__requestLock: 
            if(len(self.__request) > 0):
                temp = self.__request.pop(0) # set a local var to the reqest num so we can relase the mutex
            else :
                temp = None
        return temp
    
    def completRequest(self, key, returnVal):
        self.__completedRequestes[key] = returnVal

   
    def run(self):
        '''
            This function is for multi threading purpose. It works by using a FIFO queue to process Task assigned to it by other threads.
        '''
        self.setStatus("Running")
        sleep = False
        while(self.getRunning()):
            request = self.getNextRequest()
            # check to see if there is a request
            if(request != None):
                if(len(request[1]) > 0): request[3] = eval("self." + request[0])(request[1])
                else : request[3] = eval("self." + request[0])()
                self.completRequest(request[4], request[3])
            else :
                sleep = True      
            if(sleep): #sleep if no task are needed. 
                time.sleep(0.1)
                sleep = False  
