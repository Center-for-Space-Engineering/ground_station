import random
from infoHandling.systemEmuo import systemEmuo as sys 
# from systemEmuo import systemEmuo as sys #for running by its self

from termcolor import colored
import time



class graphicsHandler(sys):
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
    def __init__(self):

        self.__colors = ['red', 'magenta', 'blue', 'green', 'cyan', 'yellow', 'light_cyan', 'white', 'light_magenta', 'light_blue']
        self.__types = ['Error: ', 'Warning: ', 'Log: ', 'Get request: ', 'Data type found: ', 'Sensor connected: ', 'Thread created: ', 'Info: ', 'Command Mapped: ', 'reserved: ']
        self.__messages = [(2, 'Graphics handler started')]
        super().__init__() 

    def test(self):
        self.sendMessage(0, "Error") 
        self.sendMessage(1, "not a real warning") 
        self.sendMessage(2, "nice color ") 
        print("Done queing messages:")
        self.writeMessageLog()

    '''test function'''
    def displayNumber(self, num, message):
        super().print_old_continuos(colored(message,self.__colors[num]), delay=0)

    def writeMessageLog(self):
        for num in self.__messages:
            super().print_old_continuos(colored(self.__types[num[0]],self.__colors[num[0]]) + num[1], delay=0, end='\n')
        self.__messages.clear() #clear the list
    
    def sendMessage(self, num, message):
        self.__messages.append((num, message))
    
   

if __name__ == "__main__": 
    t = cypher()
    t.test()