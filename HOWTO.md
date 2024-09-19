# How to work with the CSE simulator code
In this document I will go through a few examples on how to add functionality to the CSE simulator. The following examples will be covered.
- Adding commands to the server.
- Sending requests to threads.
- Creating a new process and then running it with the parallel architecture.
- Requesting and Inserting data in to the Database.
- Working with the logging system.
- Adding New serial lines to the system.
- Adding Sensors to the system.

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
Note: In most cases all your functions will only need to return a string. 
Note: If the user wishes to download a file as part of the function this can be done simply but setting some arguments on the return value. Consider the following example. 
```python
return {
        'text_data': f'The last line fetched was {last_db_index}',
        'file_data': dto,
        'download': 'yes',
        'file_extension' : 'txt', 
    }
```
- `text_data`: This argument is what shows up on webpage as what the command returns. 
- `file_data`: This argument is the data that will be downloaded to the users computer. 
- `download` : if the arg is `yes` this tells the web page to download the information. 

Note: if you wish to download bin data here is an example:
```python
    import base64
    ...

    base64_data_combined = base64.b64encode(data_combined).decode('utf-8')
    return {
        'text_data': f'The last line fetched was {last_db_index}',
        'file_data': base64_data_combined,
        'download': 'yes',
        'file_extension' : 'bin', 
    }
```
Note: you MUST do the encoding on the bin data. 

Note: That the users wishes to return a `.bin` file. Also note that the `file_data` has to be encoded in the correct why or it will not work. 

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

The following is an example of sending multiply request and then collecting there responses. 
```python
        data_obj = []
        request_list = [] #keeps track of all the request we have sent. 
        for request in list_of_request_to_make: #Assume the thread name is in the first index, and the function to run is in the second index, the third index is the args for the request.
            #make a request to switch the serial port to new configurations
            request_list.append([name, self.__coms.send_request(request[0], [request[1], request[2]]), False]) #send the request to the port`
        all_request_serviced = False
        while not all_request_serviced:
            all_request_serviced = True
            #loop over all our requests
            for i in range(len(request_list)):
                data_obj_temp = None
                # if we haven't all ready seen the request come back  check for it. 
                if not request_list[i][2]: 
                    data_obj_temp = self.__coms.get_return(request_list[i][0], request_list[i][1])
                    # if we do get a request add it to the list and make the request as having been serviced. 
                    if data_obj_temp != None:
                        request_list[i][2] = True
                        data_obj.append(data_obj_temp)
                all_request_serviced = all_request_serviced and request_list[i][2] #All the request have to say they have been serviced for this to mark as true. 
```


# How to create a new process and then run it with the parallel architecture.
## Architecture Description:
The Architecture here has a lot built in for you to use already. In most cases you will not have to implement anything on the threading end of things. The way this is accomplished is by having your class inherit from the `threadWrapper.py` class. This class will handle making, sending, and completing requests made by other threads. It also handles reporting its status to the `threadHandler` class. Finally it also implements a `run` function. This basically checks if there are any requests to do, and if not, then it sleeps for a bit and checks again.


Note: In some cases you may need to rewrite the `run` function. You can see an example of this by looking at the `serial_listener.py` class.


## Set up class structure.
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
```python
    data_dict = {
        'felid_name' : [... data list ...]
    }
    self.__coms.send_request('Data Base', ['save_data_group', self.__thread_name, data_dict, self.__thread_name])
```
3. `save_byte_data`: This function is for saving raw binary data. Here is the function docer string.
```
    This function is in charge of saving byte data (VARBINARY)


            NOTE: This is not a general save like the insert data, it is use case specific.


            args:
                [0] : table name
                [1] : dictionary of data to save, where the key is the name of the felid, and the mapped value is a list of bytes. 
                [2] : caller thread name
```
Example :
```python
    data_dict = {
        'felid_name' : [... byte list ... ]
    }
    self.__coms.send_request('Data Base', ['save_byte_data', self.__thread_name, data_dict, self.__thread_name])
