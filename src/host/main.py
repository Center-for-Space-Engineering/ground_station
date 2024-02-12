'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
#These are some Debuggin tools I add, Turning off the display is really useful for seeing erros, because the terminal wont get erased every few millaseconds with the display on.
DISPLAY_OFF = True
NO_SERIAL_LISTENER = False
NO_SERIAL_WRITTER = False

import time
import datetime

from threading_python_api.taskHandler import taskHandler
from database_python_api.database_control import DataBaseHandler
from logging_system_display_python_api.messageHandler import messageHandler
from cmd_inter import cmd_inter
from server import serverHandler
from server_message_handler import serverMessageHandler

if not NO_SERIAL_LISTENER:
    from python_serial_api.serial_listener import serial_listener
if not NO_SERIAL_WRITTER:
    from python_serial_api.serial_writter import serial_writter

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto




hostname = '144.39.167.206' #get this by running hostname -I
# hostname = '127.0.0.1'
port = 5000
serial_listener_name = 'serial listener'
serial_writter_name = 'serial writter'
server_listener_name = 'CSE_Server_Listener' #this the name for the interal thread that collect server info 
server_name_host = 'CSE_Host' #this is the name for the thread that services all the web requests. 
data_base = 'Data Base'

def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''
    #create a server obj, not it will also create the coms object #144.39.167.206
    coms = messageHandler(display_off = DISPLAY_OFF, server_name=server_listener_name, hostname=hostname)
    #make database object 
    dataBase = DataBaseHandler(coms, is_gui=False)
    #now that we have the data base we can collect all of our command handlers.
    cmd = cmd_inter(coms, dataBase)
    #now that we have all the commands we can make the server
    #note because the server requires a theard to run, it cant have a dedicated thread to listen to coms like
    #other classes so we need another class object to listen to interal coms for the server.
    server_message_handler = serverMessageHandler(coms=coms)
    server = serverHandler(hostname, port, coms, cmd, serverMessageHandler, server_listener_name, serial_writter_name, serial_listener_name)
    

    #first start our thread handler and the message haandler (coms) so we can start reporting
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

    #collect the data for the serial monitor
    try :
        #first get the data type out of the database 
        #NOTE: Do NOT change the object you get out, it is only a copy and will not change anythin on the datebase end
        requst_num = dataBase.make_request('get_data_type', ['serial_feed'])
        return_val = None
        while return_val is None :
            return_val = dataBase.get_request(requestNum=requst_num)
        serial_data_type = return_val #did this just to make the code easier to read
        batch_size = int (serial_data_type.get_fields()['batch_sample'][0])
    except Exception as e :
        print(e)
        raise Exception("No serial interface defined in dataTypes.dtobj file.\nExample: serial_feed\n\tbatch_sample:1024 > byte\nMust have serial_feed and batch_sample\n")
    
    # create the ser_listener
    if not NO_SERIAL_LISTENER:
        ser_listener = serial_listener(coms = coms, batch_size=batch_size, thread_name=serial_listener_name)
        threadPool.add_thread(ser_listener.run, serial_listener_name, ser_listener)
        threadPool.start() #start the new task

    # create the ser_writter
    if not NO_SERIAL_WRITTER:
        ser_writter = serial_writter(coms = coms, thread_name=serial_writter_name)
        threadPool.add_thread(ser_writter.run, serial_writter_name, ser_writter)
        threadPool.start() #start the new task

    #Good line if you need to test a thread chrashing. 
    # coms.send_request('Data Base', ['save_byte_data', 'NO_TABLE', 0, 'serial listener'])
    

    #keep the main thread alive for use to see things running. 
    running = True
    i = 0
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
