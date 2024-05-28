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
from cmd_inter import cmd_inter # pylint: disable=e0401
from server import serverHandler # pylint: disable=e0401

import system_constants

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

    serial_listener_list = config_data.get("serial_listener_list", [])
    serial_writer_list = config_data.get("serial_writer_list", [])

    swp_board_writer = config_data.get("swp_board_writer", "")
    system_constants.swp_board_writer = swp_board_writer

    APID_pps = config_data.get("APID_pps", "")
    APID_Idle = config_data.get("APID_Idle", "")
    APID_Stat = config_data.get("APID_Stat", "")
    APID_Mode = config_data.get("APID_Mode", "")

    pvn = config_data.get("pvn", "")
    pck_type = config_data.get("pck_type", "")
    sec_header = config_data.get("sec_header", "")
    seq_flags = config_data.get("seq_flags", "")

    mask_pvn = config_data.get("mask_pvn", "")
    mask_pck_type = config_data.get("mask_pck_type", "")
    mask_sec_header = config_data.get("mask_sec_header", "")
    mask_APID_1 = config_data.get("mask_APID_1", "")
    mask_APID_2 = config_data.get("mask_APID_2", "")
    mask_seq_flags = config_data.get("mask_seq_flags", "")
    mask_packet_count_1 = config_data.get("mask_packet_count_1", "")
    mask_packet_count_2 = config_data.get("mask_packet_count_2", "")
    mask_packet_len_1 = config_data.get("mask_packet_len_1", "")
    mask_packet_len_2 = config_data.get("mask_packet_len_2", "")
    
    system_constants.APID_pps = APID_pps
    system_constants.APID_Idle = APID_Idle
    system_constants.APID_Stat = APID_Stat
    system_constants.APID_Mode = APID_Mode
    
    system_constants.pvn = pvn
    system_constants.pck_type = pck_type
    system_constants.sec_header = sec_header
    system_constants.seq_flags = seq_flags
    
    system_constants.mask_pvn = mask_pvn
    system_constants.mask_pck_type = mask_pck_type
    system_constants.mask_sec_header = mask_sec_header
    system_constants.mask_APID_1 = mask_APID_1
    system_constants.mask_APID_2 = mask_APID_2
    system_constants.mask_seq_flags = mask_seq_flags
    system_constants.mask_packet_count_1 = mask_packet_count_1
    system_constants.mask_packet_count_2 = mask_packet_count_2
    system_constants.mask_packet_len_1 = mask_packet_len_1
    system_constants.mask_packet_len_2 = mask_packet_len_2

    uart_0 = config_data.get("uart_0", "")
    uart_2 = config_data.get("uart_2", "")

    hostname = config_data.get("hostname", "")
    display_name = config_data.get("display_name", "")
    server_name_host = config_data.get("server_name_host", "")

    port = config_data.get("port", 0)
    port_serial_1 = config_data.get("port_serial_1", "")
    port_serial_2 = config_data.get("port_serial_2", "")


    ########################################################################################

    ########### Set up threading interface and server ########### 
    coms_name = "Coms/Graphics_Handler"
    coms = messageHandler(logging=False, hostname = hostname, coms_name=coms_name, display_name=display_name, destination="server") # for the pi to decrease load, we are turning off logging. 
    #first start our thread handler and the message handler (coms) so we can start reporting
    threadPool = taskHandler(coms, coms_name=coms_name) # NOTE: we dont need to add a coms task because it add automatically.

    cmd = cmd_inter(coms)
    server = serverHandler(hostname, port, coms, cmd, serial_writer_name=serial_writer_list, listener_name=serial_listener_list, display_name=display_name)

    #Make sure to add the  thread handler to coms so that we can send threading requests
    coms.set_thread_handler(threadPool)

    #Next we want to start the server and give it its own thread
    threadPool.add_thread(server.run, server_name_host, server) #this thread services incoming web request

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
