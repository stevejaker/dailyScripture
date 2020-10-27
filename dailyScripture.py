#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import random

def sendSlackMessage(text, verse, profile_pic, channel=''):
	r = sc.api_call(
		"chat.postMessage",
		text     = text,
		channel  = channel,
		as_user  = False,
		username = verse,
		icon_url = profile_pic
	)
	if not r['ok']:
		print(f'Error! {r}')

def limitCharacters(v):
	#not functional
	global MAX_LEN
	messages = []
	text  = v['text']
	verse = v['verse']

	if len(text) > MAX_LEN:
		while len(text) > MAX_LEN:
			new_text = text[:MAX_LEN - modifier]
			dct = {
				"verse" : verse,
				"text"  : new_text
			}
			text = text.replace(new_text,'')
			messages.append(dct)
		messages.append()
	return messages

def getProfilePic(warning=False):
	if warning:
		return "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/1109px-Warning.svg.png"
	else:
		return 'https://ldsblogs.com/files/2010/05/Jesus-Door-Knock-Mormon.jpg'

def getScriptures():
	with open(scripture_file, 'r') as f:
		f = json.load(f)
		return f #['scriptures']

def saveList(verse_list):
	# data = {"scriptures": verse_list}
	with open(scripture_file, 'w') as outfile:
		json.dump(verse_list, outfile, indent=4)

def getVerseFromList(debug=False):
	warning = False
	verse_list = getScriptures()
	choice = random.randint(0, len(verse_list)-1)
	if len(verse_list) < verse_warning_num:
		warning = f"There are {len(verse_list)} verses remaining. Consider adding more."
	elif len(verse_list) < critical_warning_num:
		warning = f"There are {len(verse_list)} verses remaining. Please add more. If the verse count hits 1. All verses will be reset."
	elif len(verse_list) == 1:
		pass # Not active for list
	if not debug:
		v = verse_list.pop(choice)
		# print(verse_list)
		saveList(verse_list)
	else:
		print(f"Running {sys.argv[0]} in debug mode.")
		print(f"Printing scripture to terminal output: ", end="")
		sys.exit(json.dumps(verse_list[choice], indent=4))

	# Alternatively...
	# choice = rc(verse_list)
	# v = verses[choice]
	# del verses[choice]
	return v, warning

def getVerseFromDatabase(debug=False):
	warning = False
	conn = mysql.connect(user=DB_USERNAME, password=DB_PASSWORD, database=DB_NAME)
	cursor = conn.cursor(buffered=True)
	cursor.execute(SQL_STATEMENT)
	verse_list = cursor.fetchall()
	choice = random.randint(0, len(verse_list)-1)
	verse = verse_list[choice]
	ID, verse, text, is_used, uri = verse_list[choice]
	cursor.execute(f"UPDATE `{TABLE_NAME}` SET `is_used` = 1 WHERE `id` = {ID}")
	conn.commit()
	v = {"text": text, "verse": verse}
	# When using the DB method, verse_list.pop() 
	# is not used, so the verse_list is 1 item longer
	# hence len(verse_list) - 1 is used.
	if len(verse_list) - 1 < verse_warning_num:
		warning = f"There are {len(verse_list)} verses remaining. Consider adding more."
	elif len(verse_list) - 1 < critical_warning_num:
		warning = f"There are {len(verse_list)} verses remaining. Please add more. If the verse count hits 1. All verses will be reset."
	elif len(verse_list) == 0:
		cursor.execute(f"UPDATE `{TABLE_NAME}` SET `is_used` = 0 WHERE `is_used` = 1")
	if not debug:
		# print(verse_list)
		pass
	else:
		print(f"Running {sys.argv[0]} in debug mode.")
		print(f"Printing scripture to terminal output: ", end="")
		sys.exit(v)

	return v, warning

def reset_from_master():
	with open(master_file, 'r') as f:
		f = json.load(f)
		
	with open(scripture_file, 'w') as outfile:
		json.dump(f, outfile, indent=4)

def main(debug=False, send_method="slack", use_db=False):
	messages = []
	if use_db:
		v, warning = getVerseFromDatabase(debug=debug)
	else:
		v, warning = getVerseFromList(debug=debug)
	profile_pic = getProfilePic()
	messages.append(v)
	# messages = limitCharacters(v) # NOT CURRENTLY FUNCTIONAL

	for msg in messages:
		text  = msg['text']
		verse = msg['verse']
		if send_method == "text":
			sendTextMessage(text, verse)
		else:
			sendSlackMessage(text, verse, profile_pic, channel=CHANNEL)
	if warning:
		warning_pic = getProfilePic(warning=True)
		sendSlackMessage(warning, "Info", warning_pic, channel=CHANNEL)


if __name__ == '__main__':
	global scripture_file, DB_USERNAME, DB_PASSWORD, DB_NAME, SQL_STATEMENT, TABLE_NAME, verse_warning_num, critical_warning_num
	TOKEN = None
	CHANNEL = None
	send_method = None
	email = None
	password = None
	debug = False
	send_method = "slack"
	data_source = "json"
	verse_warning_num = 25
	critical_warning_num = 5
	
	for idx, arg in enumerate(sys.argv):
		if arg in ['-h', '--help']:
			help()
		elif arg in ['--reset_from_master']:
			reset_from_master()
		elif arg in ['--debug']:
			debug = True
		elif arg in ['-t', '--token']:
			TOKEN = sys.argv[idx + 1] # Insert Private Slack Token Here = 
		elif arg in ['-c', '--channel']:
			CHANNEL = sys.argv[idx + 1]
		elif arg in ['-e', '--email']:
			email = sys.argv[idx + 1]
		elif arg in ['-p', '--password']:
			password = sys.argv[idx + 1]
		elif arg in ['-s', '--sql']:
			data_source = "sql"
		elif arg in ['-du', '--db-username']:
			DB_USERNAME = sys.argv[idx + 1] 
		elif arg in ['-dp', '--db-password']:
			DB_PASSWORD = sys.argv[idx + 1] 
	
	if TOKEN is not None and CHANNEL is not None:
		from slackclient import SlackClient
		sc = SlackClient(TOKEN)
		send_method = "slack"
	elif email is not None and password is not None:
		send_message = "text" # not functional
	else:
		sys.exit("No slack token/channel or email/password provided.")

	if data_source.lower() in ['sql']:
		# If using SQL DB
		import mysql.connector as mysql
		use_db = True
		# DB_USERNAME = "" # insert username
		# DB_PASSWORD = "" # insert password
		DB_NAME = "scriptures"
		TABLE_NAME = "scriptures"
		SQL_STATEMENT = f"SELECT * FROM `{TABLE_NAME}` WHERE is_used=0"
	else:
		# If using JSON data file
		use_db = False
		base_path = os.path.expanduser("~")
		subdir = ".scriptures"
		master = "master_scriptures.json"
		working = "scriptures.json"
		master_file = os.path.join(base_path,  subdir, master)
		scripture_file = os.path.join(base_path, subdir, working)
	main(debug=debug, send_method=send_method, use_db=use_db)
