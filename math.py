# Patrick McCorkell
# Feb 2024

from time import sleep
from gc import cololect as trash
from gpt import Chat
import atexit

def main():
	session = Chat(name='Matlab',model='gpt-3.5-turbo-0125',instructions='You are an AI assistant that helps users generate Matlab code.')
	atexit.register(session.exit_program)
	while(session.loop):
		session.new_message()
		trash()
		sleep(0.3)
		
main()