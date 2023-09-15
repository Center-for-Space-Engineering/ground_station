import random
import datetime
from infoHandling.systemEmuo import systemEmuo as sys 
# from systemEmuo import systemEmuo as sys #for running by its self

from termcolor import colored




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
    def __init__(self, mesDisp = 5, byteDisp = 15, byteDiv = 100):

        self.__colors = ['red', 'magenta', 'blue', 'green', 'cyan', 'yellow', 'light_cyan', 'white', 'light_magenta', 'light_blue']
        self.__types = ['Error: ', 'Warning: ', 'Log: ', 'Get request: ', 'Data type found: ', 'Sensor connected: ', 'Thread created: ', 'Info: ', 'Command Mapped: ', 'reserved: ']
        self.__messages = [(2, colored(f"[{datetime.datetime.now()}]", 'light_blue') + '\tGraphics handler started')]
        self.__threaedsStatus = []
        self.__messagsDisplayed = mesDisp
        self.__byteReport = []
        self.__byteDisp = byteDisp
        self.__byteDiv = byteDiv
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

    def writeMessageLog(self, clearList = False):
        super().print_old_continuos(colored('Loggs report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for num in self.__messages:
            super().print_old_continuos(colored(self.__types[num[0]],self.__colors[num[0]]) + num[1], delay=0, end='\n')
    
    def sendMessage(self, num, message):
        self.__messages.append((num, colored(f"[{datetime.datetime.now()}]", 'light_blue') + "\t" + message))
        if len(self.__messages) >= self.__messagsDisplayed : # this basically makes it a FIFO queue for messaging
            self.__messages.remove(self.__messages[0])

    def reportThread(self,report):
        self.__threaedsStatus = report

    def writeThreadReport(self):
        super().print_old_continuos(colored('Thread report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for report in self.__threaedsStatus:
            if report[1] == "Running":
                super().print_old_continuos(f"Time: {report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[3]) + "\t", delay=0)
            elif report[1] == "Error":
                super().print_old_continuos(f"{report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[0])+ "\t", delay=0)
            else :
                super().print_old_continuos(f"{report[2]} Thread {report[0]}: " + colored(report[1],self.__colors[2])+ "\t", delay=0)
        if(len(self.__threaedsStatus) != 0):
            self.__threaedsStatus.clear()
            print() # print new line

    def writeByteReport(self):
        super().print_old_continuos(colored('Byte report: ',self.__colors[3]) + "\t", delay=0, end = '\n')
        for  report in self.__byteReport:
            super().print_old_continuos(report, end='\n', delay=0)
        super().print_old_continuos(colored(f"KEY : ", 'light_blue') + colored((u'\u25a0'), 'magenta') + f"= {self.__byteDiv} bytes.", end='\n', delay=0)

    def reportByte(self, numbytes):
        bytesOriganal = numbytes
        numbytes //= self.__byteDiv
        self.__byteReport.append(colored(f"Bytes received at: [{datetime.datetime.now()}]", 'light_blue') + " |" + colored((u'\u25a0' * numbytes) + f"({bytesOriganal})", 'magenta'))
        if len(self.__byteReport) >= self.__byteDisp : # this basically makes it a FIFO queue for messaging
            self.__byteReport.remove(self.__byteReport[0])



            