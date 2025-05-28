import unittest
from app.apis.routes.google_gemini_routes import RoutesGemini
import asyncio

test = RoutesGemini()

class TestGeminiRoutes(unittest.TestCase):
  
  async def testTranslateNormal(self):
    await self.assertEqual(test._dictate("Olá"), None)

  async def testTranslateMargin(self):
    await self.assertEqual(test._dictate(str("Olá"*1000000)), None)
    
  async def testTranslateType(self):
    with self.assertRaises(TypeError):
      await test._dictate(100)
  
  async def testTextToTextNormal(slef):
    await self.assertEqual(test.textToText("Olá Tudo bem?"), None)
    
  async def testTextToTextMargin(slef):
    await self.assertEqual(test.textToText(str("Olá"*1000000)), None)
    
  async def testTextToTextType(slef):
    with self.assertRaises(TypeError):
      await test.textToText(100)
  
  async def testImageToTextNormal(self):
    await self.assertEqual(test.imageToText("./src/app/data/image.jpg","Descreva"), None)
    
  async def testImageToTextMargin(self):
    await self.assertEqual(test.imageToText("./src/app/data/image.jpg",str("Ola"*1000000)), None)
    
  async def testImageToTextType(self):
    with self.assertRaises(TypeError):
      await test.imageToText(100,100)
    
  async def testVideoToTextNormal(self):
    await self.assertEqual(test.videoToText("./src/app/data/video.mp4","Descreva"), None)
    
  async def testVideoToTextMargin(self):
    await self.assertEqual(test.videoToText("./src/app/data/video.mp4",str("Ola"*1000000)), None)
    
  async def testVideoToTextType(self):
    with self.assertRaises(TypeError):
      await test.videoToText(100, 100)

if __name__ == '__main__':
  asyncio.run(unittest.main())