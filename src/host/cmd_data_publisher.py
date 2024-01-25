from commandParent import commandParent

#import DTO for comminicating internally
from DTOs.logger_dto import logger_dto
from DTOs.print_message_dto import print_message_dto

class cmd_data_publisher(commandParent):
    """The init function gose to the cmd class and then pouplates its self into its command dict so that it is dynamically added to the command repo"""
    def __init__(self, CMD, coms):
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'data_publisher'
        self.__args ={
            "start_data_pubisher" : self.start_data_pubisher
        }
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__coms = coms
        self.__port = -1

    def run_args(self, args):
        try:
            message = self.__args[args[0]](args[1:])
            print(f"ran command {str(args[0])} with args {str(args[1:])}")
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except :
            message += "<p> Not vaild arg </p>"
        return message
    def start_data_pubisher(self, arg):
        self.__port = arg[0]
        return f"<h3> Started data publisher on port:{self.__port} </h3>"
    def get_args(self):
        message = ""
        for key in self.__args:
            if key == "start_data_pubisher":
                message += f"<url>/{self.__comandName}/{key}/-port-</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
        return message

    def __str__(self):
        return self.__comandName
    def get_args_server(self):
        message = []
        for key in self.__args:
           if key == "start_data_pubisher":
            message.append({ 
                'Name' : key,
                'Path' : f'/{self.__comandName}/{key}/-port number-',
                'Discription' : 'This command starts a publisher on the port that is given to it. Should be above 5000 and cann\'t be in use.'    
                })
        return message
