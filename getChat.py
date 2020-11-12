import json
from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from collections import OrderedDict
from os import path, stat, remove, makedirs
from sys import exit


API_ID   = 
API_HASH = 
PHONE_NUM = 

def telegram_connect(api_id, api_hash, phone_number):
	print('Connecting to Telegram...')
	client = TelegramClient("Session", api_id, api_hash)
	if not client.start():
		print('Could not connect to Telegram.')
		return None
	else:
		if not client.is_user_authorized():
			print('Session file not found. sending code request...')
			client.sign_in(phone_number)
			self_user = None
			while self_user is None:
				code = input('Please enter the code you just received: ')
				self_user = client.sign_in(code=code)
			print('Sign in to Telegram success.\n')
		else:
			print('Log in to Telegram success.\n')
	return client


def getBasicInfo(client, chat):
	try:
		chat_entity = client.get_entity(chat)
	except ValueError:
		print("Can't find the chat.")
		exit(1)
	try:
		num_members = client.get_participants(chat_entity)
	except Exception:
		num_members = "Chat Admin privileges required"

	msgs = client.get_messages(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", msgs[0].chat_id), \
			("title", msgs[0].chat.title), \
			("username", msgs[0].chat.username), \
			("num_members", num_members), \
			("num_messages", msgs.total), \
			("supergroup", msgs[0].chat.megagroup) \
		])
	return basic_info

def getAllMessages(client, chat_id):
	#Get all messages information from a group/channel/chat
	messages = []
	chat_entity = client.get_entity(chat_id)
	num_msg = client.get_messages(chat_entity, limit=1).total
	msgs = client.get_messages(chat_entity, limit=num_msg)
	for msg in reversed(msgs):
		msg_sender = ""
		if hasattr(msg.sender, "first_name"):
			msg_sender = msg.sender.first_name
			if hasattr(msg.sender, "last_name"):
				if msg.sender.last_name:
					msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if hasattr(msg.sender, "username"):
			if msg.sender.username:
				if msg_sender != "":
					msg_sender = "{} (@{})".format(msg_sender, msg.sender.username)
				else:
					msg_sender = "@{}".format(msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		if msg.sender == None:
			msg_data = OrderedDict \
			([ \
				("id", msg.id), ("username", ""), ("text", msg.message), ("sent_time", msg_sent_time), \
				("sent_date", msg_sent_date), ("sender_user", msg_sender), \
				("sender_user_id", ""), ("reply_to", msg.reply_to_msg_id) \
			])
		else:
			msg_data = OrderedDict \
				([ \
					("id", msg.id), ("username", msg.sender.username), ("text", msg.message), ("sent_time", msg_sent_time), \
					("sent_date", msg_sent_date), ("sender_user", msg_sender), \
					("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
				])
		messages.append(msg_data)
	return messages


def file_write_history(chat_name, messages):
	file_name = "./Telegram_chat/{}.txt".format(chat_name)
	try:
		directory = path.dirname(file_name)
		if not path.exists(directory):
			makedirs(directory)
		with open(file_name, 'w', encoding="utf-8") as f:
			export_moment = "{} - {}".format(messages[len(messages)-1]['sent_date'], \
				messages[len(messages)-1]['sent_time'])
			f.write("Exported History of \"{}\" until {}:\n" \
				"--------------------------------------------------------\n" \
				.format(chat_name, export_moment))
			for msg in messages:
				sent_moment = "{} - {}".format(msg['sent_date'], msg['sent_time'])
				msg_text = msg['text']
				if (msg_text == None) or (msg_text == ""):
					msg_text = "[Image/File/...]"
				if msg['reply_to']:
					msg_to_Write = "\n[UserName - {}]\n{}\n{}:\n[In reply to {}] - {}\n\n" \
						.format(msg['username'], sent_moment, msg['sender_user'], msg['reply_to'], \
						msg_text)
				else:
					msg_to_Write = "\n[UserName - {}]\n{}\n{}:\n{}\n\n" \
						.format(msg['username'], sent_moment, msg['sender_user'],	msg_text)
				f.write(msg_to_Write)
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Can't convert data value to write in the file")
	except MemoryError:
		print("    Error: You are trying to write too much data")

def main():
	error = False
	client = telegram_connect(API_ID, API_HASH, PHONE_NUM)
	if client is not None:
		chat_link = input('\nChat Link to Export: ')
		chat_info = getBasicInfo(client, chat_link)
		chat_name = "unknown"
		if chat_info["username"]:
			chat_name = chat_info["username"]
		else:
			chat_name = chat_info["title"]
		print('Exporting messages.......')
		messages = getAllMessages(client, chat_link)
		if messages:
			file_write_history(chat_name, messages)
		else:
			print('\n    ERROR - No access to chat messages information')
			error = True
		if not error:
			print("\nChat succesfully exported in output directory\n")

if __name__ == "__main__":
	main()
