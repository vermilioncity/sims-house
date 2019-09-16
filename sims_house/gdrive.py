import os.path
import pickle
from time import sleep

import googleapiclient
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_parent_folder_id(drive_service):

    """ Creates or returns a specific folder to upload images into """

    query = "name contains 'sims-house' and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query).execute()
    parent_folder = results.get('files', [])

    if not parent_folder:
        body = {'name': 'sims-house', "mimeType": "application/vnd.google-apps.folder"}
        parent_folder = drive_service.files().create(body=body).execute()
    else:
        parent_folder = next(f for f in parent_folder)

    return parent_folder['id']


def upload_image(drive_service, image_id, img, folder_id):

    """ Upload an individual image to Google Drive"""

    media_body = MediaIoBaseUpload(img, mimetype='image/jpeg', chunksize=1024*1024, resumable=True)

    body =  {"name": image_id,
             "parents": [folder_id],
             "mimeType": "image/jpeg"}
    
    while True:
        try:
            drive_service.files().create(body=body, media_body=media_body).execute()
            break
        except googleapiclient.errors.HttpError:
            sleep(1)


def get_creds():

    """ i hate how clunky this is...  meh """

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds
