'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
import logging 
from flask import Flask, render_template, request , send_from_directory, jsonify, send_file
from datetime import datetime
import os

#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401
from server_message_handler import serverMessageHandler # pylint: disable=e0401

#import DTO for communicating internally
from DTOs.logger_dto import logger_dto # pylint: disable=e0401
from DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class serverHandler(threadWrapper):
    '''
        This class is the server for the whole system. It hands serving the webpage and routing request to there respective classes. 
    '''
    def __init__(self, hostName, serverPort, coms, cmd, messageHandler:serverMessageHandler, messageHandlerName:str, serial_writer_name:str, serial_listener_name:str):
        # pylint: disable=w0612
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

        #set up coms with the serial port
        self.__serial_writer_name = serial_writer_name
        self.__serial_listener_name = serial_listener_name

        #these class are used to communicate with the reset of the cse code
        self.__coms = coms
        self.__cmd = cmd
        self.__log = loggerCustom("logs/server_logs.txt")

        #get the possible commands to run
        cmd_dict = self.__cmd.get_command_dict()

        #set up server
        # Disable print statements by setting the logging level to ERROR
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # set up the app
        self.app = Flask(__name__)
        self.__favicon_directory = os.path.join(self.app.root_path, 'static')
        self.setup_routes()
        print(f'Server started at http://{self.__hostName}:{self.__serverPort}')  
    def setup_routes(self):
        '''
            This function sets up all the git request that can be accessed by the webpage.
        '''
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
        self.app.route('/favicon.ico')(self.facicon)
        self.app.route('/start_serial')(self.start_serial)
        self.app.route('/serial_running_listener')(self.serial_running_listener)
        self.app.route('/serial_running_writer')(self.serial_running_writer)

        #the paths caught by this will connect to the users commands they add
        self.app.add_url_rule('/<path:unknown_path>', 'handle_unknown_path',  self.handle_unknown_path)
    def facicon(self):
        '''
            Returns image in the corner of the tab. 
        '''
        return send_from_directory(self.__favicon_directory, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    def handle_unknown_path(self, unknown_path):
        '''
            This handles path that are not automatically added. (Basically user defined commands.)
        '''
        path = unknown_path.split("/")
        self.__log.send_log("Message received: " + str(path))
        #this  if statement decides if it is going to run a prebuilt command or run one of the 
        dto = print_message_dto("Message received: " + str(path))
        self.__coms.print_message(dto, 3)
        message = self.__cmd.parse_cmd(path)
        self.__log.send_log(f"Path receive {unknown_path}")
        dto2 = print_message_dto("Server handled request")
        self.__coms.print_message(dto2, 2)
        if isinstance(message, str):
            data_dict = {
                'data' : message,
                'download' : False,
            }
            return message
        else : 
            data_dict = {
                'data' : message[0],
                'download' : False,
            }
            return send_file(, as_attachment=True)
    def serve_page_manigure(self):
        '''
            Returns java script to the browser. So that it can be run in browser. 
        '''
        return send_from_directory('source', 'page_manigure.js')
    def status_report(self):
        '''
            collects and then send the logs from the server. 
        '''
        dto = print_message_dto('Got status_report request')
        self.__coms.print_message(dto, 3)
        
        #get prem logs
        prem_data = self.get_prem_message_log()
        #get status report
        status = self.get_status_report()
        #get thread report
        thread_report = self.get_thread_report()
        #get logs
        data = self.get_logs_data()
        #get byte report
        return render_template('status_report.html', data=data, prem_data=prem_data, thread_report=thread_report, status=status)
    def get_prem_message_log(self):
        '''
            Gets the logs witch will persist across run time. 
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_prem_message_log']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
        if len(data_obj) > 0: 
            data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not available',
            'message':"Prem Logs Coming online"
            }]        
        return data
    def make_web_dto(self, data_in):
        '''
            Makes a dict that the webpage and understand. (For logging messages.)
        '''
        data = []
        for i in data_in:
            data.append({
                'time':i.get_time(),
                'message':i.get_message(),
            })
        return data
    def get_updated_prem_logger_report(self):
        '''
            This function fetches the prem log report.
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_prem_message_log']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
        if len(data_obj) > 0:
            data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not available',
            'message':"Logs Coming online"
            }]
        return jsonify(prem_logger_report=data)
    def get_logs_data(self):
        '''
            Gets the logs update, for the system. 
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_messages']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
        if len(data_obj) > 0:
            data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not available',
            'message':"Logs Coming online"
            }]        
        return data
    def get_updated_logger_report(self):
        '''
            This is the function that the webpage calls to get the logger update. 
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_messages']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
        if len(data_obj) > 0:
            data = self.make_web_dto(data_obj[0])
        else : 
            data = [{
            'time' : 'Not available',
            'message':"Logs Coming online"
            }]
        return jsonify(logger_report=data)      
    def get_thread_report(self):
        '''
            Get the threading report from the system.
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_thread_report']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
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
                'time':"Not available",
                'message':'None',
                'name':"Loading thread reports",
                'status':"Loading",
                }
            )
        return data
    def get_updated_thread_report(self):
        '''
            Server calls this to get the thread report.
        '''
        data = self.get_thread_report()
        return jsonify(thread_report = data)
    def get_status_report(self):
        '''
            Web page class this function to get the status update
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_report_status']) #send the server the info to display
        data_obj = None

        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
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
        '''
            gets the status report from the system. 
        '''
        data = self.get_status_report()
        return jsonify(status_list = data)
    def get_serial_info_update(self):
        '''
            Gets the serial feed information from the system. 
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__message_handler_name, ['get_byte_report']) #send the server the info to display
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__message_handler_name, id_request)
        return jsonify(data_obj)
    def serial_run_request(self):
        '''
            Send a request to the serial writer to execute a command.
        '''
        #make a request for the messages
        id_request = self.__coms.send_request(self.__serial_writer_name, ['write_to_serial_port', request.args.get('serial_command')]) #send the request to the serial writer
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(self.__serial_writer_name, id_request)
        return data_obj
    def start_serial(self):
        '''
            This starts a reconfigured serial listener and writer. 
        '''
        baud_rate = request.args.get('baud_rate')
        stop_bit = request.args.get('stop_bit')

        #make a request to switch the serial port to new configurations, for the serial writer
        id_writer = self.__coms.send_request(self.__serial_writer_name, ['config_port', baud_rate, stop_bit]) #send the request to the serial writer
        data_obj_writer = None
        #wait for the messages to be returned
        while data_obj_writer is None:
            data_obj_writer = self.__coms.get_return(self.__serial_writer_name, id_writer)
        #make a request to switch the serial port to new configurations, for the serial listener
        id_listener = self.__coms.send_request(self.__serial_listener_name, ['config_port', baud_rate, stop_bit]) #send the request to the serial writer
        data_obj_listener = None
        while data_obj_listener is None:
            data_obj_listener = self.__coms.get_return(self.__serial_listener_name, id_listener)
        data_obj = data_obj_listener + data_obj_writer
        return data_obj
    def serial_running_writer(self):
        '''
            Checks if the serial writer is running and returns that to the server. 
        '''
        id_writer = self.__coms.send_request(self.__serial_writer_name, ['get_connected']) #send the request to the serial writer
        data_obj_writer = None
        #wait for the messages to be returned
        while data_obj_writer is None:
            data_obj_writer = self.__coms.get_return(self.__serial_writer_name, id_writer)
        if isinstance(data_obj_writer, bool): 
            data_obj = "Online" if data_obj_writer else "Not Online"
        else : data_obj = "Not Online"
        return data_obj
    def serial_running_listener(self):
        '''
            Checks fi the serial reader is running and returns that to the server.
        '''
        id_listener = self.__coms.send_request(self.__serial_listener_name, ['get_connected']) #send the request to the serial writer
        data_obj_listen = None
        #wait for the messages to be returned
        while data_obj_listen is None:
            data_obj_listen = self.__coms.get_return(self.__serial_listener_name, id_listener)
        if isinstance(data_obj_listen, bool):
            data_obj = "Online" if data_obj_listen else "Not Online"
        else : data_obj = "Not Online"
        return data_obj
    def run(self):
        '''
            This is the run function for the server. 
        '''
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        dto = logger_dto(message="Server started http://%s:%s" % (self.__hostName, self.__serverPort), time=str(datetime.now()))
        self.__coms.send_message_permanent(dto, 2)
        super().set_status("Running")
        self.app.run(debug=False, host=self.__hostName, port=self.__serverPort)
    def kill_Task(self):
        '''
            This closes the Server, after the kill command is received.
        '''
        super().kill_Task()
        self.__log.send_log("Server stopped.")
        self.__log.send_log("Quite command received.")
    def setHandlers(self, db):
        '''
            Sets up the data base configuration. 
        '''
        self.__cmd.collect_commands(db)    
    def open_data_stream(self):
        '''
            Return the html page for the data stream page.
        '''
        return render_template('data_stream.html')
    def open_sensor(self):
        '''
            Returns html for the sensor page
        '''
        return render_template('sensor.html')
    def command(self):
        '''
            Returns html for the command page
        '''
        table_data = self.__cmd.get_commands_webpage()
        return render_template('Command.html', table_data=table_data)
    def get_message_handler(self):
        '''
            Return the servers message handler object. 
        '''
        return self.__message_handler
    def getComs(self):
        '''
            Get the coms object, the coms object is how ever thread talks to each other. 
        '''
        return self.__coms
