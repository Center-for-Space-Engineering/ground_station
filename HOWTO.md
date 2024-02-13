# How to work with the CSE simulator code
In this document I will set though a few examples on how to add functionality to the the CSE simulator. The following examples will be covered. 
- Adding commands to the server. 
- Sending request to threads.
- Creating a new process and then running it with the parrallel architecture. 
- Requesting and Inserting data to the Data Base.  

# How to add new commands to the server. 
## Architecture Discription:
In side the host folder you will see python that files that start with `cmd_`. This prefix tells the server that this is a command and needs to be added into the Architecture at run time. The python class should inherrit from the `commandParent.py`. This class as all the basic functions that a command class needs. It is left up to the user to implement these functions. However the `commandParent.py` will help the user structure their code in the correct way. 

## Steps:
1. First create a file that follows the correct format `cmd__name_of_new_class`. Make sure you class decleartion matches the name of the file with out the `cmd_` prefix. 
Note: I recomend copying the `cmd_exsample.py` file. You do not have to do this, but I belive it is easier to start from here. 
2. The `__init__` function: 
 - CMD: This is the object that ties everything to the server.
 - coms: This object handles all the internal comuntations. 
 - This function gets called when the class is created. First you need to call the `super().__init__(cmd=CMD, coms=coms, called_by_child=True)` this creates the parent class. 
 - Create a varible called `self.__comandName`, this tells the server what to call this command. 
 - Create an `self.__args = {}`: This is a dictionary of functions you want the server to be able to calls. The key in the dictionary is what the server calls. The value for that key should be a function pointer. Note: this is the function the server will call. 
 - The following lines are manditory. They are what actually tie things to the server. 
    ```python 
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__comandName] = self
        CMD.setCommandDict(dictCmd)
    ```
 - Save the coms object. Do something like the follwoing `self.__coms = coms`.

3. Create the run functions:
  - In most cases the same implementations of `run` and `run_args` in the `cmd_exsample.py` will work. If you need to customizes these further it is left up to the user to do that. However I will give a quick discription of the functions. 
  - Discription: The basic architecture of the `run` functions, is simple it just gets called if no arguments are passed to the server call. The `run_args` calls a function name given to it, and then passes args into that function. It uses the `self.__args` varible to call the functions. 
  Note: In most cases the `run_args` is what you want. The `run` function is ment for commands that should be exicuted right away with not arguments. 
4. In this step the user should define there own functions. Each of these function should be added to the `self.__args` dictionary in when it is created in the `__init__` function. 
Note: If the function has arguments, the server will pass the argument to your function in a list format. Consider the following example.
```python
    def example_fun(self, args):
        argument1 = args[1]
        argument2 = args[2]
        argument3 = args[3]
```
In this example you can see how you can extraxt argements passed by the server. Note: that `args[0]` is not used because it is the function name. 
5. Implement the `get_args`, this function loops though each key in the `self.__args` dictionary. 
 - Note: In many cases your functions will need arguments. I recomend adding something like the following. To convey to the user what the args are. 
    ```python
        message = ""
        for key in self.__args:
            if key == 'some key':
                message += f"<url>/{self.__comandName}/{key}/-add your args here-</url><p></p>" 
            else :
                message += f"<url>/{self.__comandName}/{key}</url><p></p>" 
        return message
    ```
    Note: I have been putting args in between `-` as a way to show to the user that these are args. 
 - Implement the `get_args_server`. 
  - Note: As with before in many cases your functions will need arguments. I recomend adding something like the following. To convey to the user what the args are.
    ```python
        message = []
        for key in self.__args:
            if key == 'some key':
                message.append({ 
                'Name' : key,
                'Path' : f'/{self.__comandName}/{key}/-add your args here-',
                'Discription' : 'Add discription of the function here'    
                })
            else :
                message.append({ 
                'Name' : key,
                'Path' : f'/{self.__comandName}/{key}',
                'Discription' : 'Add discription of the function here'    
                })
        return message
    ```
6. Finally implenet a to string function. In most cases the following implentation will be suffent. 
    ```python
    def __str__(self):
        return self.__comandName
    ```
# How to send a request to threads.
## Architecture Discription:
The general structure of the code is as follows. `taskHandler.py` holds and maintains every thread in the system. The `messageHandler.py` in incharge of routing messages from every class to the `taskHandler.py`. Thus when a request is made, it goes to the `messageHandler.py` class, that then sends it to the `taskHandler.py` class witch then calls the function on the corrisponding thread. In short what this means that your class needs to have access to the `messageHandler.py` class in order to send request to other threads. 

Note: in many cases the `messageHandler.py` is called `coms` or `self.__coms`.
## Code:
The code is very simple consider the following example. 
```python
    self.__coms.send_request('task_handler', ['add_thread_request_func', self.run_publisher ,'publisher', self])
```
Lets break the function call into its components.
-  `'task_handler'`: this is the name of the `thread` that you want to send a request to. 
- `['add_thread_request_func', `: What follows is a list. The first index in the list is the function to be called, in this cas it is `'add_thread_request_func'`.
- Anything that follows is arguments to be passed into that function. 

# How to creating a new process and then running it with the parrallel architecture. 
## Architecture Discription: 
The Architecture here has a lot built in for you to use already. In most cases you will not have to implement anything on the threading end of things. They way this is acomplished is by having your class inherrit from the `threadWrapper.py` class. This class will handel making, send, and completing request made by other threads. It also handles reporting its status to the `threadHandler` class. Finally it also implements a `run` function. This bassically checks if there are any request to do, and if not, then it sleeps for a bit and checks again. 

