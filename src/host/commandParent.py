'''
    This module defines the structure for classes that can be imported and used by the server. 
    It is not strictly required that you  inharriete from this class when using the server,
    however it is strongly recommend and will keep your code safe. 
'''
from colorama import Fore

class commandParent():
    """
        This is the parent class of all commands. It implements all the function that the child commands should have. 
        That way if the child class is missing a func it wont crash the server, and will be apparent to the user there is something 
        they need to add to there class. Python is not a strongly typed language, this is the best I can do to try and make it more
        strongly typed. 
    """
    def __init__(self, cmd, coms, called_by_child = False):
        if not called_by_child:
            errorRed = Fore.RED + "ERROR: " + Fore.WHITE
            _ = cmd # I dont actually need these variable here, it is just to maintain structure.
            _ = coms # I dont actually need these variable here, it is just to maintain structure.
            print(errorRed + "No init func")
    def run(self):
        '''
            This is how the server calls the command with out args
        '''
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed + "No run func")
        return "No run func"
    def run_args(self, args):
        '''
            This is how the server calls the command with args
        '''
        _ = args
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed  + "No run func with args")
        return "No run func with args"
    def __str__(self):
        '''
            It is help full for all the calls to have a to string function that returns html so the 
            serve can send things along to the browser. 
        '''
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed + "No to str func")
        return "No to str func"
    def get_args(self):
        '''
            This function is used so the server can call tell the user  what args this
            class uses. 
        '''
        return "<p>\t No Args implement</p>"
    def get_args_server(self):
        '''
            This function is used to make a dto for the server. It is so the server can take the information about this class and
            then put it into the commands table. 
        '''
        return [{ 
            'Name' : 'No get_args_server implemented',
            'Path' : 'No path given',
            'Description' : 'Please implement the get_args_server function so that the server can run this command.'    
            }]
