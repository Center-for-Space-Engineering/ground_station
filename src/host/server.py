from flask import Flask, render_template, request

#local imports (host folder)
from cmd_inter import cmd_inter


#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom
from logging_system_display_python_api.messageHandler import messageHandler
from threading_python_api.threadWrapper import threadWrapper


log = loggerCustom("logs/coms.txt")

coms_local = messageHandler()
cmd_local = cmd_inter(coms_local)



class serverHandler(threadWrapper):
    def __init__(self, hostName, serverPort):
        self.__function_dict = {
            'run' : self.run,
            'kill_Task' : self.kill_Task,
            'getComs' : self.getComs,
            'setHandlers' : self.setHandlers
        }
        super().__init__(self.__function_dict)
        self.__hostName = hostName
        self.__serverPort = serverPort
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        path = self.path.split("/")
        log.send_log("Message recived: " + str(path))
        coms_local.print_message("Message recived: " + str(path), 3)
        message = cmd_local.parse_cmd(path[1:])
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://usu.cse.groundstation.com</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(message, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        log.send_log("SENT:\n " + message)
        coms_local.print_message("Server responed ", 2)

    def index(self):
        return render_template('index.html')

    def process_text(self):
        user_text = request.form['user_text']
        # You can process the user's text here
        return f'You entered: {user_text}'
    def run(self):
        log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        coms_local.send_message_prement("Server started http://%s:%s" % (self.__hostName, self.__serverPort), 2)
        super().set_status("Running")
        self.app.run(debug=True)
    def kill_Task(self):
        super().kill_Task()
        self.__webServer.server_close()
        log.send_log("Server stopped.")
        log.send_log("Quite command recived.")   

    def getComs(self):
        return coms_local  

    def setHandlers(self, db):
        cmd_local.collect_commands(db)    

if __name__ == '__main__':
    my_app = serverHandler()
    my_app.run()

