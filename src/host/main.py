'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
#python built in imports
import time
import datetime
import yaml
import argparse

#python custom imports
import system_constants as sensor_config # pylint: disable=e0401 
from threading_python_api.taskHandler import taskHandler # pylint: disable=e0401 
from database_python_api.database_control import DataBaseHandler # pylint: disable=e0401
from logging_system_display_python_api.messageHandler import messageHandler # pylint: disable=e0401
from cmd_inter import cmd_inter # pylint: disable=e0401
from server import serverHandler # pylint: disable=e0401
from server_message_handler import serverMessageHandler # pylint: disable=e0401
from pytesting_api.test_runner import test_runner # pylint: disable=e0401
from pytesting_api import global_test_variables # pylint: disable=e0401
from peripheral_hand_shake import peripheral_hand_shake # pylint: disable=e0401

#These are some Debugging tools I add, Turning off the display is really useful for seeing errors, because the terminal wont get erased every few milliseconds with the display on.
NO_PORT_LISTENER = False
NO_SENSORS = False

if not NO_PORT_LISTENER:
    from port_interface_api.port_listener import port_listener # pylint: disable=e0401
if not NO_SENSORS:
    from sensor_interface_api.collect_sensor import sensor_importer # pylint: disable=e0401

def main(): # pylint: disable=R0915
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''

    ###################### Import from the Yaml file #########################
    # Load the YAML file
    with open("main.yaml", "r") as file:
        config_data = yaml.safe_load(file)
    
    test_interval = datetime.timedelta(seconds=config_data.get("test_interval", 0))
    failed_test_path = config_data.get("failed_test_path", 0)
    passed_test_path = config_data.get("passed_test_path", 0)
    max_passed_test = config_data.get("max_passed_test", 0)

    display_name = config_data.get("display_name", "")

    peripheral_config_dict = config_data.get("peripheral_config_dict", "")

    hostname = config_data.get("hostname", "")
    port = config_data.get("port", 0)
    server_listener_name = config_data.get("server_listener_name", "")
    server_name_host = config_data.get("server_name_host", "")

    data_base = config_data.get("data_base", "") #thread name
    data_base_name = config_data.get("data_base_name", "")#sql database name
    sensor_config.database_name = data_base #other things want this varible as well. 

    host = config_data.get("host", "")
    user = config_data.get("user", "")
    password = config_data.get("password", "")

    port_listener_list = [sub_key['name'] for key in peripheral_config_dict for sub_key in peripheral_config_dict[key]['listener_port_list']]

    serial_writer_list = []

    list_of_peripherals_url = [peripheral_config_dict[key]['host_name'] + ':' + str(peripheral_config_dict[key]['connection_port']) for key in peripheral_config_dict]

    
    if not NO_SENSORS:
        # Sensor configs
        sensor_config_dict = config_data.get("sensor_config_dict", {})

        # set up the config file
        sensor_config.interface_listener_list = port_listener_list
        sensor_config.server = server_listener_name
        sensor_config.sensors_config = sensor_config_dict

        #ccsds packet parsing constants
        ccsds_header_len = config_data.get("ccsds_header_len", 0)
        sync_word = config_data.get("sync_word", 0)
        sync_word_len = config_data.get("sync_word_len", 0)
        packet_len_addr1 = config_data.get("packet_len_addr1", 0)
        packet_len_addr2 = config_data.get("packet_len_addr2", 0)
        system_clock = config_data.get("system_clock", 0)
        real_time_clock = config_data.get("real_time_clock", 0)


        sensor_config.ccsds_header_len = ccsds_header_len
        sensor_config.sync_word = sync_word
        sensor_config.sync_word_len = sync_word_len
        sensor_config.packet_len_addr1 = packet_len_addr1
        sensor_config.packet_len_addr2 = packet_len_addr2
        sensor_config.system_clock = system_clock
        sensor_config.real_time_clock = real_time_clock

        # packet structre definition
        packet_struture_path = config_data.get("packets_structure_file_path", 0)
    

    ########################################################################################
    ######################## Get the peripherals informations ##############################

    parser = argparse.ArgumentParser(description='Update repositories and submodules.')
    parser.add_argument('--clear-database', action='store_true', help='Disable updating repositories')
    args = parser.parse_args()

    clear_database = args.clear_database
    ########################################################################################


    ######################## Get the peripherals informations ##############################
    peripherals = peripheral_hand_shake(list_of_peripheral=list_of_peripherals_url, host_url=hostname + ":" + str(port))
    ########################################################################################
    
    ########### Set up server, database, and threading interface ########### 
    #create a server obj, not it will also create the coms object #144.39.167.206
    coms = messageHandler(server_name=server_listener_name, hostname=hostname)
    #make database object 
    dataBase = DataBaseHandler(coms, db_name = data_base_name,is_gui=False, host=host, user=user, password=password, clear_database=clear_database)
    #now that we have the data base we can collect all of our command handlers.s
    cmd = cmd_inter(coms, dataBase)
    #now that we have all the commands we can make the server
    #note because the server requires a thread to run, it cant have a dedicated thread to listen to coms like
    #other classes so we need another class object to listen to internal coms for the server.
    server_message_handler = serverMessageHandler(coms=coms)
    server = serverHandler(hostname, port, coms, cmd, serverMessageHandler, server_listener_name, serial_writer_name=serial_writer_list, listener_name=port_listener_list, failed_test_path=failed_test_path, passed_test_path=passed_test_path, peripheral_handler = peripherals, display_name=display_name)
    

    #first start our thread handler and the message handler (coms) so we can start reporting
    threadPool = taskHandler(coms) # NOTE: we dont need to add a coms task because it add automatically.

    #Make sure to add the  thread handler to coms so that we can send threading requests
    coms.set_thread_handler(threadPool)

    #Next we want to start the server and give it its own thread
    threadPool.add_thread(server.run, server_name_host, server) #this thread services incoming web request
    threadPool.add_thread(server_message_handler.run, server_listener_name, server_message_handler) #this thread services incoming request from other threads on the system. 
    #Now start the data base and give it a thread
    threadPool.add_thread(dataBase.run, data_base, dataBase)
    # add dummy data generator, for now this only works for the screen
    # threadPool.add_thread(dummy.test2, 'Dummy data collector', dummy)

    threadPool.start() #we need to start all the threads we have collected.
    ########################################################################################

    ########### Set up port interface ###########  
    # create the ser_listener
    if not NO_PORT_LISTENER:
        for key in peripheral_config_dict:
            host = peripheral_config_dict[key]['host_name']
            for sub_dictionary in peripheral_config_dict[key]['listener_port_list']:
                port_listener_name = sub_dictionary['name']
                port = sub_dictionary['port']
                batch_size = sub_dictionary['batch_size']
                
                # Port listener one
                port_listener_obj = port_listener(coms = coms, batch_size=batch_size, thread_name=port_listener_name, host=host, port=port)
                threadPool.add_thread(port_listener_obj.run, port_listener_name, port_listener_obj)

        
        threadPool.start() #start the new task
    ########################################################################################
    
    ########### Set up sensor interface ###########
    if not NO_SENSORS:
        # create the sensors interface
        importer = sensor_importer(packets_file=packet_struture_path) # create the importer object
        importer.import_modules() # collect the models to import
        importer.instantiate_sensor_objects(coms=coms) # create the sensors objects.

        sensors = importer.get_sensors() #get the sensors objects
        
        # create a thread for each sensor and then start them. 
        for sensor in sensors:
            threadPool.add_thread(sensor.run, sensor.get_sensor_name(), sensor)
        threadPool.start()

        #Now that all the sensors are started lets build the tap network.
        # create a thread for each sensor and then start them. 
        for sensor in sensors:
            sensor.set_up_taps()

        # give the webpage gain access to the sensors.
        server.set_sensor_list(sensors=sensors)

    ########################################################################################

    ######################### Set up unit tests ############################################
    global_test_variables.coms = coms
    global_test_variables.db_name = data_base
    global_test_variables.session_id = f"Start_up {datetime.datetime.now()}"

    # Now lets set up the session table in the database, 
    table_name = 'session_record'
    table_structure = {
        table_name : [['session_id', 0, 'string'], ['start_time', 0, 'string'], ['end_time', 0, 'string'], ['description', 0, 'string']],
    }
    # This is the main file, so we do have access to the data base object so we could call the create_table_external function directly, 
    # however there are two major problems, 
    # 1: we would actually need to call 'make_request' to get the database to actually run our request.
    # 2: this provides a good example for the user of how to use the coms obj.
    coms.send_request(data_base, ['create_table_external', table_structure]) 

    #Now create the test_runner object
    test_interface = test_runner(failed_test_path=failed_test_path, passed_test_path=passed_test_path, max_files_passed=max_passed_test)
    ########################################################################################



    #Good line if you need to test a thread crashing. 
    # coms.send_request('Data Base', ['save_byte_data', 'NO_TABLE', 0, 'serial listener'])

    #keep the main thread alive for use to see things running. 
    running = True
    session_start_time = datetime.datetime.now()
    session_end_time = datetime.datetime.now()
    session_was_running = False
    session = f'start up session {session_start_time}'
    description = ''
    session_running = False
    test_start_time = datetime.datetime.now()

    #Run the main loop handle session, testing, and threading overhead
    while running:
        try:
            threadPool.get_thread_status() #this commands the threads to report to the server how they are running. 
            
            session, description, session_running, test_group = server.get_session_info() #get the current session settings. 

            if session_running: 
                #tell users we have started
                if not session_was_running:
                    coms.report_additional_status('Main', f'Main thread : Running Session {datetime.datetime.now()}')
                    test_interface.set_test_group([test_group])

                session_was_running = True

                #run test if it is time
                if datetime.datetime.now() - test_start_time >= test_interval:
                    coms.report_additional_status('Main', f'Main thread : Running  test {datetime.datetime.now()}')
                    test_interface.run_tests()
                    coms.report_additional_status('Main', f'Main thread : Completed test {datetime.datetime.now()}')
            elif session_was_running:
                #report the session information
                data = {
                    'session_id' : [session],
                    'start_time' : [str(session_start_time)],
                    'end_time' : [str(session_end_time)],
                    'description' : [description],
                }
                coms.send_request(data_base, ['save_data_group', table_name, data, 'main'])
                session_was_running = False
            else :
                session_start_time = datetime.datetime.now()
                session_was_running = False
            time.sleep(0.1) # the main thread needs to sleep so that it doesnt hurt the cup


        except KeyboardInterrupt:
            running = False
            print('\n>>> Main thread Shutdown Commanded, please wait.')        
    
    threadPool.kill_tasks()
     

if __name__ == "__main__":
    main()
