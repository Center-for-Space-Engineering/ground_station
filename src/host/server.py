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
    def __init__(self, hostName, serverPort, coms, cmd, messageHandler:serverMessageHandler, messageHandlerName:str, serial_writer_name:list[str], serial_listener_name:list[str]):
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

        # create a place holder for our sensors.
        self.__sensor_list = None
        self.__sensor_html_dict = {}

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
        self.app.route('/page_manigure.js')(self.serve_page_mangier)
        self.app.route('/get_updated_logger_report', methods=['GET'])(self.get_updated_logger_report)
        self.app.route('/get_updated_prem_logger_report', methods=['GET'])(self.get_updated_prem_logger_report)
        self.app.route('/get_updated_thread_report', methods=['GET'])(self.get_updated_thread_report)
        self.app.route('/get_refresh_status_report', methods=['GET'])(self.get_update_status_report)
        self.app.route('/get_serial_info_update')(self.get_serial_info_update)
        self.app.route('/serial_run_request')(self.serial_run_request)
        self.app.route('/favicon.ico')(self.facicon)
        self.app.route('/start_serial')(self.start_serial)
        self.app.route('/get_serial_names')(self.get_serial_names)
        self.app.route('/get_serial_status')(self.get_serial_status)
        self.app.route('/get_sensor_status')(self.get_sensor_status)
        self.app.route('/sensor_page')(self.sensor_page)
        self.app.route('/sensor_graph_names')(self.sensor_graph_names)
        self.app.route('/get_sensor_graph_update')(self.get_sensor_graph_update)
        self.app.route('/sensor_last_published')(self.sensor_last_published)

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
                'text_data' : message,
                'download' : 'no',
            }
            return jsonify(data_dict)
        else :
            return jsonify(message)
    def serve_page_mangier(self):
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
        thread_name = request.args.get('serial_name')
        #make a request for the messages
        id_request = self.__coms.send_request(thread_name, ['write_to_serial_port', request.args.get('serial_command')]) #send the request to the serial writer
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(thread_name, id_request)
        return data_obj
    def start_serial(self):
        '''
            This starts a reconfigured request to the serial port the users asked for. 
        '''
        requested_port = request.args.get('requested')
        baud_rate = request.args.get('baud_rate')
        stop_bit = request.args.get('stop_bit')

        print(f"{requested_port} {baud_rate} {stop_bit}")

        #make a request to switch the serial port to new configurations
        id_request = self.__coms.send_request(requested_port, ['config_port', baud_rate, stop_bit]) #send the request to the port
        data_obj = None
        #wait for the messages to be returned
        while data_obj is None:
            data_obj = self.__coms.get_return(requested_port, id_request)
        return data_obj
    def get_serial_status(self):
        data_obj = []
        request_list = [] #keeps track of all the request we have sent. 
        list_pos = 0
        for name in self.__serial_listener_name:
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
        while not all_request_serviced:
            all_request_serviced = True
            #loop over all our requests
            for i in range(len(request_list)):
                data_obj_temp = None
                # if we haven't all ready seen the request come back  check for it. 
                if not request_list[i][2]: 
                    data_obj_temp = self.__coms.get_return(request_list[i][0], request_list[i][1])
                    # if we do get a request add it to the list and make the request as having been serviced. 
                    if data_obj_temp != None:
                        request_list[i][2] = True
                        data_obj[request_list[i][3]] = data_obj_temp
                all_request_serviced = all_request_serviced and request_list[i][2] #All the request have to say they have been serviced for this to mark as true. 
        return jsonify(data_obj)
    def get_serial_names(self):
        return jsonify({
            'listener' : self.__serial_listener_name,
            'writer' : self.__serial_writer_name
        })
    def get_sensor_status(self):
        '''
            This function gets all the sensors status then returns that to the server. 
        '''
        if self.__sensor_list is None:
            return jsonify([{
                'Name' :'NA',
                'status' : 'NA',
                'taps' : 'None'
            }])
        report = []
        for sensor in self.__sensor_list:
            sensor_name = sensor.get_sensor_name()
            status = sensor.get__sensor_status()
            taps = ' | '.join(sensor.get_taps())
            report.append({
                'name' : sensor_name,
                'status' : status,
                'taps' : taps
            })
        return jsonify(report)
    def sensor_page(self):
        '''
            Returns the html page for the sensors config
        '''
        try :
            sensor_name = request.args.get('name')
            return render_template(self.__sensor_html_dict[sensor_name])
        except KeyError as e:
            return self.open_sensor() #this means we haven't created our sensor page yet so we just are going to return a different page        
    def sensor_graph_names(self):
        '''
            Returns a list of graphs to the browser
        '''
        sensor_name = request.args.get('name')
        return jsonify({
            'graphs' : self.__sensor_html_dict[sensor_name][1].get_graph_names()
        })
    def get_sensor_graph_update(self):
        '''
            Returns a the data report to the browser
        '''
        sensor_name = request.args.get('name')
        try : 
            return jsonify(self.__sensor_html_dict[sensor_name][1].get_data_report())
        except KeyError as e:
            return jsonify('') #this means we haven't created our sensor page yet so we just are going to return a different page
    def sensor_last_published(self) :
        sensor_name = request.args.get('name')
        try : 
            return jsonify(self.__sensor_html_dict[sensor_name][1].get_last_published_data())
        except KeyError as e:
            return jsonify({
            'time' : 'NA',
            'data' : 'NA'
        }) #this means we haven't created our sensor page yet so we just are going to return a different page  
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
    def set_sensor_list(self, sensors):
        '''
            This function takes a list of sensor classes that the system has created. 

            NOTE: The list should be of sensor objects!
        '''
        self.__sensor_list = sensors
        #Make the dictionary of all the file paths to each sensors html page, and generate the page (the get_html_page) generates the html page
        for sensor in self.__sensor_list:
            self.__sensor_html_dict[sensor.get_sensor_name()] = (sensor.get_html_page().replace('templates/', ''), sensor)
