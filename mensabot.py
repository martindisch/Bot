import requests
import json
import os
from time import sleep
from pprint import pprint

# Read token from untracked credentials file.
# We wouldn't want this on Github now, would we?
f = open("creds.txt")
lines = f.readlines()
f.close
token = lines[0].strip()
print "Token loaded"

# If it exists, read the previous last update id from file
last_update = 0
if os.path.isfile("offset"):
    f = open("offset", 'r')
    last_update = int(f.read())
    f.close
    print "Offset loaded"
else:
    print "No offset - starting new"

url = 'https://api.telegram.org/bot%s/' % token

pollCreator = "null"
participants_id = []
participants_name = []

while True:
    gotUpdate = False
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            gotUpdate = True
            msg = update['message']['text']
            out = "Got message: " + update['message']['text']
            reply = "null"
            if msg == "/newpoll":
                if pollCreator == "null":
                    pollCreator = update['message']['from']['id']
                    reply = "Who's also having lunch today?"
                    out = update['message']['from']['first_name'] + " started a poll"
                else:
                    reply = "There's already a poll running"
                    out = update['message']['from']['first_name'] + " tried to start another poll"
            elif msg == "/me":
                if pollCreator != "null":
                    if any(update['message']['from']['id'] in p for p in participants_id):
                        out = update['message']['from']['first_name'] + " tried to add themselves again"
                    else:
                        participants_id.append(update['message']['from']['id'])
                        participants_name.append(update['message']['from']['first_name'])
                        out = update['message']['from']['first_name'] + " joins for lunch"
                        reply = "Got it"
                else:
                    out = update['message']['from']['first_name'] + " tried to add themselves - no poll running"
            elif msg == "/result":
                if pollCreator != "null":
                    if pollCreator == update['message']['from']['id']:
                        if len(participants_name) > 2:
                            test = 0
                        elif len(participants_name) == 2:
                            reply = participants_name[0] + " and " + participants_name[1] + " are joining you today.\n\nBe sure to save two more seats."
                        elif len(participants_name) == 1:
                            reply = participants_name[0] + " is joining you today.\n\nBe sure to save one more seat."
                        else:
                            reply = "Looks like nobody is coming today"
                        pollCreator = "null"
                        participants_id = []
                        participants_name = []
                    else:
                        out = update['message']['from']['first_name'] + " tried to finish a poll they didn't start"
                        reply = "Only the creator can finish a poll"
                else:
                    out = update['message']['from']['first_name'] + " tried to finish a poll - there is none running"
                    reply = "There is no poll running"
            print out
            last_update = update['update_id']
            if reply != "null":
                requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=reply))
    if gotUpdate:
        f = open("offset", 'w')
        f.write(str(last_update))
        f.close
        print "Stored new offset"
    sleep(3)
