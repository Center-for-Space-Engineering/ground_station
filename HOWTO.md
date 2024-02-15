# How to work with the CSE simulator code
In this document I will go through a few examples on how to add functionality to the CSE simulator. The following examples will be covered.
- Adding commands to the server.
- Sending requests to threads.
- Creating a new process and then running it with the parallel architecture.
- Requesting and Inserting data in to the Database.
- Working with the logging system.

Note: When ever you are adding code to the CSE simulator, please make sure to lint your code. All of the `README.md` have instructions for doing this. By doing this you will help future developers be able to read your code. This is not consider optional for CSE coding standers, and must be complete before you push your code to `git`. 

# How to add new commands to the server.
## Architecture Description:
Inside the host folder you will see python files that start with `cmd_`. This prefix tells the server that this is a command and needs to be added into the Architecture at run time. These python class should inherit from the `commandParent.py`. This class has all the basic functions that a command class needs. It is left up to the user to implement these functions. However the `commandParent.py` will help the user structure their code in the correct way.

Note: This example is best understood if you are looking at `src\host\cmd_example.py` while reading though it. 

## Steps:
1. First create a file that follows the correct format `cmd__name_of_new_class`. Make sure you class declaration matches the name of the file.
Note: I recommend copying the `cmd_example.py` file. You do not have to do this, but I believe it is easier to start from here. Consider the following example. \
File name: `cmd_example.py`
```python
    from commandParent import commandParent # pylint: disable=e0401

    class cmd_example(commandParent):
        ...
```
2. The `__init__` function:
```python
       def __init__(self, CMD, coms):
            ...
```
 - CMD: This is the object that ties everything to the server.
 - coms: This object handles all the internal communications.
 - The `__init__` function gets called when the class is created. 
 - First you need to call the `super().__init__(cmd=CMD, coms=coms, called_by_child=True)` this creates the parent class.
 - Create a variable called `self.__commandName`, this tells the server what to call this command.
 - Create an `self.__args = {}`: This is a dictionary of functions you want the server to be able to call. The key in the dictionary is what the server calls. The value for that key should be a function pointer. Note: this is the function the server will call.
 - The following lines are mandatory. They are what actually tie things to the server.
    ```python
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__commandName] = self
        CMD.setCommandDict(dictCmd)
    ```
 - Save the coms object. Do something like the following `self.__coms = coms`.

- Note: Sometimes the user may want to have a class that has more args on its `__init__` function. This is possible if the user simply edits the `cmd_inter.py` class. Here is an example. \
The `cmd_data_collector.py` wants the database as an argument as well. Here is how we add that functionality to the server. 
    ```python
        def collect_commands(self, db):
            '''
                This fuc creates the dynamicImporter (spelled wrong, call it my programming style), after the dynamicImporter goes through the folder searching for any extra commands it adds them into the __commandDict so that the server can leverage them.
            '''
            x = dynamicImporter(self.__coms)
            moduleList = x.get_mod_list()

            for obj in moduleList: #if you want to add any args to the __init__ function other than cmd you will have to change the code in this for loop. I recommend you just use setters. Or find a way not to use them at all.  
                if 'cmd_data_collector' in str(obj):
                    _ = obj(self, self.__coms, db) #Here I need the data base reference for the data base collector class
                else :
                    _ = obj(self, self.__coms) #the reason why I pass cmd into the new class is so that the class can define its own command names and structures.
    ```
You do not need to change the whole function, just add a `elif <condition>:` to the for loop. 
- Note: you may need to pass in additional arguments to the function. 


3. Create the run functions:
  - In most cases the same implementations of `run` and `run_args` in the `cmd_example.py` will work. If you need to customize these further it is left up to the user to do that. However I will give a quick description of the functions.
  - Description: The basic architecture of the `run` functions is simple: it just gets called if no arguments are passed to the server call. The `run_args` calls a function name given to it, and then passes args into that function. It uses the `self.__args` variable to call the functions.
  Note: In most cases the `run_args` is what you want. The `run` function is meant for commands that should be executed right away with not arguments.
4. In this step the user should define their own functions. Each of these functions should be added to the `self.__args` dictionary when it is created in the `__init__` function.
Note: If the function has arguments, the server will pass the argument to your function in a list format. Consider the following example.
```python
    def example_fun(self, args):
        argument1 = args[1]
        argument2 = args[2]
        argument3 = args[3]
```
In this example you can see how you can extract arguments passed by the server. Note: that `args[0]` is not used because it is the function name.\
Note: In some cases you will not want to pass any arguments to your function. The server will still pass an list with only the function name to your function. Therefore you should add the `_` to your function call to avoid a runtime crash. Consider the following example. 
```python
 def my_func_with_no_args(self, _):
    ...
```

