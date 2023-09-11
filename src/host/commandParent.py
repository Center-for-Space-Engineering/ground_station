from colorama import Fore
"""This is the parent class of all commands. It implements all the function that the child commands should have. 
That way if the child class is missing a func it wont crash the server, and will be appernt to the user there is something 
they need to add to there class. Python is not a strongly typed language, this is the best I can do to try and make it more
strongly typed. """
class commandParent():
    def __init__(self, cmd):
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed + "No init func")
    def run(self):
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed + "No run func")
        return "No run func"
    def runArgs(self, args):
        errorRed = Fore.RED + "ERROR: " + Fore.WHITE
        print(errorRed  + "No run func with args")
        return "No run func with args"
    def __str__(self):
        errorRed = Fore.RED + "ERROR: " + Fore.WHIT
        print(errorRed + "No to str func")
        return "No to str func"
    def getArgs(self):
        return "<p>\t No Args implement</p>"
