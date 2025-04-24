import os

def Config_Project():
  os.mkdir('response')
  os.mkdir('midia')
  open('.env', 'a')
  
# pip install -r requirements.txt
Config_Project()