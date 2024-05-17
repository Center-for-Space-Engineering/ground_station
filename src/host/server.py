'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
import logging 
from flask import Flask, render_template, request , send_from_directory, jsonify, send_file # pylint: disable=w0611 
from datetime import datetime
import os
import threading
from werkzeug.serving import BaseWSGIServer
from socketserver import ThreadingMixIn
import requests

#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto # pylint: disable=e0401
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class ThreadedWSGIServer(ThreadingMixIn, BaseWSGIServer):
    pass

class serverHandler(threadWrapper):
    '''
        This class is the server for the whole system. It hands serving the webpage and routing request to there respective classes. 
    '''
    def __init__(self, hostName, serverPort, coms, cmd,serial_writer_name:list[str], listener_name:list[str], display_name:str='Local'):
        # pylint: disable=w0612
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs 
            'run' : self.run,
            'kill_Task' : self.kill_Task,
        }
        super().__init__(self.__function_dict)

        self.__hostName = hostName
        self.__serverPort = serverPort

        #set up coms with the serial port
        self.__serial_writer_name = serial_writer_name
        self.__listener_name = listener_name

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

        # create a place holder for our sensors.
        self.__sensor_list = None
        self.__sensor_html_dict = {}
       
        self.__display_name = display_name

        # Enable template auto-reloading in development mode
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True

        self.server = ThreadedWSGIServer(self.__hostName, self.__serverPort, self.app)
        
    def setup_routes(self):
        '''
            This function sets up all the git request that can be accessed by the webpage.
        '''
        self.app.route('/Command', methods=['GET'])(self.command)
        self.app.route('/receive_url', methods=['POST'])(self.set_host_url)
        self.app.route('/')(self.show_command)
        self.app.route('/favicon.ico')(self.facicon)
        self.app.route('/page_manigure.js')(self.serve_page_mangier)
        self.app.route('/get_serial_names')(self.get_serial_names)
        self.app.route('/get_serial_status')(self.get_serial_status)
        self.app.route('/serial_run_request')(self.serial_run_request)
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
        self.__log.send_log(f"Path receive {unknown_path}")
        path = unknown_path.split("/")
        
        dto = print_message_dto("Message received: " + str(path))
        self.__coms.print_message(dto, 3)

        if 'Local' == path[0]: # if it is a command for the host lets run it here
            message = self.__cmd.parse_cmd(path[1:])
        elif 'local_code=501' == path[-1]: #forwarded command
            message = self.__cmd.parse_cmd(path[:-1])
        else :
            response = requests.get('http://' + unknown_path + "/local_code=501") 

            if response.status_code == 200:
                message = (response.json())
            else :
                message = ({
                        'text_data' : 'Unable to run command',
                        'download' : 'no',
                })                

        dto2 = print_message_dto("Server handled request")
        self.__coms.print_message(dto2, 2)

        if isinstance(message, str): # pylint: disable=r1705 
            data_dict = {
                'text_data' : message,
                'download' : 'no',
            }
            return jsonify(data_dict)
        else : 
            return jsonify(message)
    def run(self):
        '''
            This is the run function for the server. 
        '''
        print(f'Server started at http://{self.__hostName}:{self.__serverPort}')  
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        dto = logger_dto(message="Server started http://%s:%s" % (self.__hostName, self.__serverPort), time=str(datetime.now()))
        self.__coms.send_message_permanent(dto, 2)
        super().set_status("Running")
        self.server.serve_forever()
    def kill_Task(self):
        '''
            This closes the Server, after the kill command is received.
        '''
        super().kill_Task()
        if self.server:
            self.server.shutdown()
        self.__log.send_log("Server stopped.")
        self.__log.send_log("Quite command received.")
    def set_sensor_list(self, sensors):
        '''
            This function takes a list of sensor classes that the system has created. 

            NOTE: The list should be of sensor objects!
        '''
        self.__sensor_list = sensors
        #Make the dictionary of all the file paths to each sensors html page, and generate the page (the get_html_page) generates the html page
        for sensor in self.__sensor_list:
            self.__sensor_html_dict[sensor.get_sensor_name()] = (sensor.get_html_page().replace('templates/', ''), sensor)
    def serial_run_request(self):
        '''
            Send a request to the serial writer to execute a command.
        '''
        thread_name = request.args.get('serial_name')
        #make a request for the messages
        id_request = self.__coms.send_request(thread_name, ['write_to_serial_port', request.args.get('serial_command')]) #send the request to the serial writer
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(thread_name, id_request)
        return data_obj
    def get_serial_names(self):
            '''
                Returns all the serial names so the webpage knows about them. 
            '''
            return jsonify({
                'listener' : self.__listener_name,
                'writer' : self.__serial_writer_name
            })
    def command(self):
        '''
            Returns html for the command page, and the display name
        '''
        table_data = self.__cmd.get_commands_webpage()
        data = {
            'table_data' : table_data,
            'display_name' : self.__display_name
        }
        return jsonify(data)
    def show_command(self):
        '''
            returns the commands that this pi can run
        '''
        table_data = self.__cmd.get_commands_webpage()
        for command_dict in table_data:
            command_dict['Host'] = 'Local'
            command_dict['display_name'] = self.__display_name
    
        return render_template('Command.html', table_data=table_data)
    def set_host_url(self):
        # Get the URL of the sending Flask app from the POST request data
        sender_url = request.form.get('sender_url')

        self.__coms.set_host_url([sender_url])

        return 'Hello Host'
    def serve_page_mangier(self):
        '''
            Returns java script to the browser. So that it can be run in browser. 
        '''
        return send_from_directory('source', 'page_manigure.js')
    def get_serial_names(self):
        '''
            Returns all the serial names so the webpage knows about them. 
        '''
        return jsonify({
            'listener' : self.__listener_name,
            'writer' : self.__serial_writer_name
        })
    def get_serial_status(self):
        '''
            This is function returns the serial status to the web server for processing. 
        '''
        data_obj = []
        request_list = [] #keeps track of all the request we have sent. 
        list_pos = 0
        for name in self.__listener_name:
            #make a request to switch the serial port to new configurations
            request_list.append([name, self.__coms.send_request(name, ['get_status_web']), False, list_pos]) #send the request to the port
            list_pos += 1
            data_obj.append({"Place holder": None}) # We are creating a list will all spots we need for return values so later we can pack the list and everything will be in the same order. 
        for name in self.__serial_writer_name:
            #make a request to switch the serial port to new configurations
            request_list.append([name, self.__coms.send_request(name, ['get_status_web']), False, list_pos]) #send the request to the port
            list_pos += 1
            data_obj.append({"Place holder": None}) # We are creating a list will all spots we need for return values so later we can pack the list and everything will be in the same order. 
        all_request_serviced = False
        while not all_request_serviced: # pylint: disable=c0200 
            all_request_serviced = True
            #loop over all our requests
            for i in range(len(request_list)): # pylint: disable=c0200 
                data_obj_temp = None
                # if we haven't all ready seen the request come back  check for it. 
                if not request_list[i][2]: 
                    data_obj_temp = self.__coms.get_return(request_list[i][0], request_list[i][1])
                    # if we do get a request add it to the list and make the request as having been serviced. 
                    if data_obj_temp is not None:
                        request_list[i][2] = True
                        data_obj[request_list[i][3]] = data_obj_temp
                all_request_serviced = all_request_serviced and request_list[i][2] #All the request have to say they have been serviced for this to mark as true. 
        return jsonify(data_obj)
    def serial_run_request(self):
        '''
            Send a request to the serial writer to execute a command.
        '''
        thread_name = request.args.get('serial_name')
        #make a request for the messages
        id_request = self.__coms.send_request(thread_name, ['write_to_serial_port', request.args.get('serial_command')]) #send the request to the serial writer
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(thread_name, id_request)
        return data_obj