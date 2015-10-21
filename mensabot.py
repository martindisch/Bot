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

last_update = 0
url = 'https://api.telegram.org/bot%s/' % token

pollCreator = "null"
participants_id = []
participants_name = []

while True:
    if (last_update == 0):
        get_updates = json.loads(requests.get(url + 'getUpdates').content)
    else:
        get_updates = json.loads(requests.get(url + 'getUpdates', params=dict(offset=last_update + 1)).content)
    for update in get_updates['result']:
        msg = update['message']['text']
        senderId = update['message']['from']['id']
        senderName = update['message']['from']['first_name']
        out = "Got message: " + update['message']['text'] + " from " + senderName
        reply = "null"
        if msg == "/newpoll":
            if pollCreator == "null":
                pollCreator = senderId
                reply = "Who's also having lunch today?"
                out = senderName + " started a poll"
            else:
                reply = "There's already a poll running"
                out = senderName + " tried to start another poll"
        elif msg == "/me":
            if pollCreator != "null":
                if senderId in participants_id:
                    out = senderName + " tried to add themselves again"
                else:
                    participants_id.append(senderId)
                    participants_name.append(senderName)
                    out = senderName + " joins for lunch"
                    reply = "Got it"
            else:
                out = senderName + " tried to add themselves - no poll running"
        elif msg == "/result":
            if pollCreator != "null":
                if pollCreator == senderId:
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
                    out = reply
                else:
                    out = senderName + " tried to finish a poll they didn't start"
                    reply = "Only the creator can finish a poll"
            else:
                out = senderName + " tried to finish a poll - there is none running"
                reply = "There is no poll running"
            print out
            last_update = update['update_id']
            if reply != "null":
                requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=reply))
    sleep(3)
