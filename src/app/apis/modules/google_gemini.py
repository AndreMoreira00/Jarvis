import os
import json
from dotenv import load_dotenv 
import google.generativeai as genai
from app.error.error_system_logs import errorSystemLogUser, errorSystemLogDev

class Gemini:
  
  try:
    load_dotenv()
    __KEY_GEMINI_API: str = os.getenv("KEY_GEMINI_API")
    genai.configure(api_key=__KEY_GEMINI_API)
  except Exception as e:
    errorSystemLogUser(f"Error: Load Keys of client Gemini! ({e})")
    errorSystemLogDev(f"Error google_gemini.py - Load Keys of client Gemini {e}")
  try:
    f = open("./src/app/.envs/modules.json")
    __data = json.load(f)
    _template: str = __data["template"]["init_prompt"]
    _modelSelect: str = __data["template"]["model_select"]
  except Exception as e:
    errorSystemLogUser(f"Error: Load failed model Gemini and prompt! ({e})")
    errorSystemLogDev(f"Error google_gemini.py - Load failed model Gemini and prompt {e}")
  
  def __init__(self):
    for i in range(3):
      try:
        self._model: object = genai.GenerativeModel(self._modelSelect, system_instruction=self._template)
      except Exception as e:
        errorSystemLogUser(f"Error: Create agent Gemini! ({e})")
        errorSystemLogDev(f"Error google_gemini.py - Create agent Gemini {e}")
        
    self._voice: str = "pt-BR-AntonioNeural"
    self._pathFile: str = "./src/app/data/response.mp3"