```
NOTE: You can only have single column tables with byte data. 
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


## Adding New serial lines to the system:
## Architecture Description:
There are 2 basic steps for adding serial ports to the code. 
1. Enable them on the pi
2. Add them to the code.


### Step one:
The Raspberry pi 4b has 5 Uart lines.
| NAME  | TYPE |
| ----- | ----- |
| UART0 | PL011 |
| UART1 | mini UART |
| UART2 | PL011 |
| UART3 | PL011 |
| UART4 | PL011 |
| UART5 | PL011 |

NOTE: Each uart has 4 pins assign to it. The first to are TX and RX and the last two are for multi device uart. \
mini uart does not work with the interface I have set up. However, it would be possible to figure out how to make it work.\
In order to see what pins the uart is using run the following command 'dtoverlay -h uart2'. \
In order to use the additional uart you first need to enable it, by doing the following. \
first: add it to the '/boot/config.txt' try running  vim /boot/config.txt, or nano /boot/config.txt, then add the correct line to the bottom of the config.txt. It should look something like this dtoverlay=UART3 \
Then reboot the pi.\
Then check the /dev/ folder for the new serial over lay. It will probably be something like '/dev/ttyAMA3' or '/dev/ttyS3'. 

### Step two:
Adding it to the system is pretty simple (I hope...). \
NOTE: You add all these variables to the `main.yaml` file.  Then you will import them in the main file. This is the arcature we are using, so please stick to it. 
Example `main.yaml`
```yaml
# Serial Configs
batch_size_1: 8
batch_size_2: 32

serial_listener_name: &serial_listener_name serial_listener_one
serial_writer_name: &serial_writer_name serial_writer_one

serial_listener_2_name: &serial_listener_2_name serial_listener_two
serial_writer_2_name: &serial_writer_2_name serial_writer_two

# Location of serial port on Raspberry Pi system
uart_0: /dev/ttyS0
uart_2: /dev/ttyAMA2

# List of interfaces for system to use
serial_listener_list:
  - *serial_listener_name
  - *serial_listener_2_name

serial_writer_list:
  - *serial_writer_name
  - *serial_writer_2_name

```
Example decoding in main file:
```python
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

    serial_listener_list = config_data.get("serial_listener_list", [])
    serial_writer_list = config_data.get("serial_writer_list", [])
    ########################################################################################
```
Fist crate a `batch_size`. This variable will tell your listeners how many bytes to collect before submitting a save request to the data base. The larger this number the faster the data base can save the data (up to 8000), however the smaller the number the faster you will see the bytes come out the other end of the pipe. One Final note, for speed the listener will collect 10 samples of the `batch_size` then send that data to be saved by the data base. I did include a 5 second time out so if the listener stops receiving data, it will eventually save it to the data base. 

Then create a name for the listener and writer. (If you need both, you can just have one or the other.) Add the names to the respective lists `serial_listener_list` and `serial_writer_list`. Then create a file path variable for the system to use. Example `uart_2 = '/dev/ttyAMA2'`. \
Note: Adding the names of your serial objects to `serial_listener_list` and `serial_writer_list` is what will tell the server and the sensors api what serial lines they have. `serial_listener_list` gets a graph on the webpage as well. \
After you have created the need variables, All you need to do is create the classes.  Find where `########### Set up seral interface ###########` Under this section you wil see where the serial listeners and writers are made, create the class and then add it to the thread pool. The thread pool is already started in the code I wrote, but if you are adding the code somewhere else, you will need to tell the thread pool to start.\
Example listener:
```python
        ser_2_listener = serial_listener(coms = coms, batch_size=batch_size_2, thread_name=serial_listener_2_name, baudrate=9600, stopbits=1, pins=uart_2)
        threadPool.add_thread(ser_2_listener.run, serial_listener_2_name, ser_2_listener)
        
        threadPool.start()
```
Example writer: 
```python
        ser_2_writer = serial_writer(coms = coms, thread_name=serial_writer_2_name, baudrate=9600, stopbits=1, pins=uart_2)
        threadPool.add_thread(ser_2_writer.run, serial_writer_2_name, ser_2_writer)
        
        threadPool.start()

```
## How to add a sensor to the system.
## Architecture Description:
Authors Note: This example is write to our data scientist, who are quite smart, but in some cases do not have the same level of programming experience. Therefore I will spend quite a bit of time explaining common programming concepts. I do not do this to be condicending or demeaning, but simple to make things as easy a possible for our team.  

