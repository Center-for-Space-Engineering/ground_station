from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

#local imports (host folder)
from cmd import cmd

#imports from other folders that are not local
import sys
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom
from infoHandling.messageHandler import messageHandler
from host.taskHandling.threadWrapper import threadWrapper # running from server

log = logggerCustom("logs/coms.txt")

coms_local = None
cmd_local = None  

class serverHandler(threadWrapper):
    def __init__(self, hostName, serverPort, coms):
        super().__init__()
        self.__hostName = hostName
        self.__serverPort = serverPort
        self.__coms = coms
        self.__cmd = cmd(self.__coms)

        
    def run(self):
        webServer = HTTPServer((self.__hostName, self.__serverPort), LitServer)
        log.sendLog("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        self.__coms.sendMessagePrement("Server started http://%s:%s" % (self.__hostName, self.__serverPort), 2)

        try:
            super().setStatus("Running")
            webServer.serve_forever()
        except KeyboardInterrupt:
            super().kill_Task()
        webServer.server_close()
        log.sendLog("Server stopped.")
        log.sendLog("Quite command recived.")     


class LitServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("/")
        log.sendLog("Message recived: " + str(path))
        coms_local.printMessage("Message recived: " + str(path), 3)
        message = cmd_local.parseCmd(path[1:])
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://usu.cse.groundstation.com</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(message, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        log.sendLog("SENT:\n " + message)
        coms_local.printMessage("SENT:\n " + message, 2)

def test():
    x = serverHandler('144.39.167.206', 5000)
    x.run()

if __name__ == "__main__": 
    test()
