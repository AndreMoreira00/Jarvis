import mimetypes
import os

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from jarvis.config import Config


class Manager:
    def __init__(self, config: Config):
        self.config = config
        self.CLIENT_SECRET = config.photos_client_secret
        self.CREDENTIALS_FILE = config.photos_token_file
        self.SCOPES = list(config.photos_scopes)

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

            with open(self.CREDENTIALS_FILE, "w") as token:
                token.write(creds.to_json())

        return creds.token

    def get_photo_url(self, access_token, photo_id):
        headers = {"Authorization": f"Bearer {access_token}", "Content-type": "application/json"}
        url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{photo_id}"
        response = requests.get(url, headers=headers)
        response_json = response.json()
        return response_json["baseUrl"]

    def upload_media(self, image_path):
        access_token = self.authorize_credentials()
        mime_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-Content-Type": mime_type,
            "X-Goog-Upload-Protocol": "raw",
        }

        with open(image_path, "rb") as f:
            image_data = f.read()

        response = requests.post(
            "https://photoslibrary.googleapis.com/v1/uploads", headers=headers, data=image_data
        )

        if response.status_code == 200:
            upload_token = response.text
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/json",
            }
            payload = {
                "newMediaItems": [
                    {
                        "simpleMediaItem": {
                            "fileName": os.path.basename(image_path),
                            "uploadToken": upload_token,
                        }
                    }
                ]
            }

            # Cria o item de midia na biblioteca. A consulta da URL final
            # (get_photo_url) ainda nao e usada; sera ligada quando a feature de
            # retorno de URL for concluida.
            requests.post(
                "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                headers=headers,
                json=payload,
            )
        else:
            response.raise_for_status()
