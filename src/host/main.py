'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
#python built in imports
import time
import datetime
import yaml

#python custom imports
import system_constants as sensor_config # pylint: disable=e0401 
from threading_python_api.taskHandler import taskHandler # pylint: disable=e0401 
from database_python_api.database_control import DataBaseHandler # pylint: disable=e0401
from logging_system_display_python_api.messageHandler import messageHandler # pylint: disable=e0401
from cmd_inter import cmd_inter # pylint: disable=e0401
from server import serverHandler # pylint: disable=e0401
from server_message_handler import serverMessageHandler # pylint: disable=e0401

#These are some Debugging tools I add, Turning off the display is really useful for seeing errors, because the terminal wont get erased every few milliseconds with the display on.
DISPLAY_OFF = True
NO_SERIAL_LISTENER = False
NO_SERIAL_WRITER = False
NO_SENSORS = False

if not NO_SERIAL_LISTENER:
    from python_serial_api.serial_listener import serial_listener # pylint: disable=e0401
if not NO_SERIAL_WRITER:
    from python_serial_api.serial_writer import serial_writer # pylint: disable=e0401
if not NO_SENSORS:
    from sensor_interface_api.collect_sensor import sensor_importer # pylint: disable=e0401

def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''

    ###################### Import from the Yaml file #########################
    # Load the YAML file
    with open("main.yaml", "r") as file:
        config_data = yaml.safe_load(file)
    # Load the sensor yaml file
    if not NO_SENSORS:
        with open("sensor_interface_api/sensors.yaml", "r") as file:
            sensor_config_yaml = yaml.safe_load(file)

        # Combine the data into a single dictionary
        config_data = {**config_data, **sensor_config_yaml}

    batch_size_1 = config_data.get("batch_size_1", 0)
    batch_size_2 = config_data.get("batch_size_2", 0)

    serial_listener_name = config_data.get("serial_listener_name", "")
    serial_writer_name = config_data.get("serial_writer_name", "")
    serial_listener_2_name = config_data.get("serial_listener_2_name", "")
    serial_writer_2_name = config_data.get("serial_writer_2_name", "")

    uart_0 = config_data.get("uart_0", "")
    uart_2 = config_data.get("uart_2", "")

    serial_listener_list = config_data.get("serial_listener_list", [])
    serial_writer_list = config_data.get("serial_writer_list", [])

    hostname = config_data.get("hostname", "")
    port = config_data.get("port", 0)
    server_listener_name = config_data.get("server_listener_name", "")
    server_name_host = config_data.get("server_name_host", "")

    data_base = config_data.get("data_base", "")
    if not NO_SENSORS:
        # Sensor configs
        sensor_config_dict = config_data.get("sensor_config_dict", {})

        # set up the config file
        sensor_config.interface_listener_list = serial_listener_list
        sensor_config.interface_writer_list = serial_writer_list
        sensor_config.server = server_listener_name
        sensor_config.sensors_config = sensor_config_dict
        sensor_config.database_name = data_base

    ########################################################################################

    ########### Set up server, database, and threading interface ########### 
    #create a server obj, not it will also create the coms object #144.39.167.206
    coms = messageHandler(display_off = DISPLAY_OFF, server_name=server_listener_name, hostname=hostname)
    #make database object 
    dataBase = DataBaseHandler(coms, is_gui=False)
    #now that we have the data base we can collect all of our command handlers.
    cmd = cmd_inter(coms, dataBase)
    #now that we have all the commands we can make the server
    #note because the server requires a thread to run, it cant have a dedicated thread to listen to coms like
    #other classes so we need another class object to listen to internal coms for the server.
    server_message_handler = serverMessageHandler(coms=coms)
    server = serverHandler(hostname, port, coms, cmd, serverMessageHandler, server_listener_name, serial_writer_name=serial_writer_list, serial_listener_name=serial_listener_list)
    

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


    ########### Set up seral interface ###########  
    # create the ser_listener
    if not NO_SERIAL_LISTENER:
        # Serial listener one
        print(f"{batch_size_1} {serial_listener_name} {uart_0}")
        ser_listener = serial_listener(coms = coms, batch_size=batch_size_1, thread_name=serial_listener_name, stopbits=1, pins=uart_0)
        threadPool.add_thread(ser_listener.run, serial_listener_name, ser_listener)

        # Serial listener two
        ser_2_listener = serial_listener(coms = coms, batch_size=batch_size_2, thread_name=serial_listener_2_name, baudrate=9600, stopbits=1, pins=uart_2)
        threadPool.add_thread(ser_2_listener.run, serial_listener_2_name, ser_2_listener)
        
        threadPool.start() #start the new task

    # create the ser_writer
    if not NO_SERIAL_WRITER:
        # Serial writer one
        ser_writer = serial_writer(coms = coms, thread_name=serial_writer_name, pins=uart_0)
        threadPool.add_thread(ser_writer.run, serial_writer_name, ser_writer)

        # Serial writer two
        ser_2_writer = serial_writer(coms = coms, thread_name=serial_writer_2_name, baudrate=9600, stopbits=1, pins=uart_2)
        threadPool.add_thread(ser_2_writer.run, serial_writer_2_name, ser_2_writer)
        
        threadPool.start() #start the new task
    ########################################################################################
    
    ########### Set up sensor interface ########### 
    # create the sensors interface
    importer = sensor_importer() # create the importer object
    importer.import_modules() # collect the models to import
    importer.instantiate_sensor_objects(coms=coms) # create the sensors objects.

    sensors = importer.get_sensors() #get the sensors objects
    
    # create a thread for each sensor and then start them. 
    for sensor in sensors:
        threadPool.add_thread(sensor.run, sensor.get_sensor_name(), sensor)
    threadPool.start()

    # give the webpage gain access to the sensors.
    server.set_sensor_list(sensors=sensors)

    ########################################################################################


    #Good line if you need to test a thread crashing. 
    # coms.send_request('Data Base', ['save_byte_data', 'NO_TABLE', 0, 'serial listener'])

    #keep the main thread alive for use to see things running. 
    running = True
    while running:
        try:
            threadPool.get_thread_status()
            coms.report_additional_status('Main', f'Main thread Running {datetime.datetime.now()}')
            time.sleep(0.35)
        except KeyboardInterrupt:
            running = False
            print('\n>>> Main thread Shutdown Commanded, use ctrl c if termination takes to long.')        
    
    threadPool.kill_tasks()
     

if __name__ == "__main__":
    main()