Note: In some cases you may need to rewrite the `run` function. You can see an example of this by looking at the `serial_listener.py` class. 

## Set upp class structure.
1. Create the `__init__(self, coms, ... )` function.  It is required to pass in the `coms` object. This is the `messageHandler.py` class. It handles all internal communications. 
2. Create a `self.__function_dict = {}`: This dictionary should contain any function you want to be called by other threads. If the function is not called by other threads it should not go in the function. Consider the following example:
```python
self.__fuction_dict = {
    "function_name" : self.function_name
}
```
Note: You should have the key and the function name be the same. There is nothing to force you to do this. However it will make things much easier for people who are reading your code in the future. 
3. Then call `super().__init__(self, self.__function_dict)`. This will set up the `threadWrapper.py` class.
Note: If you need to inherrit from multiple classes then the class would look like this `threadWrapper.__init__(self, self.__function_dict)`. You can see an example of a class that inherrits multiple classes in the `cmd_data_publisher.py`. In this example it is both a thread, and a server command. 
4. At this point the user should build the implementation of what they wish to build.
5. There are two ways to start your thread at run time after you have built the class. The first way is to call it from `main.py`. This is relatively simple. It consists of a 3 main calls. 
    - Create your class object. 
    - call `threadPool.add_thread(-the run function -, class object name, class object. )`
    Note: the class object name, is the name that you use to make request. In other words it is what name the system calls that thread. 
    - call `threadPool.start()`. This function can be called multiply times, in multiple places. It just checks all the threads it knows about and if they havent been started it starts them. 

## How to request and insert data to the Data Base
## Architecture Discription: 
The Data Base is ment to be as easy to use as possible. If you want to create a new table in the Data Base all you have to do is eddit the `src\host\database\dataTypes.dtobj` file. The format is as follows. 
### RULES:

1. Any line holding // is ignored. (basically this is how you comment)
2. Any line WITHOUT a tab is consider a data group name, and will be stored into the data base as that name.
3. Any line with a TABS will be consider a data type of the data group above it. These type of lines must have a : and >. \
 The format is `<name of data feild> : <number of bits> > <data type>`. \
 This format is used to collected data from the bit stream then store it into the database.\
 Data feild is the name of the data row to be added to the data base. \
 Number of bits is how many bits are in the bit stream from the sensor. \
 data type is the type that the collected data should be converted to.  
4. any line with # is ignored bits. This is inteded for a header or footer. These lines have the following format. 
 `# : <number of bits igrnored>`.
5. lines that contain the @ are for discontinuos bit streams. This means that bits somewhere else in the bit stream
 that need to be added to this feild. The syntax is: \
 `<name of data feild> : <number of bits> > <data type> @ <MSB feild> < <LSB feild>`\
 `<name of data feild> : <number of bits>` \
NOTE: the first feild in the file can be the MSB or the LSB. \
NOTE: this is consider the same rule 3, it just tells the bit map the bits out of order. \
NOTE: if you are going to do mulpile discontinuos types mapping to the same elment then the intermediate types must have a type cast of NONE. 
6. Data feilds are collected in the order that they appear in the data group. 
7. All feild names in a data group MUST BE unique. 
8. NO inline comments are allowed. 

After that file has been updated to the new Data Base will be created at run time. (It may be nessary to delete the old Data Base fie.)

## Insert Data
To insert data into the data base you only need to make a single call to the data base. There are three calls you can make 
1. `insert_data` this is the slowest of the calls, but is also the esiest to use. If you have a very low data rate, this call will work well your needs. Here is the function docer string.
```
    This func takes in the table_name to insert and a list of data,
    the list must be in the same order that is defined in the .dtobj file.
    args is a list were the fist index is the table name and 
    the second is the data
    Args:
        [0] : table name
        [1] : list of data
```
Note: This call is for inserting a single row of data.
2. `save_data_group`:  this function is for inserting large amounts of data. It is faster than `insert_data` but is more difficult to use. It is ment to be used in batch, in other words collect serveral lines of data then insert them all at once.  Here is the function docer string. 
```
   This function takes in a list of group to store as a group

            ARGS:
                args[0] : table name
                args[1] : dict of data to store
                args[2] : threaad id (used for reporting) 
```
3. `save_byte_data`: This function is for saving raw binary data. Here is the function docer string.
```
    This function is in charge of saving byte data (VARBINARY)

            NOTE: This is not a genreal save like the insert data, it is use case spesific. 

            args:
                [0] : table name
                [1] : list of bytes
                [2] : caller thread name
```
## Request Data
There are two function to call for requesting data. 
1. `get_data`: This is a slow function. It takes a starting index and request EVERYTHING after that. I would recomend only using this for debugging. Here is the function docer string.
```
    args is a list where the fist index is the table name 
    and the second is the start time for collecting the data
    ARGS:
        [0] table name
        [1] table_idx (starting indx)
    RETURNS:
        html string with data
    NOTE: This function is NOT meant for larg amouts of data! Make request small request to this function of it will take a long time. 
```
2. `get_data_large`: This function runs much faster than the previous and is ment for getting large amounts of data from the Data Base. It returns a pands data frame. Here is the function docer string.
```
    args is a list where the fist index is the table name 
    and the second is the start time for collecting the data
    ARGS:
        [0] table name
        [1] table_idx (starting indx)
        [2] Max rows allowed to be fecthed at one time
    RETURNS:
        pandas data obj
    NOTE: This function IS for larg amouts of data! 
```

Note: All these function should be called by sending a thread request. See the `How to send a request to threads.` example. 