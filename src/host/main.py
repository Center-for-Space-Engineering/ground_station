import time

import sys
sys.path.insert(0, "..")
from  taskHandling.taskHandler import taskHandler
from infoHandling.messageHandler import messageHandler
from server import serverHandler
from database.databaseControl import dataBaseHandler

def main():
    #first start our thread handler and the message haandler (coms) so we can start reporting
    coms =  messageHandler()
    threadPool = taskHandler(coms) # NOTE: we dont need to add a coms task because it add automatically.

    #Next we want to start the server and give it its own thread
    server = serverHandler('144.39.167.206', 5000, coms)
    threadPool.addThread(server.run, 'Server', server)

    threadPool.start() #we need to start all the threads we have collected.

    #keep the main thread alive for use to see things running. 
    running  = True
    while(running):
        try:
            threadPool.getThreadStatus()
            time.sleep(0.5)
        except KeyboardInterrupt:
            running = False
        
    
    threadPool.killTasks()
     

    #Next we wanna start the server and add it as a task we can do. 

if __name__ == "__main__":
    main()