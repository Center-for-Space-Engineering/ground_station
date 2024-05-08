'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
#python built in imports
import time
import yaml

#python custom imports
from threading_python_api.taskHandler import taskHandler # pylint: disable=e0401
from python_serial_api.serial_listener import serial_listener # pylint: disable=e0401
from python_serial_api.serial_writer import serial_writer # pylint: disable=e0401
from logging_system_display_python_api.messageHandler import messageHandler # pylint: disable=e0401
from data_publisher import data_publisher # pylint: disable=e0401

def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''

    ###################### Import from the Yaml file #########################
    # Load the YAML file
    with open("main.yaml", "r") as file:
        config_data = yaml.safe_load(file)

    batch_size_1 = config_data.get("batch_size_1", 0)
    batch_size_2 = config_data.get("batch_size_2", 0)

    serial_listener_name = config_data.get("serial_listener_name", "")
    serial_writer_name = config_data.get("serial_writer_name", "")
    serial_listener_2_name = config_data.get("serial_listener_2_name", "")
    serial_writer_2_name = config_data.get("serial_writer_2_name", "")

    uart_0 = config_data.get("uart_0", "")
    uart_2 = config_data.get("uart_2", "")

    hostname = config_data.get("hostname", "")

    port_serial_1 = config_data.get("port_serial_1", "")
    port_serial_2 = config_data.get("port_serial_2", "")


    ########################################################################################

    ########### Set up threading interface ########### 
    coms = messageHandler(logging=False, hostname=hostname) # for the pi to decrease load, we are turning off logging. 
    #first start our thread handler and the message handler (coms) so we can start reporting
    threadPool = taskHandler(coms) # NOTE: we dont need to add a coms task because it add automatically.

    #Make sure to add the  thread handler to coms so that we can send threading requests
    coms.set_thread_handler(threadPool)

    threadPool.start() #we need to start all the threads we have collected.
    ########################################################################################


    ########### Set up seral interface ###########  
    # create the ser_listener
    # Serial listener one
    ser_listener = serial_listener(coms = coms, batch_size=batch_size_1, thread_name=serial_listener_name, stopbits=1, pins=uart_0)
    threadPool.add_thread(ser_listener.run, serial_listener_name, ser_listener)

    # Serial listener two
    ser_2_listener = serial_listener(coms = coms, batch_size=batch_size_2, thread_name=serial_listener_2_name, baudrate=9600, stopbits=1, pins=uart_2)
    threadPool.add_thread(ser_2_listener.run, serial_listener_2_name, ser_2_listener)
    
    threadPool.start() #start the new task

    # create the ser_writer
    # Serial writer one
    ser_writer = serial_writer(coms = coms, thread_name=serial_writer_name, pins=uart_0)
    threadPool.add_thread(ser_writer.run, serial_writer_name, ser_writer)

    # Serial writer two
    ser_2_writer = serial_writer(coms = coms, thread_name=serial_writer_2_name, baudrate=9600, stopbits=1, pins=uart_2)
    threadPool.add_thread(ser_2_writer.run, serial_writer_2_name, ser_2_writer)
    
    threadPool.start() #start the new task
    ########################################################################################

    ########### Set up publishers for our listeners ###########
    data_publisher_one = data_publisher(coms=coms, live_feed=serial_listener_name)
    data_publisher_two = data_publisher(coms=coms, live_feed=serial_listener_2_name)

    print(data_publisher_one.start_data_publisher([port_serial_1, 'live']))
    print(data_publisher_two.start_data_publisher([port_serial_2, 'live']))
    ########################################################################################


    #Run the main loop handle session, testing, and threading overhead
    running = True

    while running:
        try:
            threadPool.get_thread_status() #this commands the threads to report to the server how they are running. 
            time.sleep(1) # sleep for one second.
        except KeyboardInterrupt:
            running = False
            print('\n>>> Main thread Shutdown Commanded, please wait.')        
    
    threadPool.kill_tasks()
     

if __name__ == "__main__":
    main()
