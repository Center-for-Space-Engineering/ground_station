'''
    This modules handles request from both the web and other threads. It starts the server then servers requests. 
'''
#python imports
import logging 
from flask import Flask, render_template, request , send_from_directory, jsonify, send_file # pylint: disable=w0611 
from datetime import datetime
import os
import threading
import copy
import requests

#imports from other folders that are not local
from logging_system_display_python_api.logger import loggerCustom # pylint: disable=e0401
from threading_python_api.threadWrapper import threadWrapper # pylint: disable=e0401
from server_message_handler import serverMessageHandler # pylint: disable=e0401
from peripheral_hand_shake import peripheral_hand_shake # pylint: disable=e0401

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.logger_dto import logger_dto # pylint: disable=e0401
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401
from logging_system_display_python_api.DTOs.byte_report import byte_report_dto # pylint: disable=e0401

class serverHandler(threadWrapper):
    '''
        This class is the server for the whole system. It hands serving the webpage and routing request to there respective classes. 
    '''
    def __init__(self, hostName, serverPort, coms, cmd, messageHandler:serverMessageHandler, messageHandlerName:str, serial_writer_name:list[str], listener_name:list[str], failed_test_path:str, passed_test_path:str, peripheral_handler:peripheral_hand_shake, display_name:str):
        # pylint: disable=w0612
        self.__function_dict = { #NOTE: I am only passing the function that the rest of the system needs 
            'run' : self.run,
            'getComs' : self.getComs,
        }
        super().__init__(self.__function_dict)

        #set up server coms 
        self.__message_handler = messageHandler
        self.__message_handler_name = messageHandlerName
        


        self.__hostName = hostName
        self.__serverPort = serverPort
        self.__display_name = display_name
        self.__system_info_lock = threading.Lock()

        #set up coms with the serial port
        self.__serial_writer_name = serial_writer_name
        self.__listener_name = listener_name
        self.__serial_writter_lock = threading.Lock()
        self.__serial_listener_lock = threading.Lock()

        #these class are used to communicate with the reset of the cse code
        self.__coms = coms
        self.__cmd = cmd
        self.__log = loggerCustom("logs/server_logs.txt")

        #get the possible commands to run
        cmd_dict = self.__cmd.get_command_dict()

        #Connect to peripheral 
        self.__peripheral_handler = peripheral_handler

        self.__peripheral_handler.connect_peripherals()

        self.__peripherals_commands = self.__peripheral_handler.get_commands()
        self.__peripherals_commands_lock = threading.Lock()

        self.__peripherals_serial_interface = self.__peripheral_handler.get_peripheral_serial_interfaces()
        self.__peripherals_serial_interface_lock = threading.Lock()
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

        #this is the file path for our failed test
        self.__failed_test_path = failed_test_path
        self.__passed_test_path = passed_test_path

        # Enable template auto-reloading in development mode
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True

        self.__current_session_name = "NA"
        self.__session_running = False
        self.__session_description = "NA"
        self.__unit_test_group = "Defult"
        self.__session_lock = threading.Lock()       
    def setup_routes(self):
        '''
            This function sets up all the git request that can be accessed by the webpage.
        '''
        #Paths that the server will need 
        self.app.route('/')(self.status_report)
        self.app.route('/templates/assets/style.css', methods=['GET'])(self.style)
        self.app.route('/open_data_stream')(self.open_data_stream)
        self.app.route('/Sensor')(self.open_sensor)
        self.app.route('/Command')(self.command)
        self.app.route('/unit_testing')(self.unit_testing)
        self.app.route('/failed_test')(self.failed_test)
        self.app.route('/page_manigure.js')(self.serve_page_mangier)
        self.app.route('/get_updated_logger_report', methods=['GET'])(self.get_updated_logger_report)
        self.app.route('/get_updated_prem_logger_report', methods=['GET'])(self.get_updated_prem_logger_report)
        self.app.route('/get_updated_thread_report', methods=['GET'])(self.get_updated_thread_report)
        self.app.route('/get_refresh_status_report', methods=['GET'])(self.get_update_status_report)
        self.app.route('/get_serial_info_update')(self.get_serial_info_update) 
        self.app.route('/favicon.ico')(self.facicon)
        self.app.route('/get_serial_names')(self.get_serial_names)
        self.app.route('/get_serial_status')(self.get_serial_status)
        self.app.route('/get_sensor_status')(self.get_sensor_status)
        self.app.route('/sensor_page')(self.sensor_page)
        self.app.route('/test_page')(self.test_page)
        self.app.route('/sensor_graph_names')(self.sensor_graph_names)
        self.app.route('/get_sensor_graph_update')(self.get_sensor_graph_update)
        self.app.route('/sensor_last_published')(self.sensor_last_published)
        self.app.route('/update_failed_test')(self.update_failed_test)
        self.app.route('/update_passed_test')(self.update_passed_test)

        #the paths caught by this will connect to the users commands they add
        self.app.add_url_rule('/<path:unknown_path>', 'handle_unknown_path',  self.handle_unknown_path)
        self.app.add_url_rule('/start_session', 'start_session', self.start_session, methods=['POST'])
        self.app.add_url_rule('/end_session', 'end_session', self.end_session, methods=['POST']) 
        self.app.add_url_rule('/logger_reports', 'logger_reports', self.logger_reports, methods=['POST'])
    def facicon(self):
        '''
            Returns image in the corner of the tab. 
        '''
        return send_from_directory(self.__favicon_directory, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    def style(self):
        return send_from_directory('templates/assets/style.css', 'style.css', mimetype='css')
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
            response = requests.get('http://' + unknown_path + "/local_code=501", timeout=10) 

            if response.status_code == 200:
                message = response.json()
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
    
    def get_serial_status(self):
        '''
            This is function returns the serial status to the web server for processing. 
        '''
        data_obj = []
        request_list = [] #keeps track of all the request we have sent. 
        list_pos = 0

        if self.__serial_listener_lock.acquire(timeout=10): # pylint: disable=R1732
            serial_listener = copy.deepcopy(self.__listener_name)
            self.__serial_listener_lock.release()
        else :
            raise RuntimeError("Could not aquire serial listener lock")
        for name in serial_listener:
            #make a request to switch the serial port to new configurations
            request_list.append([name, self.__coms.send_request(name, ['get_status_web']), False, list_pos]) #send the request to the port
            list_pos += 1
            data_obj.append({"Place holder": None}) # We are creating a list will all spots we need for return values so later we can pack the list and everything will be in the same order. 
        
        if self.__serial_writter_lock.acquire(timeout=10): # pylint: disable=R1732
            serial_writer = self.__serial_writer_name
            self.__serial_writter_lock.release()
        else :
            raise RuntimeError("Could not aquire serial writer lock")
        for name in serial_writer:
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
        
        if self.__peripherals_serial_interface_lock.acquire(timeout=10): # pylint: disable=R1732
            peripherals_serial_copy = copy.deepcopy(self.__peripherals_serial_interface)
            self.__peripherals_serial_interface_lock.release()
        else :
            raise RuntimeError("Could not aquire peripherals serial interface lock")
        for host in peripherals_serial_copy:
            try : 
                response = requests.get('http://' + host + '/get_serial_status', timeout=10)
            
                if response.status_code == 200:
                    data = response.json()
                    data_obj.extend(data)           
            except : # pylint: disable=W0702
                pass # request failed just going to pass it
        return jsonify(data_obj)
    def get_serial_names(self):
        '''
            Returns all the serial names so the webpage knows about them. 
        '''

        if self.__serial_listener_lock.acquire(timeout=10): # pylint: disable=R1732
            serial_listener = copy.deepcopy(self.__listener_name)
            self.__serial_listener_lock.release()
        else :
            raise RuntimeError("Could not aquire serial listener lock")
        if self.__serial_writter_lock.acquire(timeout=10): # pylint: disable=R1732
            serial_writer = copy.deepcopy(self.__serial_writer_name)
            self.__serial_writter_lock.release()
        else : 
            raise RuntimeError("Could not aquire serial writter lock")
        data = {
            'listener' : serial_listener,
            'writer' : serial_writer
        }
        
        if self.__peripherals_serial_interface_lock.acquire(timeout=10): # pylint: disable=R1732
            peripherals_serial_copy = copy.deepcopy(self.__peripherals_serial_interface)
            self.__peripherals_serial_interface_lock.release()
        else : 
            raise RuntimeError("Could not aquire serial interface lock")
        for host in peripherals_serial_copy:
            data['listener'].extend(peripherals_serial_copy[host]['listener'])
            data['writer'].extend(peripherals_serial_copy[host]['writer'])
        return jsonify(data)
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
        except KeyError:
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
        except KeyError:
            return jsonify('') #this means we haven't created our sensor page yet so we just are going to return a different page
    def sensor_last_published(self) :
        '''
            Finds the last published data on the current sensor
        '''
        sensor_name = request.args.get('name')
        try : 
            return jsonify(self.__sensor_html_dict[sensor_name][1].get_last_published_data())
        except KeyError:
            return jsonify({
            'time' : 'NA',
            'data' : 'NA'
        }) #this means we haven't created our sensor page yet so we just are going to return a different page
    def update_failed_test(self):
        '''
            This function updates the list of failed test on the webpage
        '''
        files = []

        # Walk through the testing folder and find all the failed test their. 
        for root, _, filenames in os.walk(self.__failed_test_path):
            # Add the file names to the list
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path.replace('templates/', ''))
        return files
    def update_passed_test(self):
        '''
            This function updates the list of passed test on the webpage
        '''
        files = []

        # Walk through the testing folder and find all the failed test their. 
        for root, _, filenames in os.walk(self.__passed_test_path):
            # Add the file names to the list
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path.replace('templates/', ''))
        return files
    def test_page(self):
        '''
            Returns the html page for a test
        '''
        test_name = request.args.get('name')

        return render_template(test_name)
    def run(self):
        '''
            This is the run function for the server. 
        '''
        print(f'Server started at http://{self.__hostName}:{self.__serverPort}')  
        self.__log.send_log("Test Server started http://%s:%s" % (self.__hostName, self.__serverPort))
        dto = logger_dto(message="Server started http://%s:%s" % (self.__hostName, self.__serverPort), time=str(datetime.now()))
        self.__coms.send_message_permanent(dto, 2)
        super().set_status("Running")
        self.app.run(debug=False, host=self.__hostName, port=self.__serverPort, threaded=True)
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
        if self.__system_info_lock.acquire(timeout=10): # pylint: disable=R1732
            display_name = self.__display_name
            self.__system_info_lock.release()
        else : 
            raise RuntimeError("Could not aquire system info lock")
        table_data = self.__cmd.get_commands_webpage()
        for command_dict in table_data:
            command_dict['Host'] = 'Local'
            command_dict['display_name'] = display_name
        if self.__peripherals_commands_lock.acquire(timeout=10): # pylint: disable=R1732
            peripherals_commands_copy = copy.deepcopy(self.__peripherals_commands)
            self.__peripherals_commands_lock.release()
        else :
            raise RuntimeError("Could not aquire peripherals commands lock")
        for host in peripherals_commands_copy:
            for command_dict in peripherals_commands_copy[host]['table_data']:
                command_dict['Host'] = host 
                command_dict['display_name'] = peripherals_commands_copy[host]['display_name']
                table_data.append(command_dict)
        return render_template('Command.html', table_data=table_data)
    def failed_test(self):
        '''
            Returns html for the command page
        '''
        return render_template('failed_test_achieve.html')
    def unit_testing(self):
        '''
            Returns html for the unit testing page
        '''
        return render_template('passed_test_achieve.html')
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
    def start_session(self):
        '''
            Start a session id 
        '''
        session_name = request.json.get('sessionName')
        session_description = request.json.get('description')
        unittestGroup = request.json.get('unittestGroup')

        if self.__session_lock.acquire(timeout=10): # pylint: disable=R1732
            self.__current_session_name = session_name
            self.__session_description = session_description
            self.__unit_test_group = unittestGroup
            self.__session_running = True
            self.__session_lock.release()
        else : 
            raise RuntimeError("Could not aquire session lock")
        if session_name: # pylint: disable=R1705
            # Do something with the session name, like start a session
            return jsonify({'message': 'Session started successfully'}), 200
        else: 
            return jsonify({'error': 'Session name not provided'}), 400

    def end_session(self):
        '''
            This functions marks the session to end.
        '''
        # Do something to end the session
        if self.__session_lock.acquire(timeout=10): # pylint: disable=R1732
            self.__session_running = False
            self.__session_lock.release()
        else : 
            raise RuntimeError("Could not aquire session lock")
        return jsonify({'message': 'Session ended successfully'}), 200

    def get_session_info(self):
        '''
            Returns the session information to the requester.

            Return order:
            name, description, running 
        '''
        if self.__session_lock.acquire(timeout=10): # pylint: disable=R1732
            name = self.__current_session_name
            session_description = self.__session_description
            running = self.__session_running
            test_group = self.__unit_test_group
            self.__session_lock.release()
        else : 
            raise RuntimeError("Could not aquire session lock")
        return name, session_description, running, test_group
    def logger_reports(self):
        '''
            Collect data form the peripherals. The pass that data into our logging system.
        '''

        message = request.form.get('message')
        _ = request.form.get('sender')
        display_name = request.form.get('Display_name')
        request_fucntion = request.form.get('function')
        message = request.form.get('message')

        if request_fucntion == 'send_message_permanet':
            dto_obj = print_message_dto(message=f"{display_name} : {message}")
            self.__coms.send_message_permanet(dto_obj)
        elif request_fucntion == 'print_message':
            dto_obj = print_message_dto(message=f"{display_name} : {message}")
            self.__coms.print_message(dto_obj)
        elif request_fucntion == 'report_bytes':
            dto_obj = byte_report_dto(byte_count=int(message), thread_name=request.form.get('thread_name'), time=request.form.get('time'))
            self.__coms.report_bytes(dto_obj)
        elif request_fucntion == 'report_additional_status':
            dto_obj = print_message_dto(message=f"{display_name} : {message}")
            self.__coms.report_additional_status(dto_obj)
        
        return 'OK'
