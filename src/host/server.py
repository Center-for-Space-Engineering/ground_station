'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
from flask import Flask, render_template, request , send_from_directory
from threading import Lock
#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom
from threading_python_api.threadWrapper import threadWrapper

class serverHandler(threadWrapper):
    def __init__(self, hostName, serverPort, coms, cmd):
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs 
            'run' : self.run,
            'kill_Task' : self.kill_Task,
            'getComs' : self.getComs,
            'write_message_log' : self.write_message_log,
        }
        super().__init__(self.__function_dict)

        self.__hostName = hostName
        self.__serverPort = serverPort

        #these class are used to comminicate with the reset of the cse code
        self.__coms = coms
        self.__cmd = cmd
        self.__log = loggerCustom("logs/coms.txt")

        #data structs for storing messages
        self.__messages = []
        #threading saftey 
        self.__message_lock = Lock()

        cmd_dict = self.__cmd.get_command_dict()
        print(cmd_dict)
        for var in cmd_dict:
            print(f"{var}  maps to {cmd_dict[var]}")

        #set up server
        self.app = Flask(__name__)
        self.setup_routes()

        
    def setup_routes(self):
        self.app.route('/')(self.status_report)
        self.app.route('/open_data_stream')(self.open_data_stream)
        self.app.route('/Sensor')(self.open_sensor)
        self.app.route('/Command')(self.command)
        self.app.route('/page_manigure.js')(self.serve_page_manigure)
        
        # path = self.path.split("/")
        # self.__log.send_log("Message recived: " + str(path))
        # self.__coms.print_message("Message recived: " + str(path), 3)
        # message = self.__cmd.parse_cmd(path[1:])
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # self.wfile.write(bytes("<html><head><title>https://usu.cse.spacecraftemulator.com</title></head>", "utf-8"))
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        # self.wfile.write(bytes("<body>", "utf-8"))
        # self.wfile.write(bytes(message, "utf-8"))
        # self.wfile.write(bytes("</body></html>", "utf-8"))
        # self.__log.send_log("SENT:\n " + message)
        # self.__coms.print_message("Server responed ", 2)
    def serve_page_manigure(self):
        return send_from_directory('source', 'page_manigure.js')
    def status_report(self):
        return render_template('status_report.html')
    def run(self):
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        self.__coms.send_message_prement("Server started http://%s:%s" % (self.__hostName, self.__serverPort), 2)
        super().set_status("Running")
        self.app.run(debug=False, host=self.__hostName, port=self.__serverPort)
    def run_serve_coms(self):
        super().run()
    def kill_Task(self):
        super().kill_Task()
        self.__webServer.server_close()
        self.__log.send_log("Server stopped.")
        self.__log.send_log("Quite command recived.")
    def getComs(self):
        return self.__coms
    def setHandlers(self, db):
        self.__cmd.collect_commands(db)    
    def open_data_stream(self):
        return render_template('data_stream.html')
    def open_sensor(self):
        return render_template('sensor.html')
    def command(self):
        return render_template('Command.html')
    def write_message_log(self, message):
        with self.__message_lock:
            self.__messages = message
            print (self.__messages)
