import time
import os
import colorama
import sys
from termcolor import colored, cprint
import threading

class systemEmuo:
    def __init__(self, coms = None):
        self.__messageLock = threading.Lock()
        self.__coms = coms

    def print_old_continuos(self, message, delay = 0.15, end=''):
        with self.__messageLock:
            print(message, end=end)
            if delay != 0:
                time.sleep(delay)
    def clear(self):
        with self.__messageLock:
            print("\033c", end='') #clears the terminal