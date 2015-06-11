#!/usr/bin/python
import os
import time
import subprocess
import httplib2
import pprint
from time import sleep
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

def uploadFile(filename):
    # Copy your credentials from the console
    CLIENT_ID = '319850744543-9ggq00pu89osfbtie7crrk37931fpt7p.apps.googleusercontent.com'
    CLIENT_SECRET = 'xMbVOC4TloMTeEUw-_nqjQo0'

    # Check https://developers.google.com/drive/scopes for all available scopes
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

    # Redirect URI for installed apps
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    # Path to the file to upload
    FILENAME = filename

    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                               redirect_uri=REDIRECT_URI)
    # create the storage object with a file that is hopefully there
    storage = Storage('cred_file')
    # attempt to get the creds
    credentials = storage.get()

    # if the credentials object is null or it's invalid run the old school auth
    if credentials is None or credentials.invalid:
        authorize_url = flow.step1_get_authorize_url()
        print 'Go to the following link in your browser: ' + authorize_url
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage = Storage('cred_file') # open a storage file
        storage.put(credentials) # put the credentials in the storage file

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    drive_service = build('drive', 'v2', http=http)

    # Insert a file
    media_body = MediaFileUpload(FILENAME, mimetype='video/mp4', resumable=True)
    body = {
      'title': filename,
      'description': filename+" Lecture",
      'mimeType': 'video/mp4'
    }

    file = drive_service.files().insert(body=body, media_body=media_body).execute()
    pprint.pprint(file)



class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        now = time.strftime("%c")
        for i in os.listdir(os.getcwd()):
            if i.endswith(".ts"): 
                print "Creating mp4 version"
                output_filename = now
                cmd = "avconv -i "+str(i)+" -c:v copy -c:a copy -bsf:a aac_adtstoasc "+i[:-3]+".mp4"
                print cmd
		p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p.wait()
                remove_command = "rm "+i
                p2 = subprocess.Popen(remove_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                #sleep(20)
                uploadFile(i[:-3]+".mp4")
            else:
                continue


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
