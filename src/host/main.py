'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
import time
from threading_python_api.taskHandler import taskHandler
from database_python_api.database_control import DataBaseHandler
from python_serial_api.serialHandler import serialHandler
from server import serverHandler

hostname = '144.39.167.206' #get this by running hostname -I
serial_handler_name = 'serial listener'
server_name = 'Server'
data_base = 'Data Base'

def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''
    #create a server obj, not it will also create the coms object #144.39.167.206
    server = serverHandler(hostname, 5000)
    coms = server.getComs()

    #make database object 
    dataBase = DataBaseHandler(coms, is_gui=False)

    #now that we have the data base we can collect all of our command handlers.
    server.setHandlers(dataBase)

    #first start our thread handler and the message haandler (coms) so we can start reporting
    threadPool = taskHandler(coms) # NOTE: we dont need to add a coms task because it add automatically.

    #Make sure to add the  thread handler to coms so that we can send threading requests
    coms.set_thread_handler(threadPool)

    #Next we want to start the server and give it its own thread
    threadPool.add_thread(server.run, server_name, server)
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
    ser_listener = serialHandler(coms = coms, batch_size=batch_size, thread_name=serial_handler_name)
    threadPool.add_thread(ser_listener.run, serial_handler_name, ser_listener)
    threadPool.start() #start the new task

    #keep the main thread alive for use to see things running. 
    running = True
    while running:
        try:
            threadPool.get_thread_status()
            time.sleep(0.35)
        except KeyboardInterrupt:
            running = False
        
    
    threadPool.kill_tasks()
     

if __name__ == "__main__":
    main()
