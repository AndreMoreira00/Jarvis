import os
import json
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Manager:
    def __init__(self):
        self.CLIENT_SECRET = './env/client_secret.json'
        self.CREDENTIALS_FILE = './env/token.json'
        self.SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
    
    def authorize_credentials(self):
        creds = None

        if os.path.exists(self.CREDENTIALS_FILE):
            creds = Credentials.from_authorized_user_file(self.CREDENTIALS_FILE, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.CREDENTIALS_FILE, 'w') as token:
                token.write(creds.to_json())

        return creds.token 

    def getPhotoUrl(self, access_token, photo_id):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/json"
        }
        url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{photo_id}"
        response = requests.get(url, headers=headers)
        response_json = response.json()
        return response_json["baseUrl"]

    def uploadMidia(self, image_path):
        access_token = self.authorize_credentials()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-type': 'application/octet-stream',
            'X-Goog-Upload-Content-Type': 'image/jpeg',
            'X-Goog-Upload-Protocol': 'raw'
        }

        with open(image_path, 'rb') as f:
            image_data = f.read()

        response = requests.post('https://photoslibrary.googleapis.com/v1/uploads',
                                 headers=headers, data=image_data)

        if response.status_code == 200:
            upload_token = response.text
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-type': 'application/json'
            }
            payload = {
                "newMediaItems": [
                    {
                        "simpleMediaItem": {
                            "fileName": os.path.basename(image_path),
                            "uploadToken": upload_token
                        }
                    }
                ]
            }

            response = requests.post(
                'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
                headers=headers, json=payload
            )
            response_json = response.json()
            photo_id = response_json['newMediaItemResults'][0]['mediaItem']['id']
            photo_url = self.getPhotoUrl(access_token, photo_id)
        else:
            response.raise_for_status()