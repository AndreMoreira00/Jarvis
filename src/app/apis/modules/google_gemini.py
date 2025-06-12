import os
import json
from dotenv import load_dotenv 
import google.generativeai as genai
from app.error.error_system_logs import errorSystemLogUser, errorSystemLogDev
import asyncio

class Gemini:
  
  try:
    load_dotenv()
    __KEY_GEMINI_API = os.getenv("KEY_GEMINI_API") 
    genai.configure(api_key=__KEY_GEMINI_API) # type: ignore
  except Exception as e:
    asyncio.run(errorSystemLogUser(f"Error: Load Keys of client Gemini! ({e})"))
    errorSystemLogDev(f"Error google_gemini.py - Load Keys of client Gemini {e}")
  try:
    f = open("./src/app/.envs/modules.json")
    __data = json.load(f)
    _template: str = __data["template"]["init_prompt"]
    _modelSelect: str = __data["template"]["model_select"]
  except Exception as e:
    asyncio.run(errorSystemLogUser(f"Error: Load failed model Gemini and prompt! ({e})")) 
    errorSystemLogDev(f"Error google_gemini.py - Load failed model Gemini and prompt {e}")
  
  def __init__(self):
    for i in range(3): # type: ignore
      try:
        self._model: object = genai.GenerativeModel(self._modelSelect, system_instruction=self._template) # type: ignore
      except Exception as e:
        asyncio.run(errorSystemLogUser(f"Error: Create agent Gemini! ({e})")) 
        errorSystemLogDev(f"Error google_gemini.py - Create agent Gemini {e}")
        
# Copyright 2025 André Fernandes Nascimento Moreira
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.