#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from time import sleep, ctime
# from random import choice as rc
import random
from slackclient import SlackClient

scripture_file = '/home/stevejaker/Programming/Scripts/daily_scripture/scriptures.json'
master_file = '/home/stevejaker/Programming/Scripts/daily_scripture/master_scriptures.json'
TOKEN = '' # Insert Private Slack Token Here
sc = SlackClient(TOKEN)



def sendMessage(text, verse, profile_pic, channel='CN69KLNTY'):
	sc.api_call(
		"chat.postMessage",
		text     = text,
		channel  = channel,
		as_user  = False,
		username = verse,
		icon_url = profile_pic
	)

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

def getProfilePic():
	return 'https://ldsblogs.com/files/2010/05/Jesus-Door-Knock-Mormon.jpg'

def getScriptures():
	with open(scripture_file, 'r') as f:
		f = json.load(f)
		return f #['scriptures']

def saveList(verse_list):
	# data = {"scriptures": verse_list}
	with open(scripture_file, 'w') as outfile:
		json.dump(verse_list, outfile, indent=4)

def getVerse():
	verse_list = getScriptures()
	choice = random.randint(0, len(verse_list))
	v = verse_list.pop(choice)
	# print(verse_list)
	saveList(verse_list)

	# Alternatively...
	# choice = rc(verse_list)
	# v = verses[choice]
	# del verses[choice]
	return v

def reset_from_master():
	with open(master_file, 'r') as f:
		f = json.load(f)
		
	with open(scripture_file, 'w') as outfile:
		json.dump(f, outfile, indent=4)

def main():
	messages = []
	if '--test' in sys.argv:
		test('This is a test message')

	v = getVerse()
	profile_pic = getProfilePic()
	messages.append(v)
	# messages = limitCharacters(v) # NOT CURRENTLY FUNCTIONAL

	for msg in messages:
		text  = msg['text']
		verse = msg['verse']
		sendMessage(text, verse, profile_pic)



if __name__ == '__main__':
	if '--reset_from_master' in sys.argv:
		reset_from_master()
	else:
		main()
	# HOUR = '12'
	# MIN = '00'
	# SEC_RANGE = ['00','01']
	# main()
	# sleep(4 * 60 * 60)
	# main()
	# while True:
	# 	# sleep_time = 24 * 60 * 60
	# 	t = mytime()
	# 	if t.hour == HOUR and t.min == MIN and t.sec in SEC_RANGE:
	# 		main()
	# 		sleep_time = 120
	# 	else:
	# 		if '--showtime' in sys.argv:
	# 			print("{}:{}:{}".format(t.hour,t.min,t.sec))
	# 		sleep_time = 1

	# 	sleep(sleep_time)

