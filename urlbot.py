import os, sys, urllib
import requests
import json
import os
import time
from time import sleep

def dateTime():
    return time.strftime("%Y/%m/%d %H:%M:%S")

def getChanges():
    errormsg = '%s: No such file or directory'
    for path in savepath, urlspath:
        if not os.path.exists(path):
            print errormsg % path
            sys.exit(0)
    urlfile = open(urlspath, 'r').readlines()
    urlstring = ''
    for url in urlfile:
        if not url == "":
            if not 'http://' in url:
                url = 'http://' + url
            url = url.replace('\n', '')
            filename = url.replace("https://", "").replace(
                "http://", "").replace("/", "%2f")
            if not os.path.isfile(savepath + filename):
                urllib.urlretrieve(url, savepath + filename)
            filelines = open(savepath + filename, 'r').readlines()
            urllines = urllib.urlopen(url).readlines()
            if not filelines == urllines:
                open(savepath + filename, 'w').writelines(urllines)
                urlstring += '"' + url + '" '

    if urlstring:
        print "New data on " + urlstring
    else:
        print "Nothing for today"


def addUrl(url):
    open(urlspath, 'a').write(url + "\n")


def listUrls():
    filelines = open(urlspath, 'r').readlines()
    for idx, val in enumerate(filelines):
        if not val == "":
            print "[" + str(idx) + "] " + val.rstrip("\n")


def removeUrl(index):
    filelines = open(urlspath, 'r').readlines()
    if len(filelines) > index:
        del filelines[index]
        open(urlspath, 'w').writelines(filelines)
    else:
        print "Item does not exist"


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
hasConnection = True

savepath = 'urldata/'
urlspath = savepath + 'urls.txt'

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
            
            if msg == "/add":
                
            elif msg == "/list":
                
            elif msg == "/remove":
                
            print out
            last_update = update['update_id']
            if reply != "null":
                requests.post(
                    url + 'sendMessage',
                    params=dict(chat_id=update['message']['chat']['id'],
                                text=reply))