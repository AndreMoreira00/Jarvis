import os

def Config_Project():
  os.mkdir('audio')
  os.mkdir('image')
  os.mkdir('respoonse')
  os.mkdir('video')
  open('.env', 'a')
  
# pip install -r requirements.txt