The system supports dynamically adding sensors. A sensors is anything that consumes and/or produces data. The system also supports producing sensor chains. For example: serial line -> L0 processing -> L1 processing. The sensors also allow for dynamically graphing your data. The sensors also support data insertion into the Data Base. Finally they will also handel shipping all that data to the webpage. This should allow for real time debugging on the system. However the primary purpose of sensors is to facilitate unit testing.

Note: We have designed a special type of sensor that allows you to import a data for a dictionary file and automatically parse a raw bit stream. The steps for creating this are a little different from the following and will be explained after the basic steps. Under the section call `Unpacking Sensors`.

### Step One:
Set up a config dictionary in the `main.yaml`. This tells the system how to handle this sensor. Consider the following example:
```yaml
# Sensor configs
sensor_config_dict:
  # This dictionary holds all the sensors configuration, NOTE: the key must match the self.__name variable in the sobj_<sensor> object. 
  # NOTE: The key here becomes part of a file name so make sure you use valid chars in the name. 
  gps_board:
      # This dictionary tells the GPS sensor how to configure itself.
      tap_request: [*serial_listener_2_name]  # Index in the list can be the name of a serial listener or any sensors whose data you want to listen to or None (Example for none: None) 
      publisher: 'yes'
      publish_data_name: 'gps_packets'  # NOTE: NOT used right now
      passive_active: 'passive'  # Passive sensors only publish when they receive then process data, active sensors always publish on an interval.
      interval_pub: 'NA'  # We are not using this param because we are a passive publisher, however if the sensor is active we will need to set this interval to the desired rate. 
      Sensor_data_tag: 0x24  # Hexadecimal representation of '$' This parameter is for the sensor class to search data from the tag, whether it comes from the serial line or from other sensors on the system.

```
NOTE: Any new sensor needs to go under the `sensor_config_dict` this is what tells the system there is a sensor to add.\
Argument expiation: 
1. `tap_request` : This parameter is a list of the classes you would like to listen too. (can be serial lines or sensors.) You are allowed to have more than one tap requests. 
2. `publisher` : `yes` or `no` This parameter tells the system where or not this sensors will publish data. 
3. `publish_data_name` : This is the name of your published data. 
4. `passive_active` : `passive` or `active` if you are passive sensor you need to call the publish function your self. If it is an active sensor any data you put in the sensors using the `set_publish_data` function will be automatically punished on some interval. NOTE: in both cases you need to call the `set_publish_data` data in order for data to be published. \
    Example Active :
    ```python
        data = ...
        sensor_parent.set_publish_data(data)
        sensor_parent.publish()
    ```
    Example Passive :
    ```python
        data = ...
        sensor_parent.set_publish_data(data)
    ```
    NOTE: Because the data is published on an interval be careful not to overwrite your data.  There is a function you can check to see if the data has been published. It is called `set_publish_data`.
5. `interval_pub` : This parameter is the interval you will publish on if you are an active sensor. Can be `NA` or `<some data>`.
6. `Sensor_data_tag` : This parameter is not used by the system. It is meant to be used by the class you will  write if you so choose. Basically I put it there so that other users can see what data tag the sensor is searching for in the incoming data stream.

NOTE: If you would like to add, addition arguments to your config dictionary, you can, the system wont care. But all of the basic arguments should be present. 

### Step Two:
Take note of the key you use it is super important. When you make the `sobj_-sensor-` class (step 3) you need to make sure that the `self.__name` variable must be  the same as the key or the system will be unable to match your config file to the sensor class you build. IN the example above the key is `gps_board`

### Step Three:
Now it is time to create the `sobj_-sensor-` class. I will first example how to set up the class, then I will example the tools you have to. Every sensors implementation will be different. So I wont be able to provide as detailed instructions, but I will do my best to give you enough information to be able to build a sensor, even if you have little to no programming experience.

