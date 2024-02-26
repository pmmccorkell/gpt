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

# Class for creating a Thread and Assistant with GPT API
class Chat():

	def __init__(self):
		#### Log Setup ####
		self.default_directory = DEFAULT_DIRECTORY														# from secrets.py
		self.filename = self.default_directory + datetime.now().strftime('%Y%m%d_%H:%M:%s.log')			# format the log filename
		self.log = 0																					# initiate an attribute w/dummy value 
		self.renamed = 0
		self.log_setup()																				# setup() function to initiate logging

		#### Loop and Stop parameters to stop sending messages to GPT ####
		self.loop = 1
		self.stop_dict = {		# add more values to stop the user_prompt->response loop
			'stop' : 1,				# or remove values if undesired.
			'stop.' : 1,
			'quit' : 1,
			'quit.' : 1,
			'exit' : 1,
			'exit.' : 1,
			'end' : 1,
			'end.' : 1,
			'q' : 1
		}

		# Instantiate the OpenAI session using your private key
		self.client = openai.OpenAI(api_key=OPENAI_KEY)					# key from secrets.py

		# Create an assistant
		self.assistant_name = "Matlab"
		self.instructions = "You are an AI assistant that helps users generate Matlab code."
		self.model = "gpt-3.5-turbo-0125"
		self.assistant = self.client.beta.assistants.create(
			name = self.assistant_name,
			instructions = self.instructions,
		#	tools=[{"type": "code_interpreter"}],
			model = self.model,
		)

		###### For the first cycle of the prompt->response loop, execute manually in __init__() ######

		# Create a thread to track the conversation
		self.thread = self.client.beta.threads.create()

		# Get input from user
		get_input = input("\r\nPrompt >>> ")

		# Check if the user is requesting to exit the program.
		if ( self.stop_dict.get(get_input.lower(),0) ):
			self.loop = 0			# end the loop
			self.exit_program()		# exit appropriately
	
		# 
		else:
			self.message = self.client.beta.threads.messages.create(
				thread_id=self.thread.id,
				role="user",
				content = get_input
			)

			self.run = self.client.beta.threads.runs.create(
				thread_id=self.thread.id,
				assistant_id=self.assistant.id,
				instructions=self.instructions,
			)

			while True:
				self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)

				if self.run.status == "completed":
					self.messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
					print()
					content_in = self.messages.data[-1].content[0]
					assert content_in.type == "text"
					self.log.info("Prompt: " + str(content_in.text.value))
					# print("Prompt: " + str(content_in.text.value))
					content_out = self.messages.data[-2].content[0]
					assert content_out.type == "text"
					self.log.info("GPT: " + str(content_out.text.value))
					print("GPT: " + str(content_out.text.value))
					print()
					break
				else:
					sleep(0.3)

	def log_setup(self):
		self.log = logging.getLogger("Assitant")
		self.log.setLevel(logging.INFO)
		format = logging.Formatter('%(asctime)s : %(message)s')
		file_handler = logging.FileHandler(self.filename)
		file_handler.setLevel(logging.INFO)
		file_handler.setFormatter(format)
		self.log.addHandler(file_handler)


	def response(self):
		self.run = self.client.beta.threads.runs.create(
			thread_id=self.thread.id,
			assistant_id=self.assistant.id,
			instructions=self.instructions,
		)
		while(self.run.status != "completed"):
			sleep(0.3)
			self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
		self.messages=self.client.beta.threads.messages.list(thread_id=self.thread.id)
		print()
		content_in = self.messages.data[1].content[0]
		assert content_in.type == "text"
		self.log.info("Prompt: " + str(content_in.text.value))
		# print("Prompt: " + str(content_in.text.value))
		content_out = self.messages.data[0].content[0]
		assert content_out.type == "text"
		self.log.info("GPT: " + str(content_out.text.value))
		print("\r\nGPT: " + str(content_out.text.value))
		print()


	def new_message(self):
		get_input = input("\r\nPrompt >>> ")

		self.message = self.client.beta.threads.messages.create(
			thread_id=self.thread.id,
			role="user",
			content = get_input
		)

		if ( self.stop_dict.get(get_input.lower(),0) ):
			self.loop = 0
			self.exit_program()
		else:
			self.response()

	# Function to rename the log file based on a short summary from GPT.
	def file_rename(self):
		
		# open file, read the contents in, and close the file
		file = open(self.filename,'r')
		file_text = file.read()
		file.close()

		# GPT-3.5-turbo has a text limit, so of the conversation is too long read the first and last 2000 characters.
		if (len(file_text) > 4096):
			file_text = file_text[0:2000] + " [TEXT BREAK] " + file_text[-2000:-1]

		# Let the user know what's going on.
		print("\r\n\r\nrenaming")
		print(file_text)

		# Open a new OpenAI session
		self.client = openai.OpenAI(api_key=OPENAI_KEY)

		# Start a new assistant with instructions to summarize the input into a filename.
		self.assistant = self.client.beta.assistants.create(
			name="Summarizer",
			instructions="You provide a short summary of text to be used as a Windows filename.",
			# tools=[{"type": "code_interpreter"}],
			model=self.model,
		)

		# Start a new thread.
		self.thread = self.client.beta.threads.create()

		# Generate the prompt, consisting of the logfile contents, to be sent to GPT.
		self.message = self.client.beta.threads.messages.create(
			thread_id=self.thread.id,
			role="user",
			content = file_text
		)

		# Execute the prompt.
		self.run = self.client.beta.threads.runs.create(
			thread_id=self.thread.id,
			assistant_id=self.assistant.id,
			instructions="Provide a short summary of text to be used as a Windows filename. Use less than 20 words.",
		)

		while True:
			# Check GPT for updates to the run status.
			self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)

			# Once the run status has completed, save the response and break out of the loop.
			if self.run.status == "completed":
				self.messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
				break
			else:
				sleep(1)

		# Parse the response for the useable information we want.
		content_out = self.messages.data[0].content[0]
		assert content_out.type == "text"
		gpt_summary = content_out.text.value
		gpt_summary = gpt_summary[0:min(128,len(gpt_summary))]
		while (gpt_summary[-1]=="."):
			gpt_summary = gpt_summary[:-1]
		print("\r\nsummary: ")
		print(gpt_summary)


		new_filename = self.filename[0:len(self.default_directory)+9] + self.assistant_name + " - " + gpt_summary + '.log'
		print(new_filename)
		os.rename(self.filename,new_filename)
		self.renamed = 1

	def delete_assistants(self):
		try:
			self.client.beta.assistants.delete(self.assistant.id)
		except:
			pass

	# Procedures once user has requested to exit the program.
	def exit_program(self):
		print("\r\n\r\nQuitting program.")
		self.delete_assistants()
		logging.shutdown()
		trash()
		if not self.renamed:
			self.file_rename()
		self.delete_assistants()
		trash()

def main():
	session = Chat()
	atexit.register(session.exit_program)
	while(session.loop):
		session.new_message()
		trash()
		sleep(0.3)
		
main()