import os

def Config_Project():
  # os.mkdir('audio')
  # os.mkdir('image')
  os.mkdir('response')
  # os.mkdir('video')
  os.mkdir('midia')
  open('.env', 'a')
  
# pip install -r requirements.txt
Config_Project()