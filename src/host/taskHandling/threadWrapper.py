import time

class threadWrapper():
    def __init__(self):
        self.__status = "NOT STARTED"
        self.__RUNNING = True


    def test1(self):
        self.__status = "Running"
        time.sleep(10)
        self.__status = "Complete"

    def test2(self):
        self.__status = "Running"
        time.sleep(5)
        self.__status = "Complete"

    def getStatus(self):
        return self.__status
    def setStatus(self, status):
        self.__status = status

    def getRunning(self):
        return self.__RUNNING
    def kill_Task(self):
        self.__RUNNING = False