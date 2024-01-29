'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
import logging
from flask import Flask, render_template, request , send_from_directory, jsonify
from threading import Lock
import random
from datetime import datetime

#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom
from threading_python_api.threadWrapper import threadWrapper
from server_message_handler import serverMessageHandler

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto

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
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

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
        self.app.route('/get_updated_logger_report', methods=['GET'])(self.get_updated_logger_report)
        self.app.route('/get_updated_prem_logger_report', methods=['GET'])(self.get_updated_prem_logger_report)
        self.app.route('/get_updated_thread_report', methods=['GET'])(self.get_updated_thread_report)
        self.app.route('/get_refresh_status_report', methods=['GET'])(self.get_update_status_report)
        self.app.route('/get_serial_info_update')(self.get_serial_info_update)
        self.app.route('/serial_run_request')(self.serial_run_request)

        #the paths caught by this will connect to the users commands they add
        self.app.add_url_rule('/<path:unknown_path>', 'handle_unknown_path',  self.handle_unknown_path)
    def handle_unknown_path(self, unknown_path):
        path = unknown_path.split("/")
        self.__log.send_log("Message recived: " + str(path))
        #this  if statement decides if it is going to run a prebuilt command or run one of the 
        dto = print_message_dto("Message recived: " + str(path))
        self.__coms.print_message(dto, 3)
        message = self.__cmd.parse_cmd(path)
        self.__log.send_log(f"Paht recive {unknown_path}")
        self.__coms.print_message("Server responed ", 2)
        return message
    def serve_page_manigure(self):
        return send_from_directory('source', 'page_manigure.js')
    def status_report(self):
        dto = print_message_dto('Got status_report request')
        self.__coms.print_message(dto, 3)
        
        #get prelogs
        prem_data = self.get_prem_message_log()
        #get status report
        status = self.get_status_report()
        #get thread report
        thread_report = self.get_thread_report()
        #get logs
        data = self.get_loggs_data()
        #get byte report
        return render_template('status_report.html', data=data, prem_data=prem_data, thread_report=thread_report, status=status)
    def get_prem_message_log(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_prem_message_log']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        if len(data_obj) > 0:data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not avalible',
            'message':"Prem Loggs Comming online"
            }]        
        return data
    def make_web_dto(self, data_in):
        data = []
        for i in data_in:
            data.append({
                'time':i.get_time(),
                'message':i.get_message(),
            })
        return data
    def get_updated_prem_logger_report(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_prem_message_log']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        if len(data_obj) > 0:data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not avalible',
            'message':"Loggs Comming online"
            }]
        return jsonify(prem_logger_report=data)
    def get_loggs_data(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_messages']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        if len(data_obj) > 0:data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not avalible',
            'message':"Loggs Comming online"
            }]        
        return data
    def get_updated_logger_report(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_messages']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        if len(data_obj) > 0:data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not avalible',
            'message':"Loggs Comming online"
            }]
        return jsonify(logger_report=data)      
    def get_thread_report(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_thread_report']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        data = []
        if len(data_obj[0]) > 0:
            for report in data_obj[0]:
                data.append({
                    'time':report[1].get_time(),
                    'message':report[1].get_message(),
                    'name':report[0],
                    'status':report[2],
                    }
                )
        else : 
            data.append({
                'time':"Not avalible",
                'message':'None',
                'name':"Loading thread reports",
                'status':"Loading",
                }
            )
        return data
    def get_updated_thread_report(self):
        data = self.get_thread_report()
        return jsonify(thread_report = data)
    def get_status_report(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_report_status']) #send the server the info to display
        data_obj = None

        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        data = []
        if len(data_obj[0]) < 1: 
            data = [{
                    'name' : "Not available",
                    'message' : "No reports at this time",
                    }]
        else :
            for dict_report in data_obj:
                for thread_name in dict_report:
                    data.append({
                        'name':thread_name,
                        'message':dict_report[thread_name]
                    })
        return data
    def get_update_status_report(self):
        data = self.get_status_report()
        return jsonify(status_list = data)
    def get_serial_info_update(self):
        #make a request for the messages
        id = self.__coms.send_request(self.__message_handler_name, ['get_byte_report']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        return jsonify(data_obj)
    def serial_run_request(self):
        print(request.args.get('serial_command'))
        #make a request for the messages
        id = self.__coms.send_request('serial_writter', ['write_to_serial_port']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returneds
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id)
        return data_obj
    def run(self):
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        dto = logger_dto(message="Server started http://%s:%s" % (self.__hostName, self.__serverPort), time=str(datetime.now()))
        self.__coms.send_message_prement(dto, 2)
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
        table_data = self.__cmd.get_commands_webpage()
        return render_template('Command.html', table_data=table_data)
    def get_message_handler(self):
        return self.__message_handler
