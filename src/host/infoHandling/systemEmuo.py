import time
import os
import colorama
import sys
from termcolor import colored, cprint

class systemEmuo:
    def __init__(self):
        pass

    def print_old(self, message, delay = 0.15):
        for i in range(len(message)):
            print(message[:i] + "#")
            time.sleep(delay)
            print("\033c", end='')
        print(message)

    def print_old_continuos(self, message, delay = 0.15, end=''):
        print(message, end=end)
        if delay != 0:
            time.sleep(delay)
    
    def print_blinking(self, message, delay = 0.15, iter = 10):
        for i in range(iter):
            print(message + "|")
            time.sleep(delay)
            print("\033c", end='')
            print(message + "-")
            time.sleep(delay)
            print("\033c", end='')
    
        
    def print_system_load(self,message, delay = 0.2, loop = 2):
        for i in range(loop):
            print(message + colored(".", "yellow"))
            time.sleep(1)
            print("\033c", end='')
            print(message + colored("..", "yellow"))
            time.sleep(1)
            print("\033c", end='')
            print(message + colored("...", "yellow"))
            time.sleep(1)
            print("\033c", end='')