5. Implement the `get_args`, this function loops through each key in the `self.__args` dictionary.
 - Note: In many cases your functions will need arguments. I recommend adding something like the following. To convey to the user what the args are.
    ```python
        message = ""
        for key in self.__args:
            if key == 'some key':
                message += f"<url>/{self.__commandName}/{key}/-add your args here-</url><p></p>"
            else :
                message += f"<url>/{self.__commandName}/{key}</url><p></p>"
        return message
    ```
    Note: I have been putting args in between `-` as a way to show to the user that these are args.
 - Implement the `get_args_server`.
  - Note: As with before in many cases your functions will need arguments. I recommend adding something like the following. To convey to the user what the args are.
    ```python
        message = []
        for key in self.__args:
            if key == 'some key':
                message.append({
                'Name' : key,
                'Path' : f'/{self.__commandName}/{key}/-add your args here-',
                'Description' : 'Add description of the function here'    
                })
            else :
                message.append({
                'Name' : key,
                'Path' : f'/{self.__commandName}/{key}',
                'Description' : 'Add description of the function here'    
                })
        return message
    ```
6. Finally implement a to string function. In most cases the following implementation will be sufficient.
    ```python
    def __str__(self):
        return self.__commandName
    ```

# How to send a request to threads.
## Architecture Description:
The general structure of the code is as follows. `taskHandler.py` holds and maintains every thread in the system. The `messageHandler.py` in charge of routing messages from every class to the `taskHandler.py`. Thus when a request is made, it goes to the `messageHandler.py` class, which then sends it to the `taskHandler.py` class which then calls the function on the corresponding thread. In short, what this means is that your class needs to have access to the `messageHandler.py` class in order to send requests to other threads.


Note: in many cases the `messageHandler.py` is called `coms` or `self.__coms`.
## Code:
The code is very simple, consider the following example.
```python
    self.__coms.send_request('task_handler', ['add_thread_request_func', self.run_publisher ,'publisher', self])
```
Lets break the function call into its components.
-  `'task_handler'`: this is the name of the `thread` that you want to send a request to.
- `['add_thread_request_func', `: What follows is a list. The first index in the list is the function to be called, in this cas it is `'add_thread_request_func'`.
- Anything that follows is arguments to be passed into that function.


# How to create a new process and then run it with the parallel architecture.
## Architecture Description:
The Architecture here has a lot built in for you to use already. In most cases you will not have to implement anything on the threading end of things. The way this is accomplished is by having your class inherit from the `threadWrapper.py` class. This class will handle making, sending, and completing requests made by other threads. It also handles reporting its status to the `threadHandler` class. Finally it also implements a `run` function. This basically checks if there are any requests to do, and if not, then it sleeps for a bit and checks again.


Note: In some cases you may need to rewrite the `run` function. You can see an example of this by looking at the `serial_listener.py` class.


## Set upp class structure.
1. Create the `__init__(self, coms, ... )` function.  It is required to pass in the `coms` object. This is the `messageHandler.py` class. It handles all internal communications.
2. Create a `self.__function_dict = {}`: This dictionary should contain any function you want to be called by other threads. If the function is not called by other threads it should not go in the function. Consider the following example:
```python
self.__function_dict = {
    "function_name" : self.function_name
}
```

Note: You should have the key and the function name be the same. There is nothing to force you to do this. However it will make things much easier for people who are reading your code in the future.

3. Then call `super().__init__(self, self.__function_dict)`. This will set up the `threadWrapper.py` class.
Note: If you need to inherit from multiple classes then the class would look like this `threadWrapper.__init__(self, self.__function_dict)`. You can see an example of a class that inherits multiple classes in the `cmd_data_publisher.py`. In this example it is both a thread, and a server command.
4. At this point the user should build the implementation of what they wish to build.
5. There are two ways to start your thread at runtime after you have built the class. The first way is to call it from `main.py`. This is relatively simple. It consists of 3 main calls.
    - Create your class object.
    - call `threadPool.add_thread(-the run function -, class object name, class object. )`
    Note: the class object name is the name that you use to make requests. In other words it is what name the system calls that thread.
    - call `threadPool.start()`. This function can be called multiple times, in multiple places. It just checks all the threads it knows about and if they have not been started it starts them.

### Note: The task Handler will want you to sent your thread status. Just call the `set_status` on the parent `threadWrapper` class. You can set it to `Running` or `Complete`. Anything else is consider an error, and the thread status will report on that. 

## How to request and insert data to the Data Base
## Architecture Description:
The Database is meant to be as easy to use as possible. If you want to create a new table in the Database all you have to do is edit the `src\host\database\dataTypes.dtobj` file. The format is as follows.
### RULES:


1. Any line holding // is ignored. (basically this is how you comment)
2. Any line WITHOUT a tab is considered a data group name, and will be stored into the database as that name.
3. Any line with a TABS will be considered a data type of the data group above it. These types of lines must have a : and >. \
 The format is `<name of data field> : <number of bits> > <data type>`. \
 This format is used to collected data from the bit stream then store it into the database.\
 Data field is the name of the data row to be added to the database. \
 Number of bits is how many bits are in the bit stream from the sensor. \
 data type is the type that the collected data should be converted to.  
4. any line with # is bits to ignore. This is intended for a header or footer. These lines have the following format.
 `# : <number of bits ignored>`.
