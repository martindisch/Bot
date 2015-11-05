import os, sys, urllib
savepath = 'urldata/'

errormsg = '%s: No such file or directory'
urlspath = savepath + 'urls.txt'
for path in savepath, urlspath:
    if not os.path.exists(path):
        print errormsg % path
        sys.exit(0)
urlfile = open(urlspath, 'r').readlines(); urlstring = ''
for url in urlfile:
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