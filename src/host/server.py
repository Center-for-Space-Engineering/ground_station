from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

#local imports (host folder)
from cmd import cmd

#imports from other folders that are not local
import sys
sys.path.insert(0, "..")
from infoHandling.logger import logggerCustom
from infoHandling.messageHandler import messageHandler

# controlEmulo = keySimulator()

log = logggerCustom("logs/coms.txt")
coms = messageHandler()
cmdObj = cmd(coms)


class serverHandler():
    def __init__(self, hostName, serverPort):
        self.__hostName = hostName
        self.__serverPort = serverPort
        
    def run(self):
        webServer = HTTPServer((self.__hostName, self.__serverPort), LitServer)
        log.sendLog("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        coms.printMessage("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort), 2)
        print("Server started http://%s:%s" % (self.__hostName, self.__serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass
        webServer.server_close()
        log.sendLog("Server stopped.")
        print("Server stopped.")
        print("Quit command recived.")
        log.sendLog("Quite command recived.")
        exit(0)


class LitServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("/")
        log.sendLog("Message recived: " + str(path))
        coms.printMessage("Message recived: " + str(path), 3)
        message = cmdObj.parseCmd(path[1:])
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://usu.cse.groundstation.com</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(message, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        log.sendLog("SENT:\n " + message)
        coms.printMessage("SENT:\n " + message, 2)

def test():
    x = serverHandler('144.39.167.206', 5000)
    x.run()

if __name__ == "__main__": 
    test()
