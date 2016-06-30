from __future__ import print_function
from lxml import html
from pprint import pprint
import requests
import time
# import datetime
import os
import difflib

# Declare last scrape
allLogs = [d for d in os.listdir('./logs')]
lastLogDir = ''
if allLogs:
    lastLogDir = './logs/' + max((os.path.getmtime('./logs/' + f), f) for f in allLogs)[1]


# Create somewhere to put our scrape
ts = time.time()
dt = time.strftime('%d-%b-%y-%H:%M')
print('ts dt', ts, dt)
logPath = os.path.join('./logs/', dt)

print('logPath ' + logPath)

if not os.path.exists(logPath):
    print("New log folder!")
    os.makedirs(logPath)
    os.chmod(logPath, 0777)

print('lastLogDir', lastLogDir)

# The pages we're going to scrape
pages = {
    '1': {
        'title': 'photobucketImport',
        'url': 'http://support.photobucket.com/hc/en-us/articles/200724324-Linking-and-Embedding-Images'}}
xpath = ''


# El loopo
for site in pages:
    page = requests.get(pages[site]['url'])
    tree = html.fromstring(page.content)
    print(page)

# Convert paragraphs to string
    content = '\n'.join(tree.xpath('//p/text()')).encode('utf-8').strip()
#    print(content)

# Save it

#    print(logPath + "/" + pages[site]['title'] + '.txt')

    with open(logPath + "/" + pages[site]['title'] + '.txt', 'a') as logFile:
        logFile.write(content)
# Open both copies
    with open(lastLogDir + "/" + pages[site]['title'] + '.txt', 'r') as l:
        lastLog = l.read()
    l.closed

    with open(logPath + "/" + pages[site]['title'] + '.txt', 'r') as t:
        thisLog = t.read()
    t.closed

# Check for diff
    # print('Raw content', content, ' \n --------------------\n', lastLog)
    
    # d = difflib.Differ()
    diff = difflib.unified_diff(thisLog.splitlines(), lastLog.splitlines(), n=0)
    print('>>>>>>>>>>>diff<<<<<<<<<<<<<', '\n'.join(diff))


# Break up diff

# Push diff to spreadsheet