Okay lets talk setting up the sensor:
-  The file name is very import, the fist part of the name must be `sobj_` and it must be located in the `sensor_interface_api` folder. The `sobj_` tells the system that this is a sensor object and to import it at run time. Consider some example sensor class sames:

- `sobj_cool_sensor.py`
- `sobj_will_justin_use_this.py`
- `sobj_l__one_processing.py`

### Consider the following example:
```python
from sensor_interface_api.sensor_parent import sensor_parent # pylint: disable=e0401
import system_constants as sensor_config # pylint: disable=e0401
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class sobj_gps_board(sensor_parent):
    def __init__(self, coms):
        self.__name = 'gps_board'
        self.__graphs = ['num gps packets received']
        self.__config = sensor_config.sensors_config[self.__name]
        self.__coms = coms
        self.__serial_line_two_data = []
        self.__data_lock = threading.Lock()
        

        ...
```
#### First consider the imports:
- I believe these are the three basic import you will need. The first one is the sensor_parent, this is the class that will handel all the background stuff describe in the Architecture section. The following line tells python to use all the code I wrote in the `sensor_parent` class. THis is called inheritance. Programers will talk about inheritance using family structures, the class I inheritance from is my 'parent class', the class that inheritances from me is my 'child' class. 
```python 
class sobj_gps_board(sensor_parent):
```
- The next import `sensor_config` imports the sensor configs that you set up in the main file. 
- The final import `print_message_dto` is the way you can send logs on the system. (There are many example on using this class. SEe the Working with the log system example.) \
#### Now consider the class declaration: 
- Notice that `class` name must match the file name. Consider the following class declarations to match the above file names. 
```python
class sobj_cool_sensor(sensor_parent):
```
```python
class sobj_will_justin_use_this(sensor_parent):
```
```python
class sobj_l__one_processing(sensor_parent):
```
- Notice that every class declaration has the following `(sensor_parent)`. This is called inheritance, I wont get into it too much here, however it basically it tells the system how sensors should look, and uses all the code I wrote for them. 

#### Now consider the `__init__` function:
The `__init__` function gets called when you create a class object, you can think of it as a set up function. 
- First think to notice is that `self.__name = 'gps_board'` if you notice `'gps_board'` is the same as the key name in the dictionary, in our earlier example. 
- Second consider the `self.__graphs`, this variable contains a list of graph names you would like the sensor page to have. YOU DO NOT have to do anything else to create graphs, one you make this variable you just need to pass it to the parent class, witch I will show you how to do later. 
- Next `self.__config = sensor_config.sensors_config[self.__name]`  this line will always be the same. It just grabs your config file from the global config file. 
- Then consider `self.__coms = coms` this is the internal coms for the whole system. For more information see `How to send request to threads` and/or `Working with the logging system` and/or `logging_system_display_python_api/READ.md`.
- The file two variable are two I include because I think that variables like this will be used quite often. The first is `self.__serial_line_two_data` this is a list of data that you can but data into. The next variable is `self.__data_lock = threading.Lock()` this variable is called a mutex lock. You need to add the following line in order to make a mutex lock `import threading`. NOTE: There is a section later witch talks in depth about how to use a mutex lock. We will get to how to use them a little later. 

## Step 4:
Now it is time for more advanced class structuring.

