import time
import threading
import random

class threadWrapper():
    def __init__(self, coms = None):
        self.__status = "NOT STARTED"
        self.__RUNNING = True
        self.__coms = coms
        self.__lockStatus = threading.Lock()
        self.__lockRunning = threading.Lock()


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
                self.__coms.printMessage("Test 2 dummy bytres received...")
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