5. lines that contain the @ are for discontinuous bit streams. This means that bits somewhere else in the bit stream
 that needs to be added to this field. The syntax is: \
 `<name of data field> : <number of bits> > <data type> @ <MSB field> < <LSB field>`\
 `<name of data field> : <number of bits>` \
NOTE: the first field in the file can be the MSB or the LSB. \
NOTE: this is considered the same rule 3, it just tells the bitmap the bits out of order. \
NOTE: if you are going to do multiple discontinuous types mapping to the same element then the intermediate types must have a type cast of NONE.
6. Data fields are collected in the order that they appear in the data group.
7. All field names in a data group MUST BE unique.
8. NO inline comments are allowed.


After that file has been updated to the new Database will be created at run time. (It may be necessary to delete the old DataBase file.)


## Insert Data
To insert data into the database you only need to make a single call to the database. There are three calls you can make
1. `insert_data` is the slowest of the calls, but is also the easiest to use. If you have a very low data rate, this call will work well for your needs. Here is the function docer string.
```
    This func takes in the table_name to insert and a list of data,
    the list must be in the same order that is defined in the .dtobj file.
    args is a list were the first index is the table name and
    the second is the data
    Args:
        [0] : table name
        [1] : list of data
```
Note: This call is for inserting a single row of data.
2. `save_data_group`:  this function is for inserting large amounts of data. It is faster than `insert_data` but is more difficult to use. It is meant to be used in batch, in other words collect several lines of data then insert them all at once.  Here is the function docer string.
```
   This function takes in a list of group to store as a group


            ARGS:
                args[0] : table name
                args[1] : dict of data to store
                args[2] : thread id (used for reporting)
```
3. `save_byte_data`: This function is for saving raw binary data. Here is the function docer string.
```
    This function is in charge of saving byte data (VARBINARY)


            NOTE: This is not a general save like the insert data, it is use case specific.


            args:
                [0] : table name
                [1] : list of bytes
                [2] : caller thread name
```
## Request Data
There are two function to call for requesting data.
1. `get_data`: This is a slow function. It takes a starting index and requests EVERYTHING after that. I would recommend only using this for debugging. Here is the function docer string.
```
    args is a list where the fist index is the table name
    and the second is the start time for collecting the data
    ARGS:
        [0] table name
        [1] table_idx (starting index)
    RETURNS:
        html string with data
    NOTE: This function is NOT meant for large amounts of data! Making a small request to this function will take a long time.
```
2. `get_data_large`: This function runs much faster than the previous and is meant for getting large amounts of data from the Database. It returns a pandas data frame. Here is the function docer string.
```
    args is a list where the fist index is the table name
    and the second is the start time for collecting the data
    ARGS:
        [0] table name
        [1] table_idx (starting index)
        [2] Max rows allowed to be fetched at one time
    RETURNS:
        pandas data obj
    NOTE: This function IS for large amounts of data!
```


Note: All these functions should be called by sending a thread request. See the `How to send a request to threads.` example.

## Working with the logging system.
## Architecture Description:
The logging system has different logs that you can pass, that will then auto populate on the webpage.To pass an object you need to use one of the defined `DTOs` (Data  Transfer Object) in the `src\host\DTOs` folder. The `DTOs` are structured to be python classes so they can be easily imported and used. Consider the following example.  
```python
    import datetime

    from DTOs.logger_dto import logger_dto # pylint: disable=e0401
    from DTOs.print_message_dto import print_message_dto # pylint: disable=e0401
     
    ...

    dto = logger_dto(message="Some logging message here", time=str(datetime.now()))
    dto2 = print_message_dto("Some Message here")
```
To then send the message to the logging system you can simply call the log level you want in with the `coms` (`messageHandler.py`) object. 
```python
    self.__coms.send_message_permanent(dto)
    self.__coms.print_message(dto2)
```
There are a number of different logs you can send, here is a list. 
1. `send_message_permanent` : Theses logs persist through run time. USE SPARINGLY. 
2. `print_message` : Send a log. These logs have a FIFO queue, so the logs will only persist for a short time.  
3. `Report_thread` : This logging is for `taskHandler.py`, the user shouldn't have to use it. 
4. `report_bytes` : This is called by the `serial_listener.py` it is how the system knows how many bytes have been received in a second. Here is an example of reporting a byte count ever second.
```python
    ### Reporting ###
    if time.time() - start > 1: #check to see if it has been one second
        # Report the how many bytes we have received
        self.__coms.report_bytes(self.__byte_count_received)
        self.__byte_count_received = 0
        start = time.time() # set start to the new starting point
```
5. `report_additional_status` : This is for threads or task that  need to report something. Like say if they are connected to the serial port. Or if they are running. Here is an example of how to call this logger.
```python
    self.__coms.report_additional_status(self.__thread_name, " Not Connected!")
```
- Note: In this case no `DTO` is needed. This is an effort to keep things simpler for the user. 
Note: Not all `DTO` types work with all the logger types. Please take care what you pass to the logger. 

