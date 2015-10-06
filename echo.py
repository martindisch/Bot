import requests
import json
import os
from time import sleep

# Read token from untracked credentials file.
# We wouldn't want this on Github now, would we?
f = open("creds.txt")
lines = f.readlines()
f.close
token = lines[0].strip()

# If it exists, read the previous last update id from file
last_update = 0
if os.path.isfile("offset"):
    f = open("offset", 'r')
    last_update = int(f.read())
    f.close

# This is the url for communicating with your bot
url = 'https://api.telegram.org/bot%s/' % token

# We want to keep checking for updates. So this must be a never ending loop
while True:
    gotUpdate = False
    # My chat is up and running, I need to maintain it! Get me all chat updates
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    # Ok, I've got 'em. Let's iterate through each one
    for update in get_updates['result']:
        # First make sure I haven't read this update yet
        if last_update < update['update_id']:
            gotUpdate = True
            last_update = update['update_id']
            # I've got a new update. Let's see what it is.
            if 'message' in update:
                # It's a message! Let's send it back :D
                requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=update['message']['text']))
    if gotUpdate:
        f = open("offset", 'w')
        f.write(str(last_update))
        f.close
    # Let's wait a few seconds for new updates
    sleep(3)
