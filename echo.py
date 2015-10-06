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

url = 'https://api.telegram.org/bot%s/' % token

while True:
    gotUpdate = False
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            gotUpdate = True
            last_update = update['update_id']
            if 'message' in update:
                requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=update['message']['text']))
    if gotUpdate:
        f = open("offset", 'w')
        f.write(str(last_update))
        f.close
    sleep(3)
