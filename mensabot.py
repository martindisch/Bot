import requests
import json
import os
import time
from time import sleep


def dateTime():
    return time.strftime("%Y/%m/%d %H:%M:%S")

# Read token and owner id from untracked credentials file.
# We wouldn't want this on Github now, would we?
f = open("creds.txt")
lines = f.readlines()
f.close
token = lines[0].strip()
ownerId = lines[1].strip()
print "Token and owner id loaded"

last_update = 0
url = 'https://api.telegram.org/bot%s/' % token
bot_name = "@unifr_mensabot"

pollCreator = "null"
participants_id = []
participants_name = []
hasConnection = True

while True:
    try:
        if (last_update == 0):
            get_updates = json.loads(requests.post(url + 'getUpdates',
                                                  params=dict(timeout=20),
                                                  timeout=40).content)
        else:
            get_updates = json.loads(
                requests.post(url + 'getUpdates',
                              params=dict(offset=last_update + 1,
                                          timeout=20),
                              timeout=40).content)
        if not hasConnection:
            print dateTime() + "    regained connection"
            hasConnection = True
    except:
        if hasConnection:
            print dateTime() + "    lost connection"
            hasConnection = False
        get_updates['result'] = []
        sleep(25)
    for update in get_updates['result']:
        hasMsg = False
        try:
            msg = update['message']['text']
            hasMsg = True
        except:
            hasMsg = False
        if hasMsg:
            senderId = update['message']['from']['id']
            senderName = update['message']['from']['first_name']
            out = "Got message: " + update['message']['text']
            out += " from " + senderName
            reply = "null"
            msg = msg.replace(bot_name, "")
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
                    if pollCreator != senderId:
                        if senderId in participants_id:
                            out = senderName + " tried to add themselves again"
                        else:
                            participants_id.append(senderId)
                            participants_name.append(senderName)
                            out = senderName + " joins for lunch"
                            reply = "Got it"
                    else:
                        out = "The poll creator tried to add themselves"
                        reply = "No need for that, you know you're coming"
                else:
                    out = senderName + " tried to add themselves - "
                    out += "no poll running"
            elif msg == "/result":
                if pollCreator != "null":
                    if pollCreator == senderId or senderId == ownerId:
                        if len(participants_name) > 2:
                            reply = ""
                            count = len(participants_name)
                            for i in range(count - 2):
                                reply += participants_name[i] + ", "
                            reply += participants_name[count - 2]
                            reply += " and " + participants_name[count - 1]
                            reply += " are joining you today.\n\n"
                            reply += "Be sure to save " + str(count)
                            reply += " more seats."
                        elif len(participants_name) == 2:
                            reply = participants_name[0] + " and "
                            reply += participants_name[1]
                            reply += " are joining you today.\n\n"
                            reply += "Be sure to save two more seats."
                        elif len(participants_name) == 1:
                            reply = participants_name[0]
                            reply += " is joining you today.\n\n"
                            reply += "Be sure to save one more seat."
                        else:
                            reply = "Looks like nobody is coming today"
                        pollCreator = "null"
                        participants_id = []
                        participants_name = []
                        out = senderName + " finished poll. Result:\n\n"
                        out += reply + "\n"
                    else:
                        out = senderName
                        out += " tried to finish a poll they didn't start"
                        reply = "Only the creator can finish a poll"
                else:
                    out = senderName
                    out += " tried to finish a poll - there is none running"
                    reply = "There is no poll running"
            print out
            last_update = update['update_id']
            if reply != "null":
                requests.post(
                    url + 'sendMessage',
                    params=dict(chat_id=update['message']['chat']['id'],
                                text=reply))
