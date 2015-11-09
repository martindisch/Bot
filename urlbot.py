import os, sys, urllib

savepath = 'urldata/'
urlspath = savepath + 'urls.txt'

def getChanges():
    errormsg = '%s: No such file or directory'
    for path in savepath, urlspath:
        if not os.path.exists(path):
            print errormsg % path
            sys.exit(0)
    urlfile = open(urlspath, 'r').readlines(); urlstring = ''
    for url in urlfile:
        if not url == "":
            if not 'http://' in url:
                url = 'http://' + url
            url = url.replace('\n', '')
            filename = url.replace("https://", "").replace("http://", "").replace("/", "%2f")
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