### Creating tables to save your data
You are going to want to save the data your sensor makes. I have built automated tools to help you do this, but they need some explanation. First lets create the table structure in the data base. \
Here is an example:
```python
# the structure here is a dict where the key is the name of the table you want to make and the value is a list of list that has your column information on each sub index.
# the column structure is [<table name>, bit count (zero if you dont care), type (int, float, string, bool, bigint, byte)]
self.__table_structure = {
    f'processed_data_for_{self.__name}' : [['gps_packets', 0, 'string'], ['test_data', 10, 'int']],
    f'processed_data_for_{self.__name}_table_2' : [['gps_packets', 0, 'string'], ['test_data', 10, 'int']],

}
```
- The structure is a dictionary, then the key is the name of the table you want to make. The value the key maps to is a list of list. Each sub list is a description of how a column in that table should be structured. The fist index in the sub list is the name of the data in that column. The next index only matters if you are storing byte data and it is the number of bytes to store, the final index is the type of the data.\
NOTE: The Database has about 32 bytes of over head per row (index for that row) plus what ever `sqlite3` wants. Bottom line, try not to create rows with very little data in them, like a row of single bytes because you will have a massive memory explosion. 
- NOTE: the table will be created and archived when the system boots, because of this archive your table structure and data should persist across run cycles.  
- NOTE: I will explain saving into the database when I talk about processing the data. 

## Step 5:
Okay now we have set up the sensor class, it is time to create the parent class to take advantage of all the prebuilt functions. Here is the commad to do it. 
```python
    # NOTE: if you change the table_structure, you need to clear the database/dataTypes.dtobj and database/dataTypes_backup.dtobj DO NOT delete the file, just delete everything in side the file.
    sensor_parent.__init__(self, coms=coms, config= self.__config, name=self.__name, graphs=self.__graphs, max_data_points=100, db_name = sensor_config.database_name, table_structure=self.__table_structure)
    sensor_parent.set_sensor_status(self, 'Running')
```
NOTE: That I have passed in all the variables that we made in earlier steps, with this information the `sensor_parent` can build your sensor class now. The only thing you have to do now is process the data. 
NOTE: The code from steps 3 through 5 all go into your `__init__` function. So at this point you should have the following:
1. A file that starts with `sobj_` and ends with `.py` in the `sensors_interface_api` folder.
2. The three basic imports (4 if you are using `threading`).
3. The class should look something like this. 
```python
import threading
import copy

from sensor_interface_api.sensor_parent import sensor_parent # pylint: disable=e0401
import system_constants as sensor_config # pylint: disable=e0401
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class sobj_gps_board(sensor_parent):
    def __init__(self, coms):
        self.__name = 'gps_board'
        self.__graphs = ['num gps packets received']
        self.__config = sensor_config.sensors_config[self.__name]
        self.__serial_line_two_data = []
        self.__data_lock = threading.Lock()
        self.__coms = coms

        # the structure here is a dict where the key is the name of the table you want to make and the value is a list of list that has your row information on each sub index.
        # the row structure is [<table name>, bit count (zero if you dont care), type (int, float, string, bool, bigint, byte)]
        self.__table_structure = {
            f'processed_data_for_{self.__name}' : [['gps_packets', 0, 'string'], ['test_data', 10, 'int']],
            f'processed_data_for_{self.__name}_table_2' : [['gps_packets', 0, 'string'], ['test_data', 10, 'int']],

        }

        # NOTE: if you change the table_structure, you need to clear the database/dataTypes.dtobj and database/dataTypes_backup.dtobj DO NOT delete the file, just delete everything in side the file.
        sensor_parent.__init__(self, coms=coms, config= self.__config, name=self.__name, graphs=self.__graphs, max_data_points=100, db_name = sensor_config.database_name, table_structure=self.__table_structure)
        sensor_parent.set_sensor_status(self, 'Running')

```
NOTE: I haven't talked about this yet but `copy` is a use import to use with `threading`.

## Step 6:
Now its time to process our data. The way things work is every time one of the taps you requested is received the `sensor_parent` will call the process data function. It will also pass in a parameter called `event`. The `event` parameter is what data was received. The format of the events is as follows:
`data_received_for_<name of tap request>` so in our example we asked for one tap request called `serial_listener_connect_to_gps_board`. Thus we have one event called `data_received_for_serial_listener_connect_to_gps_board`. Your class must have a `process` function implemented. Let me show you how to implement them. 
```python
def process_data(self, event):
    '''
        This function gets called when one of the tap request gets any data. 

        NOTE: This function always gets called no matter with tap gets data. 
    '''
```
- NOTE: This function declaration will ALWAYS be the same. What is actually happening here is we are over ridding a function the parent class already has. (This is one of the features of inheritance.)

