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

while True:
    gotUpdate = False
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            gotUpdate = True
            print ""
            pprint(update)
            print ""
            last_update = update['update_id']
            requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text="Received"))
            print "Acknowledged"
    if gotUpdate:
        f = open("offset", 'w')
        f.write(str(last_update))
        f.close
        print "Stored new offset"
    sleep(3)
