import unittest
import asyncio
from app.controller.modules.controller_check_audio import AudiosChecks

audios = AudiosChecks()

class TestErrorSystemLog(unittest.TestCase):
  
  async def testphotoTakeSound(self):
    await self.assertEqual(audios.playConfirmationSound(audios.photoTakeSound), None)
    
  async def testaudioStartSound(self):
    await self.assertEqual(audios.playConfirmationSound(audios.audioStartSound), None)
    
  async def testvideoStartSsound(self):
    await self.assertEqual(audios.playConfirmationSound(audios.videoStartSsound), None)
    
  async def testvideoEndSound(self):
    await self.assertEqual(audios.playConfirmationSound(audios.videoEndSound), None)
  
if __name__ == '__main__':
  asyncio.run(unittest.main())
  
