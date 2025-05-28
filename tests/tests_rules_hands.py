import unittest
from unittest.mock import Mock, MagicMock
from app.controller.rules.rules_hands import RulesHands
import numpy as np

hands = RulesHands()
h = 480
w = 640
fake_landmark = MagicMock()
fake_landmark.x = 0.5
fake_landmark.y = 0.5
fake_landmark.z = 0.0
handLandmarks = [fake_landmark for _ in range(21)]
frame = np.zeros((h, w, 3), dtype=np.uint8)

class TestRulesHands(unittest.TestCase):
  
  def testMapOK(self):  
    self.assertFalse(hands.mapOk(h, w, handLandmarks, frame))
  
  def testMapPositive(self):  
    self.assertFalse(hands.mapPositive(h, w, handLandmarks, frame))
  
  def testMapSpeak(self):  
    self.assertFalse(hands.mapSpeak(h, w, handLandmarks, frame))
  
  def testMapSquid(self):  
    self.assertFalse(hands.mapSquid(h, w, handLandmarks, frame))

  def testMapRock(self):  
    self.assertFalse(hands.mapRock(h, w, handLandmarks, frame))

if __name__ == '__main__':
  asyncio.run(unittest.main())