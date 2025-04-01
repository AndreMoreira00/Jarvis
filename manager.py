import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import requests
import os
from concurrent.futures import ThreadPoolExecutor # Torna as funções sincronas

class Manager:
  def __init__(self):
    self.CLIENT_SECRET = './env/client_secret.json'
    self.SCOPE = 'https://www.googleapis.com/auth/photoslibrary'
    self.STORAGE = Storage('./env/credentials.storage') #Transforma em Json para credenciais 
  
  def authorize_credentials(self):
    if os.path.exists('./env/credentials.storage'):
      credentials = self.STORAGE.get() #Pega o conteudo do Json atual
      if credentials and not credentials.invalid: #Verifica se o token é valido
        if credentials.access_token_expired: # Verifica se o token experiou
          credentials.refresh(httplib2.Http()) #Recria o token
    else:
      flow = flow_from_clientsecrets(self.CLIENT_SECRET, scope=self.SCOPE) # Caso não tenha o arquivo ele vai solicitar o acesso ao Host
      http = httplib2.Http() # Requisicao HTTP
      credentials = run_flow(flow, self.STORAGE, http=http) # Obtem uma credencial de um novo usario
      print("Contact the HOST to access the Beta Test version.\nandremoreira102030@gmail.com\nSubject: Credentials Jarvir for client test.\nHello André Moreira, I wanted to test your Jarvis project, but I don't have credentials for Google Project.\nEmail: <your-email>. ") # Passa o convite de teste para novos usuarios
    
    return credentials.access_token # Obtem o token da credencial
  
  def getPhotoUrl(self,access_token, photo_id):
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-type": "application/json"
    }
    url = "https://photoslibrary.googleapis.com/v1/mediaItems/" + photo_id
    response = requests.get(url, headers=headers)
    response_json = response.json()
    photo_url = response_json["baseUrl"]
    return photo_url
    
  def uploadMidia(self, midia_path):
    access_token = self.authorize_credentials()
    
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Content-Type': 'image/jpeg',
        'X-Goog-Upload-Protocol': 'raw'
    }

    with open(midia_path, 'rb') as f:
        midia_data = f.read()

    response = requests.post('https://photoslibrary.googleapis.com/v1/uploads',
                            headers=headers, data=midia_data)

    if response.status_code == requests.codes.ok:
        upload_token = response.text
        headers = {
            'Authorization': 'Bearer %s' % access_token,
            'Content-type': 'application/json'
        }
        payload = {
            "newMediaItems": [
                    {
                        "simpleMediaItem": {
                            "fileName": os.path.basename(midia_path),
                            "uploadToken": upload_token
                        }
                    }
                ]
            }
        
        response = requests.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
                                headers=headers, json=payload)   
        json_response = response.json()
        photo_id = json_response['newMediaItemResults'][0]['mediaItem']['id']
        photo_url = self.getPhotoUrl(access_token, photo_id)
    else:
        response.raise_for_status()

# with ThreadPoolExecutor() as executor:
#   maneger = Manager()
#   maneger.uploadMidia('./image/Colors.jpeg')