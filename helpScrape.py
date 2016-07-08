from __future__ import print_function
from lxml import html
#import pprint
import requests
import time
# import datetime
import os
import difflib

# Google sheets setup
import httplib2

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# List of websites
from websites import *

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials



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

def main():

    returnedPages = 0
    sheetBody = []
    # El loopo
    for site in pages:
        page = requests.get(pages[site]['url'])
        tree = html.fromstring(page.content)
        print('URL', pages[site]['url'])

    # Convert paragraphs to string
        content = '\n'.join(tree.xpath('//p/text()')).encode('utf-8').strip()
        print('CONTENT', content, '///END CONTENT')

    # Save it

    #    print(logPath + "/" + pages[site]['title'] + '.txt')

        with open(logPath + "/" + pages[site]['title'] + '.txt', 'a') as logFile:
            logFile.write(content)
        logFile.closed
    # Open both copies
        with open(lastLogDir + "/" + pages[site]['title'] + '.txt', 'r') as l:
            lastLog = l.read()
        l.closed

        thisLog = content
        # with open(logPath + "/" + pages[site]['title'] + '.txt', 'r') as t:
        #     thisLog = t.read()
        # t.closed

    # Check for diff
        # print('Raw content', content, ' \n --------------------\n', lastLog)

        # d = difflib.Differ()
        diff = difflib.unified_diff(thisLog.splitlines(), lastLog.splitlines(), n=0)
        diffResult = '\n'.join(diff)
        if diffResult:
            diffResult = pages[site]['url'] + diffResult
        print('site, len pages', site, str(len(pages)))
        print('>>>>>>>>>>>diff<<<<<<<<<<<<<', diffResult)
        if diffResult:
            print('Changes: ' + diffResult)

        if not diffResult:
            print('There was no diff. All is well.')
        
        returnedPages += 1
        print('>>sheet body<<', sheetBody)


    # Format diff for spreadsheet

        print('>>returned pages<<', returnedPages)
        if diffResult:
            sheetBody.append({

                'appendCells': {
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredValue': {'numberValue': ts}
                                },
                                {
                                    'userEnteredValue': {'stringValue': dt}
                                },
                                {
                                    'userEnteredValue': {'stringValue': diffResult}
                                }
                            ]
                        }
                    ],
                    'fields': "*"
                }})
            print('this should be printed to SHEET BODY', sheetBody)
        # Unless all pages have been tried and there are no diffs
        elif returnedPages == int(len(pages)) and not sheetBody:
            sheetBody.append({

                'appendCells': {
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredValue': {'numberValue': ts}
                                },
                                {
                                    'userEnteredValue': {'stringValue': dt}
                                },
                                {
                                    'userEnteredValue': {'stringValue': 'All quiet on the western front'}
                                }
                            ]
                        }
                    ],
                    'fields': "*"
                }})

    # Push diff to spreadsheet
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1ZWBONvazeyqyDcJ1q_aF8_bbV4iJzwEErrtnXuB9Y68'
    batchUpdateSheetBody = {'requests': sheetBody}
    print('BATCH UPDATE SHEET BODY', batchUpdateSheetBody)
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
                                       body=batchUpdateSheetBody).execute()
    print('Sheet body ', sheetBody)

if __name__ == '__main__':
    main()
