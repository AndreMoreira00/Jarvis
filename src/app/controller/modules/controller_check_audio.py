import asyncio
from pygame import mixer

mixer.init()

class AudiosChecks():
  def __init__(self): 
    self.photoTakeSound = "src/app/data/sounds/photo_take.wav"
    self.audioStartSound = "src/app/data/sounds/audio_starter.wav"
    self.videoStartSound = "src/app/data/sounds/video_starter.wav" 
    self.videoEndSound = "src/app/data/sounds/video_out.wav"
    self._mixer = mixer
    
  async def playConfirmationSound(self, soundPath: str) -> None:
    sound = self._mixer.Sound(soundPath) 
    sound.play()
    await asyncio.sleep(sound.get_length())
    sound.stop()

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