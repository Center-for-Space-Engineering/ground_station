'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
import logging
from flask import Flask, render_template, request , send_from_directory
from threading import Lock
#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom
from threading_python_api.threadWrapper import threadWrapper
from server_message_handler import serverMessageHandler

class serverHandler(threadWrapper):
    def __init__(self, hostName, serverPort, coms, cmd, messageHandler:serverMessageHandler, messageHandlerName:str):
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs 
            'run' : self.run,
            'kill_Task' : self.kill_Task,
            'getComs' : self.getComs,
        }
        super().__init__(self.__function_dict)

        #set up server coms 
        self.__message_handler = messageHandler
        self.__message_handler_name = messageHandlerName


        self.__hostName = hostName
        self.__serverPort = serverPort

        #these class are used to comminicate with the reset of the cse code
        self.__coms = coms
        self.__cmd = cmd
        self.__log = loggerCustom("logs/server_loggs.txt")

        #get the possible commands to run
        cmd_dict = self.__cmd.get_command_dict()

        #set up server
        # Disable print statements by setting the logging level to ERROR
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.ERROR)

        # set up the app
        self.app = Flask(__name__)
        self.setup_routes()

        
    def setup_routes(self):
        #Paths that the server will need 
        self.app.route('/')(self.status_report)
        self.app.route('/open_data_stream')(self.open_data_stream)
        self.app.route('/Sensor')(self.open_sensor)
        self.app.route('/Command')(self.command)
        self.app.route('/page_manigure.js')(self.serve_page_manigure)

        #the paths caught by this will connect to the users commands they add
        self.app.add_url_rule('/<path:unknown_path>', 'handle_unknown_path', self.handle_unknown_path)

    def handle_unknown_path(self, unknown_path):
        path = unknown_path.split("/")
        print(path)
        self.__log.send_log("Message recived: " + str(path))
        self.__coms.print_message("Message recived: " + str(path), 3)
        message = self.__cmd.parse_cmd(path)
        print(message)
        # self.__log.send_log("SENT:\n " + message)
        # self.__coms.print_message("Server responed ", 2)
        return f'Unknown Path: {unknown_path}'
    def serve_page_manigure(self):
        return send_from_directory('source', 'page_manigure.js')
    def status_report(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_messages']) #send the server the info to display
        data = None
        #wait for the messages to be returneds
        while data is None:
            data = self.__coms.get_return(self.__message_handler_name, id)
        return render_template('status_report.html', data=data[0])
    def run(self):
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        self.__coms.send_message_prement("Server started http://%s:%s" % (self.__hostName, self.__serverPort), 2)
        super().set_status("Running")
        self.app.run(debug=False, host=self.__hostName, port=self.__serverPort)
    def kill_Task(self):
        super().kill_Task()
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
    def get_message_handler(self):
        return self.__message_handler     
