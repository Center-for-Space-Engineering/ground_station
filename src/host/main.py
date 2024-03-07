'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
#python built in imports
import time
import datetime

#python custom imports
from threading_python_api.taskHandler import taskHandler # pylint: disable=e0401 
from database_python_api.database_control import DataBaseHandler # pylint: disable=e0401
from logging_system_display_python_api.messageHandler import messageHandler # pylint: disable=e0401
from cmd_inter import cmd_inter # pylint: disable=e0401
from server import serverHandler # pylint: disable=e0401
from server_message_handler import serverMessageHandler # pylint: disable=e0401

#import DTO for communicating internally
from DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

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
    from sensor_interface_api import system_constants as sensor_config # pylint: disable=e0401

############## Serial Configs ##############
# How many bytes to collect
batch_size_1 = 8
batch_size_2 = 1024

#Names of writers
serial_listener_name = 'serial_listener_one'
serial_writer_name = 'serial_writer_one'

#Names of listeners
serial_listener_2_name = 'serial_listener_two'
serial_writer_2_name = 'serial_writer_two'

#Location of serial port on raspberry pi system
uart_0 = '/dev/ttyS0'
uart_2 = '/dev/ttyAMA2'

#List of interface for system to use
serial_listener_list = [serial_listener_name, serial_listener_2_name]
serial_writer_list = [serial_writer_name, serial_writer_2_name]
############################################

############## Server Configs ##############
hostname = '144.39.167.206' #get this by running hostname -I
# hostname = '127.0.0.1'
port = 8000
server_listener_name = 'CSE_Server_Listener' #this the name for the internal thread that collect server info 
server_name_host = 'CSE_Host' #this is the name for the thread that services all the web requests. 
############################################

############## Data Base configs ###########
data_base = 'Data Base'
############################################

############## Sensor configs ###########
gps_config = { #this dictionary tell the gps sensor how to configure it self.
    'serial_port' : serial_listener_2_name, # Can be the name of a serial listener or None
    'publisher' : 'yes',
    'publish_data' : 'gps_packets',
    'passive_active' : 'passive', #passive sensors only publish when they receive then process data, active sensors always publish on an interval. 
}

sensor_config_dict = { #this dictionary holds all the sensors configuration, NOTE: the key must match the self.__name variable in the sobj_<sensor> object. 
    'gps board' : gps_config, 
}

# set up the config file
sensor_config.interface_listener_list = serial_listener_list
sensor_config.interface_writer_list = serial_writer_list
sensor_config.server = server_listener_name
sensor_config.sensors_config = sensor_config_dict
    
############################################




########## Writer's NOTE ######################
# The Raspberry pi 4b has 5 Uart lines.
# NAME  | TYPE
#_______|_____
# UART0 | PL011
# UART1 | mini UART 
# UART2 | PL011
# UART3 | PL011
# UART4 | PL011
# UART5 | PL011
# NOTE: Each uart has 4 pins assign to it. The first to are TX and RX and the last two are for multi device uart. 
# mini uart does not work with the interface I have set up. However, it would be possible to figure out how to make it work.
# In order to see what pins the uart is using run the following command 'dtoverlay -h uart2'. 
# In order to use the additional uart you first need to enable it, by doing the following. 
#   first: add it to the '/boot/config.txt' try running  vim /boot/config.txt, or nano /boot/config.txt, then add the correct line 
#       to the bottom of the config.txt. It should look something like this dtoverlay=UART3
# Then reboot the pi.
# Then check the /dev/ folder for the new serial over lay. It will probably be something like '/dev/ttyAMA3' or '/dev/ttyS3'. 
# One you find the correct path, that is the path you should pass in to our serial class. (see uart_2 or uart_0)
########## Writer's NOTE ######################

def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''

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

    ########### Set up seral interface ###########  
    # create the ser_listener
    if not NO_SERIAL_LISTENER:
        # Serial listener one
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
    
    ########### Set up sensor interface ########### 
    # create the sensors interface
    importer = sensor_importer() # create the importer object
    importer.import_modules() # collect the models to import
    importer.instantiate_sensor_objects(coms=coms) # create the sensors objects.

    sensors = importer.get_sensors() #get the sensors objects
    
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
            dto2 = print_message_dto('Main thread Shutdown started')
            coms.report_additional_status('Main', dto2)
        
    
    threadPool.kill_tasks()
     

if __name__ == "__main__":
    main()
