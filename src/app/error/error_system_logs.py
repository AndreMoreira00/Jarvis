import edge_tts
from pygame import mixer
import asyncio

async def errorSystemLogUser(error: str) -> None:
  mixer.init()
  _voice: str = "pt-BR-AntonioNeural"
  _mixer: object = mixer
  _pathFile: str = "./src/app/error/error.mp3"
  error_text: str = error.strip()
  communicate = edge_tts.Communicate(error_text, _voice)
  await communicate.save(_pathFile)
  sound = _mixer.Sound(_pathFile) 
  sound.play()
  await asyncio.sleep(sound.get_length())
  sound.stop()
  
def errorSystemLogDev(error: str) -> None:
  print(f"ERROR DEV: {error}")
  
  
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