Now that we know about event we can call other processing functions based on the event like so:
```python
if event == 'data_received_for_serial_listener_connect_to_gps_board':
    temp = sensor_parent.get_data_received(self, self.__config['tap_request'][0])
```
NOTE: You do not need to worry about threading here, because I have already done this in the background for you. 

Now in the above example we are assuming that the data is coming in all nice and package for us. However this is not the case when it is coming from the serial lines. This is because the serial line just grab a bunch of data then ship it. I have built a function to help but the data back together, but it may not work in all situation. However here is an example of how to use it. 

```python
if event == 'data_received_for_serial_listener_two':
    temp, start_partial, end_partial = sensor_parent.preprocess_data(self, sensor_parent.get_data_received(self, self.__config['tap_request'][0]), delimiter=self.__config['Sensor_data_tag'], terminator=self.__config['Sensor_terminator_data_tag']) #add the received data to the list of data we have received.
    with self.__data_lock:
        if start_partial and len(self.__serial_line_two_data) > 0: 
            self.__serial_line_two_data[-1] += temp[0] #append the message to the previous message (this is because partial message can be included in batches, so we are basically adding the partial messages to gether, across batches. )
            self.__serial_line_two_data += temp[1:]
        else :
            self.__serial_line_two_data += temp
        data_ready_for_processing = len(self.__serial_line_two_data) if not end_partial else len(self.__serial_line_two_data) - 1 #if the last packet is a partial pack then we are not going to process it.  
        
        self.__coms.send_request('task_handler', ['add_thread_request_func', self.process_gps_packets, f'processing data for {self.__name} ', self, [data_ready_for_processing]]) #start a thread to process data
```
NOTE: This is where it might be useful to use the 'Sensor_data_tag' parameter from the config dictionary in step 1, but it is not required.
Lets look at the processing steps:
1. get the data  `get_data_received`.
2. put the data into packets based on the give delimiter. `preprocess_data`\
NOTE: This function assumes that your data has only one delimiter, and always has a delimiter between packets. IF your packets have a different structure, you may have to write your own `preprocess_data` function. \
REMINDER: If your data comes in as a list of packets, (witch in may cases you can publish it that way) you do not need to do any preprocessing. Also I am only putting things in to nice packets because it makes threading MUCH easier. If you do not care, then you do not need to do any preprocessing.
3. Next I am going to add the data into a class variable for processing. There are two important things to notice here. First I use a mutex lock called  `self.__data_lock`, I have a whole section Mutex locks after this. Please read it if you have never used a mutex lock before. 

Now it is time to actually process our data, I recommend calling another function on another thread to do this. This will not always be required, but it you do this it will make it so that you wont drop packets because you are processing data, when the parent class is trying to save data. I have worked very hard to make creating new threads as easy as possible, and there is another example in this file called  `How to create a new process and then run it with the parallel architecture`. However it 90 percent of use cases you will only need a single line command to multithread your processing. Consider the following line of code:
```python
self.__coms.send_request('task_handler', ['add_thread_request_func', self.process_gps_packets, f'processing data for {self.__name}', self, [len(self.__serial_line_two_data)]]) #start a thread to process data

```
Lets break down the command:
1. `self.__coms.send_request` : This function sends request to other class running on the system.
2. `'task_handler'` : Target class
3. `'add_thread_request_func'` : The function we want to run, this particular function as a thread to the thread pool. \
NOTE: 1,2, and 3 will always be the same. 
4. `Name of function to run` : in our case it is `self.process_gps_packets`.
5. `Name that the system will call this process` : in our case `f'processing data for {self.__name}'`.
6. `class object` : The `task_handler` needs this to run, this because the grandparent of your class is the `thread_wrapper` class, witch sets up all the need functionality for threading. 
7. `arguments for the function you want to run on the thread` : in this case I pass in the number of packets to process. (If you read Mutex Locks section you will see why I pass in `len(self.__serial_line_two_data)`)

NOTE: items 3 - 7 are in a list, this makes things a little faster in python. (Well at least I think they do).

