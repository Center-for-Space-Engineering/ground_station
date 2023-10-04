'''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
'''
import time
from taskHandling.taskHandler import taskHandler
from taskHandling.threadWrapper import threadWrapper
from database.database_control import DataBaseHandler
from server import serverHandler



def main():
    '''
    This module runs everything, its main job is to create and run all of the 
    system objects and classes. 
    '''
    #create a server obj, not it will also create the coms object #144.39.167.206
    server = serverHandler('144.39.167.206', 5000)
    coms = server.getComs()

    #make database object 
    dataBase = DataBaseHandler(coms)

    #now that we have the data base we can collect all of our command handlers.
    server.setHandlers(dataBase)  

    #dummy data generator
    dummy = threadWrapper(coms)  

    #first start our thread handler and the message haandler (coms) so we can start reporting
    threadPool = taskHandler(coms) # NOTE: we dont need to add a coms task because it add automatically.

    #Next we want to start the server and give it its own thread
    threadPool.addThread(server.run, 'Server', server)
    #Now start the data base and give it a thread
    threadPool.addThread(dataBase.run, 'Data Base', dataBase)
    # add dummy data generator, for now this only works for the screen
    threadPool.addThread(dummy.test2, 'Dummy data collector', dummy)

    threadPool.start() #we need to start all the threads we have collected.

    #keep the main thread alive for use to see things running. 
    running = True
    while running:
        try:
            threadPool.getThreadStatus()
            time.sleep(0.35)
        except KeyboardInterrupt:
            running = False
        
    
    threadPool.killTasks()
     

if __name__ == "__main__":
    main()
