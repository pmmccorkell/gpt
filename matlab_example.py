# Patrick McCorkell
# Feb 2024

from time import sleep
from gc import collect as trash
from gpt import Chat
import atexit

def main():
	# Initiate class with default values.
	session = Chat('Matlab','gpt-3.5-turbo-0125','You are an AI assistant that helps users generate Matlab code.')

	# Register exit_program() to execute any time the program ends.
	atexit.register(session.exit_program)

	# Loop the prompt->answer cycle
	while(session.loop):
		session.new_message()
		trash()
		sleep(0.3)

# Execute main() if this is the top level script.
if __name__ == '__main__':
	main()