In order to be safe you need to use Mutex locks to protect your data in the function you just called here is a simple example:
```python
def process_gps_packets(self, num_packets):
    '''
        This function rips apart gps packets and then saves them in the data base as ccsds packets.  
    '''
    
    sensor_parent.set_thread_status(self, 'Running')
    with self.__data_lock: #get the data out of the data storage. 
        temp_data_structure = copy.deepcopy(self.__serial_line_two_data[:num_packets])
```

NOTE: Notice how I copy the data, this is needed to make sure that you protect your data when threading.

#### After this point it is up to the user to process the data. 

## There are a few things left that will be of use to you as you build your processing though, namely writing data to the database, graphing data, and publishing data. 

#### - Writing data to the database
I wrote a function to automatically do this for you if you are saving any data that is not byte data. If you want to save byte data please see the `How to request and insert data to the Data Base` example. \
Here is an example of saving your data. Assume the our table structure is `f'processed_data_for_{self.__name}' : [['gps_packets', 0, 'string'], ['test_data', 10, 'int']],`: 
```python
data = {
            'gps_packets' : ['hello', 'hello'],
            'test_data' : [10, 10]
        }

sensor_parent.save_data(self, table = f'processed_data_for_{self.__name}', data = data)
```
- `table` is the name of the table you want to save into, the data is the data. 
- NOTE: data is a dictionary of the data you want to save, where the key is the column name, and the value mapped to is a list of data points to insert. I wrote it this way so that it would be easier to processes by type then save it all at once. Make sure your list are the same lengths.
- NOTE: If your any of your columns contain byte data you need to call `sensor_parent.save_byte_data`, following the same structure. Reminder saving byte data only works for tables that only have one column. 

#### - Graphing data
Graphing is a simple x, y graph. After talking with our scientist, I assumed this would be sufficient for debugging. It should be easy to use, simply call: 
```python
y = [ ... ]
x = [ ... ] 
sensor_parent.add_graph_data(self, graph=self.__graphs[0], x=x, y=y)
``` 
1. `graph` is the name of one of the graphs you created in step 3.
2. The x and y data can be a list data that you wish to graph. I have tested up to about 10,000 points and the graphs seem to do fine. If you are graphing and nothing is happening on the web page, it is probably due to an internal error, try changing your data format. If that doesn't work you probably have a bigger problem. 

### - Publishing data
Your published data can take any format, I would recommend organizing it so that it is easy to process by other sensors but it is up to you. 
if you are a passive publisher (part 1):
```python
sensor_parent.set_publish_data(self, data=data)
sensor_parent.publish(self)
```
if you are a active publisher:
```python
sensor_parent.set_publish_data(self, data=data)
```
You may want to check to make sure you have publisher your last batch of data first, if you want to check to see if you data has been published call 
```python
sensor_parent.has_been_published(self)
```

## Unpacking Sensors
Often times when we add a new prefill to the system. (Often times a raspberry pi.) We will have a defined dictionary for all the packet types. In this we can build a lot of sensors with very little work. Allowing use to parse raw packets into the database automatically. This section will walk though the process for setting this up. 

### Step 1: Create a yaml file from the dictionary
Go to the `processing_telemetry_dictionary` git repo. This repo has instructions on how to export the y


## Mutex Locks:
Mutex locks serve to protect your data when multiple threads want to access your data. Basically if multiple threads try and access a variable at the same time wired things can happen. So we made mutex locks to prevent data loss and data corruption. Python is pretty easy to use mutex lock, just uses the `with` command. (See examples) Be warned though it is really easy to take a nice parallel program and turn it into a 'single' threaded program by abusing mutex locks.  \
Consider the following example: 
```python
import threading 

shared_list = [1, 2, 3]
mutex = threading.Lock()

#thread one 
def do_something(lock):
    with lock: #get the mutex lock
        # do something with shared list
    #Once we leave the with indentation we release the mutex lock. 

#thread two 
def do_something_two(lock):
    with lock:
        # do something with shared list

#run thread one and two.
```
In the above example threading does NOTHING for use, in fact it will increase your execution time. This is because thread one gets the mutex lock does all its processing, then releases the mutex lock. So thread two has to wait for thread on to finish, then it can begin. This is really easy to do in code. To avoid this problem I have a rule of thumb that I like to follow, it is not always true but I have found it to be useful. The rule is if you have more than one line of code in a mutex lock you have too many lines of code in your mutex. Now lets revise our example to follow this rule so wwe can take advantage of threading. 

