import os, sys, urllib
import requests
import json
import os
import time
import pickle
from time import sleep

def dateTime():
    return time.strftime("%Y/%m/%d %H:%M:%S") + "   "

def getChanges():
    try:
        urlfile = pickle.load(open(urlspath, 'rb'))
    except (OSError, IOError) as e:
        urlfile = []
    urlstring = ''
    for url in urlfile:
        if not 'http://' in url:
            url = 'http://' + url
        url = url.replace('\n', '')
        filename = url.replace("https://", "").replace(
            "http://", "").replace("/", "%2f")
        try:
            if not os.path.isfile(savepath + filename):
                urllib.urlretrieve(url, savepath + filename)
            filelines = open(savepath + filename, 'r').readlines()
            urllines = urllib.urlopen(url).readlines()
            if not filelines == urllines:
                open(savepath + filename, 'w').writelines(urllines)
                urlstring += "Updated: " + url + "\n"
        except:
            urlstring += "Down: " + url + "\n"

    if urlstring:
        return urlstring
    else:
        return "Nothing"


def addUrl(url):
    urls = []
    try:
        urls = pickle.load(open(urlspath, 'rb'))
        urls.append(url)
    except (OSError, IOError) as e:
        urls.append(url)
    pickle.dump(urls, open(urlspath, 'wb'))
    return "Watching the given URL"


def listUrls():
    try:
        filelines = pickle.load(open(urlspath, 'rb'))
    except (OSError, IOError) as e:
        filelines = []
    out = ""
    if len(filelines) > 0:
        for idx, val in enumerate(filelines):
            out += "[" + str(idx) + "] " + val + "\n"
        return out
    else:
        return "Not watching any URLs"


def removeUrl(index):
    filelines = []
    try:
        filelines = pickle.load(open(urlspath, 'rb'))
        if len(filelines) > index:
            del filelines[index]
            pickle.dump(filelines, open(urlspath, 'wb'))
            return "URL removed from watchlist"
        else:
            return "Item does not exist"
    except (OSError, IOError) as e:
        return "Not watching any URLs"


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
urlspath = savepath + 'urls'
commandState = "null"
interval = 5
timestamp = time.time()

if not os.path.exists(savepath):
    os.makedirs(savepath)

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
            print dateTime() + "regained connection"
            hasConnection = True
    except:
        if hasConnection:
            print dateTime() + "lost connection"
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
            
            if senderId == int(ownerId):
                if msg == "/add":
                    reply = "Send me the URL you want to watch"
                    commandState = "add"
                    out = senderName + " wants to add a URL"
                elif msg == "/list":
                    reply = listUrls()
                    out = senderName + " lists the URLs"
                elif msg == "/remove":
                    reply = "Send me the index of the URL you want to unwatch"
                    commandState = "remove"
                    out = senderName + " wants to remove a URL"
                elif commandState == "add":
                    reply = addUrl(msg)
                    commandState = "null"
                    out = senderName + " added " + msg
                elif commandState == "remove":
                    reply = removeUrl(int(msg))
                    commandState = "null"
                    out = senderName + " removed URL [" + msg + "]"
            else:
                reply = "You are not authorized to use this service"
                
            print dateTime() + out
            last_update = update['update_id']
            if reply != "null":
                requests.post(
                    url + 'sendMessage',
                    params=dict(chat_id=update['message']['chat']['id'],
                                text=reply))
    if time.time() - timestamp > interval * 60:
        if hasConnection:
            changes = getChanges()
            if changes != "Nothing":
                requests.post(
                        url + 'sendMessage',
                        params=dict(chat_id=update['message']['chat']['id'],
                                    text=changes))
                print dateTime() + "Notified " + senderName + " of changes"
        timestamp = time.time()