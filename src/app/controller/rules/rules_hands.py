import math
import numpy as np

class RulesHands:
  def __init__(self):
    pass
    
  def calculateDistance(self, point1: tuple, point2: tuple):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

  def _mapOk(self, h: float, w: float, handLandmarks: list, frame: np.ndarray) -> bool:
    points = {}
    ids = [1, 3, 4, 5, 6, 8, 12, 16, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks[id].x * w), int(handLandmarks[id].y * h))
    
    distance = self.calculateDistance(
        (points[4][0], points[4][1]),
        (points[8][0], points[8][1])
    )
    
    return (distance < 0.05 * w and
      points[5][1] > points[6][1] and
      points[1][1] > points[6][1] and
      points[3][0] > points[5][0])
    

  def _mapPositive(self, h: float, w: float, handLandmarks: list, frame: np.ndarray) -> bool:
    points = {}
    ids = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks[id].x * w), int(handLandmarks[id].y * h))
    
    
    return (points[4][1] < points[1][1] - 0.05 * h and
    points[8][1] > points[5][1] and
    points[12][1] > points[9][1] and
    points[16][1] > points[13][1] and
    points[20][1] > points[17][1])

  def _mapSpeak(self, h: float, w: float, handLandmarks: list, frame: np.ndarray) -> bool:
    points = {}
    ids = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]

    for id in ids:
      points[id] = (int(handLandmarks[id].x * w), int(handLandmarks[id].y * h))
    
    
    return (points[8][1] < points[5][1] - 0.05 * h and
      points[4][0] > points[1][0] and
      points[12][1] > points[9][1] and
      points[16][1] > points[13][1] and
      points[20][1] > points[17][1])

  def _mapSquid(self, h: float, w: float, handLandmarks: list, frame: np.ndarray) -> bool:
    points = {}
    ids = [2, 4, 6, 8, 9, 12, 13, 16, 17, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks[id].x * w), int(handLandmarks[id].y * h))

    
    return (points[8][1] < points[6][1] - 0.05 * h and
      points[4][0] < points[2][0] and
      points[20][1] > points[17][1] and
      points[12][1] > points[9][1] and
      points[16][1] > points[13][1])

  def _mapRock(self, h: float, w: float, handLandmarks: list, frame: np.ndarray) -> bool:
    points = {}
    ids = [6, 8, 9, 12, 13, 16, 18, 20]

    for id in ids:
      points[id] = (int(handLandmarks[id].x * w), int(handLandmarks[id].y * h))
    
    
    return (points[8][1] < points[6][1] - 0.05 * h and
        points[20][1] < points[18][1] and
        points[12][1] > points[9][1] and
        points[16][1] > points[13][1])
