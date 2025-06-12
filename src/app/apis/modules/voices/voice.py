from app.error.error_system_logs import errorSystemLogDev, errorSystemLogUser


class Voice:
  def __init__(self):
    self._charRemoved: dict[str, str]  = {
      '\t': ' ',
      '*': ' ',
      '\u200b': ' ',
      '\u200c': ' ',
      '\u200d': ' ',
      '\ufeff': ' ',
      '  ': ' ',
    }
    
    self._voice: str = "pt-BR-AntonioNeural"
    self._pathToResponse = "./src/app/data/response.mp3"
    
    async def _dictate(self, text: str) -> None: # type: ignore
      for old, new in self._charRemoved.items(): # type: ignore
        text: str = text.replace(old, new) # type: ignore
      text: str = text.strip()
        
      try:  
        communicate: object = edge_tts.Communicate(text, self._voice) #type: ignore
      except RuntimeError:
        await errorSystemLogUser("Error: Runtime Error in dictate of Jarvis")
        errorSystemLogDev("Error voice.py - Runtime Error in dictate of Jarvis")
      finally:
        await communicate.save(self._pathToResponse) #type: ignore
        
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