from commandParent import commandParent

class cmd_exsample(commandParent):
    """The init function gose to the cmd class and then pouplates its self into its command dict so that it is dynamically added to the command repo"""
    def __init__(self, CMD):
        #CMD is the cmd class and we are using it to hold all the command class
        self.__comandName = 'exsample'
        self.__args ={
            "arg1" : self.func1
        }
        dictCmd = CMD.getCommandDict()
        dictCmd[self.__comandName] = self #this is the name the webserver will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)

    def run(self):
        print("Ran command")
        return f"<p>ran command {self.__comandName}<p>"
    def runArgs(self, args):
        print("Ran command w/ args: " + str(args))
        message = f"<p>ran command {self.__comandName} with args {str(args)}<p>"
        try:
            message += self.__args[args[0]](args)
        except :
            message += "<p> Not vaild arg </p>"
        return message
    def func1(self, arg):
        print("ran fun1")
        return f"<p>Ran function for {arg}</p>"
    def getArgs(self):
        message = ""
        for key in self.__args:
            message += f"<p>&emsp;/{key}</p>"
        return message

    


    def __str__(self):
        return self.__comandName