```python
import threading 
import copy

shared_list = [1, 2, 3]
mutex = threading.Lock()

#thread one 
def do_something(lock):
    with lock: #get the mutex lock
        data_copy = copy.deepcopy(shared_list)
    # do something with data_copy
    data_copy = ...
    with lock: #get the mutex lock
        shared_list = data_copy
    

#thread two 
def do_something_two(lock):
    with lock: #get the mutex lock
        data_copy = copy.deepcopy(shared_list)
    # do something with data_copy 
    data_copy = ...
    with lock: #get the mutex lock
        shared_list = data_copy

#run thread one and two.
```
This will allow the threads to run at the same time.\
In our application we will processing real time data, so let me describe the structure that works best for me in the following steps.
1. get the mutex lock (`with`  command)
2. copy  the data over. 
3. release the mutex lock
4. process the data
5. set the data into another storage for use later (remember to use mutex locking here if appropriate.)\

Here is an example, for this example assume that `byte_data` is a list that is published by another thread and that the other thread will call the `populate` function when it has data. Also assume that `processed_data` is a list that is read by another thread that calls the `read` function when it wants to read the data. Also assume that our `processing` function is called every so often by an event that triggers.

```python
import threading 
import copy

byte_data = []
byte_data_lock = threading.Lock()

processed_data = []
processed_data_lock = threading.Lock()

#populate the byte_data 
def populate(data):
    with byte_data_lock:
        byte_data.append(data)

def read():
    with processed_data_lock:
        data_copy = copy.deepcopy(processed_data)
        # You may want to clear the data after it is read here is an example of how to do that
        processed_data.clear()
    return data_copy

def processing():
    with byte_data_lock:
        data_copy = copy.deepcopy(byte_data)
    #save the length of the data we are processing 
    num_samples = len(data_copy)

    #process data into a local variable called temp_processed_data 
    temp_processed_data = ...
    
    #Now we want to clear the data we have already process
    with byte_data_lock:
        byte_data = byte_data[num_samples:] # this is called slicing, it will create a new list starting at num_samples and going to the end of the list. NOTE: I am pretty sure this works but I am not going to compile this code to check. 
    # Now it is time to save our data
    with processed_data_lock:
        processed_data.append(temp_processed_data)
```
Okay lets talk about this example. First you may ask, why are we coping the data so much, does that increase our memory foot print a lot? The answer is yes it does increase our memory foot print a lot. However, we gain a lot of speed, provided that we are not copying HUGE amounts of data. This example is meant to be a simple implantation that will work for most cases. I would suggest trying it, with out optimizing the code, then if it is too slow try optimizing the code to run faster. Second question I get a lot is why do we have to use `copy.deepcopy` the short answers is because python is that way. The long answer is written in the `NOTES.md`  under `Threading`. However, you do not have to use `copy.deepcopy` if you are using simple types such as int, float, bool, ect. \

Now lets talk about the structure of the code. 
- Notice that I have have bi-directional mutex locking. This means I lock the data on both reads a writes. Makes sure you do that. It is tempting to not lock on writes, because it may not always be strictly necessary, in some edge cases. However, I would recommend always using them. 
- Notice that I save the `number_samples` I get from `byte_data`. This is because it is possible that while I am processing the populate thread, will put more data in that list. Thus I need to save how much data I have processed.
- Finally do not multi thread if you do not have too. It cause headaches and over head that is really not worth it unless it is necessary. 

NOTE: Be careful not to create circular dependance on your mutex locks. If thread 1 wants a lock that thread 2 has, and thread 2 wants a lock that thread 1 has, well then, nobody can do anything and your program will freeze. 
