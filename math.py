# Patrick McCorkell
# Feb 2024

from time import sleep
import openai
import logging
import logging.handlers
from datetime import datetime
from gc import collect as trash
import os
import atexit
from secrets import *
from gpt import Chat


def main():
	session = Chat(name='Matlab',model='gpt-3.5-turbo-0125',instructions='You are an AI assistant that helps users generate Matlab code.')
	atexit.register(session.exit_program)
	while(session.loop):
		session.new_message()
		trash()
		sleep(0.3)
		
main()