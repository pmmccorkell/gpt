from time import sleep
import openai
import logging
import logging.handlers
from datetime import datetime
from gc import collect as trash
import os
from secrets import *


class Chat():

	def __init__(self):
		self.default_directory = "/mnt/c/Python/openai/discussions/"
		self.filename = self.default_directory + datetime.now().strftime('%Y%m%d_%H:%M:%s.log')
		self.log = 0
		self.log_setup()

		self.client = openai.OpenAI(api_key=OPENAI_KEY)
		self.loop = 1
		self.stop_dict = {
			'stop' : 1,
			'stop.' : 1,
			'quit' : 1,
			'quit.' : 1,
			'exit' : 1,
			'exit.' : 1
		}

		self.assistant = self.client.beta.assistants.create(
			name="Anthropologist",
			instructions="You are a sardonic anthropology professor of Irish heritage who approaches all topics from a neutral stance. You hate the English.",
			# tools=[{"type": "code_interpreter"}],
			model="gpt-3.5-turbo-0125",
		)

		self.thread = self.client.beta.threads.create()

		get_input = input("\r\nPrompt >>> ")
		if ( self.stop_dict.get(get_input.lower(),0) ):
			# print("\r\nquitting\r\n\r\n")
			self.loop = 0
			self.exit_program()
	
		else:
			self.message = self.client.beta.threads.messages.create(
				thread_id=self.thread.id,
				role="user",
				content = get_input
			)

			self.run = self.client.beta.threads.runs.create(
				thread_id=self.thread.id,
				assistant_id=self.assistant.id,
				instructions="Please be as neutral as possible while maintaining levity and Irish humor. And fuck the English.",
			)

			while True:
				self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)

				if self.run.status == "completed":
					self.messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
					print()
					content_in = self.messages.data[-1].content[0]
					assert content_in.type == "text"
					self.log.info("Prompt: " + str(content_in.text.value))
					print("Prompt: " + str(content_in.text.value))
					content_out = self.messages.data[-2].content[0]
					assert content_out.type == "text"
					self.log.info("GPT: " + str(content_out.text.value))
					print("GPT: " + str(content_out.text.value))
					print()
					break
				else:
					# print("in progress...")
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
			instructions="Please be as neutral as possible while maintaining levity. And fuck the English.",
		)
		while(self.run.status != "completed"):
			# print('...checking...\r\n')
			sleep(0.3)
			self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
		self.messages=self.client.beta.threads.messages.list(thread_id=self.thread.id)
		print()
		content_in = self.messages.data[1].content[0]
		assert content_in.type == "text"
		self.log.info("Prompt: " + str(content_in.text.value))
		print("Prompt: " + str(content_in.text.value))
		content_out = self.messages.data[0].content[0]
		assert content_out.type == "text"
		self.log.info("GPT: " + str(content_out.text.value))
		print("GPT: " + str(content_out.text.value))
		print()


	def new_message(self):
		get_input = input("\r\nPrompt >>> ")

		self.message = self.client.beta.threads.messages.create(
			thread_id=self.thread.id,
			role="user",
			content = get_input
		)

		if ( self.stop_dict.get(get_input.lower(),0) ):
			# print("\r\nquitting\r\n\r\n")
			self.loop = 0
			self.exit_program()
		else:
			self.response()

	def file_rename(self):
		file = open(self.filename,'r')
		file_text = file.read()
		file.close()
		if (len(file_text) > 4096):
			file_text = file_text[0:2000] + " [TEXT BREAK] " + file_text[-2000:-1]
		print("\r\n\r\nrenaming")
		print(file_text)

		self.client = openai.OpenAI(api_key='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')
		self.assistant = self.client.beta.assistants.create(
			name="Summarizer",
			instructions="You provide a short summary of text to be used as a Windows filename.",
			# tools=[{"type": "code_interpreter"}],
			model="gpt-3.5-turbo-0125",
		)
		self.thread = self.client.beta.threads.create()
		self.message = self.client.beta.threads.messages.create(
			thread_id=self.thread.id,
			role="user",
			content = file_text
		)
		self.run = self.client.beta.threads.runs.create(
			thread_id=self.thread.id,
			assistant_id=self.assistant.id,
			instructions="Provide a short summary of text to be used as a Windows filename. Use less than 20 words",
		)
		while True:
			self.run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)

			if self.run.status == "completed":
				self.messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
				break
			else:
				sleep(1)

		content_out = self.messages.data[0].content[0]
		assert content_out.type == "text"
		gpt_summary = content_out.text.value
		print("summary: ")
		print(gpt_summary)
		gpt_summary_trunc = gpt_summary[0:min(128,len(gpt_summary))]
		new_filename = self.filename[0:len(self.default_directory)+9] + gpt_summary_trunc + '.log'
		print(new_filename)
		os.rename(self.filename,new_filename)

	def exit_program(self):
		print("\r\n\r\nQuitting program.")
		self.client.beta.assistants.delete(self.assistant.id)
		logging.shutdown()
		trash()
		self.file_rename()
		self.client.beta.assistants.delete(self.assistant.id)
		trash()





def main():
	session = Chat()
	# print("checking assistant status. ")
	# time.sleep(10)
	while(session.loop):
		session.new_message()
		trash()
		sleep(0.3)
		
main()