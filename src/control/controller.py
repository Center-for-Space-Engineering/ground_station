import json
import requests
from readchar import readkey
from time import sleep
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import sys
sys.path.insert(0, "..")
from logger.logger import logggerCustom

class control:
    def __init__(self, host, port):
        self.__log = logggerCustom("logs/control.txt")
        self.__port = port
        self.__host = host

    def start(self):
        print("Enter WASD, then a duration for the command: \n\tNote: q quits the program and t runs the test function\n")
        running = True
        while running:
            command = readkey()
            if command == 'w': 
                self.callAction("exsample")
            if command == "q":
                self.callAction("getCmd")
            if command == "a":
                self.callAction("exsample/more_args/1/2/3/4")


                          
    def callAction(self, action):
        print("Action: " + action)
        self.__log.sendLog("Action: " + action)
        x = self.sendRequest(action)
        logMessage = "Request sent: "+ str(x)
        self.__log.sendLog(logMessage)

    def sendRequest(self, move):
        self.__log.sendLog("sending...")
        URL = f"http://{self.__host}:{self.__port}/{move}"
        x = requests.get(URL)
        return x

def test():
    hostName = "localhost"
    serverPort = 5000
    pos = 1
    log = logggerCustom("logs/coms.txt")

    try:
        controlObj = control(hostName, str(serverPort))
        controlObj.start()
    except KeyboardInterrupt:
        print("Quit command recived.")
        log.sendLog("Quite command recived.")
        exit(0)
if __name__ == "__main__": 
    test()