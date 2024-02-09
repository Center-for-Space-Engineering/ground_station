'''
    This class shows and example of how to implement a command on the server. 
'''
from commandParent import commandParent

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto

class cmd_exsample(commandParent):
    '''
        The init function gose to the cmd class and then pouplates its 
        self into its command dict so that it is dynamically added to the command repo
    '''
    def __init__(self, CMD, coms):
        # init the parent
        super().__init__(CMD, coms=coms)
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'exsample'
        self.__args ={
            "fun1" : self.func1
        }
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__coms = coms

    def run(self):
        print("Ran command")
        dto  = print_message_dto("Ran command")
        self.__coms.print_message(dto, 2)
        return f"<p>ran command {self.__comandName}<p>"
    def run_args(self, args):
        print(f"ran command {str(args[0])} with args {str(args[1:])}")
        try:
            message = self.__args[args[0]](args)
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except Exception as e: #
            message += f"<p> Not vaild arg Error {e}</p>"
        return message
    def func1(self, arg):
        print("ran func1")
        dto = print_message_dto("Ran func1")
        self.__coms.print_message(dto, 2)
        return f"<p>ran command func1 with args {str(arg)}<p>"
    def get_args(self):
        message = ""
        for key in self.__args:
            message += f"<url>/{self.__comandName}/{key}</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
        return message

    def __str__(self):
        return self.__comandName
    def get_args_server(self):
        message = []
        for key in self.__args:
            message.append({ 
            'Name' : key,
            'Path' : f'/{self.__comandName}/{key}/-paramerters for the function-',
            'Discription' : 'Example commands'    
            })
        return message
