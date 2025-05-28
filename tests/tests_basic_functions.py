import unittest
from app.controller.modules.controller_functions_actions import BasicFunctions
import numpy as np
from concurrent.futures import ThreadPoolExecutor

basic = BasicFunctions()
h = 480
w = 640
frame = np.zeros((h, w, 3), dtype=np.uint8)

class TestBasicFunctions(unittest.TestCase):
  
  def testCapturePhoto(self):
    with ThreadPoolExecutor() as executor:   
      self.assertIsInstance(basic.capturePhoto(frame, executor), str)

if __name__ == '__main__':
  asyncio.run(unittest.main())