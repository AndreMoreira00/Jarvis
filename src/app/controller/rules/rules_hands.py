import math

class RulesHands:
  def __init__(self):
    pass
    
  def calculateDistance(self, point1: tuple[float, float], point2: tuple[float, float]) -> float:
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

  def _mapOk(self, h: float, w: float, handLandmarks: list[float]) -> bool: #type: ignore
    points: dict[int, float] = {}
    ids: list[int] = [1, 3, 4, 5, 6, 8, 12, 16, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks.landmark[id].x * w), int(handLandmarks.landmark[id].y * h)) # type: ignore
    
    distance: float = self.calculateDistance(
        (points[4][0], points[4][1]), # type: ignore
        (points[8][0], points[8][1])  # type: ignore
    )
    
    return (distance < 0.05 * w and #type: ignore
      points[5][1] > points[6][1] and # type: ignore
      points[1][1] > points[6][1] and # type: ignore
      points[3][0] > points[5][0]) # type: ignore
    

  def _mapPositive(self, h: float, w: float, handLandmarks: list[float]) -> bool:
    points: dict[int, float] = {}
    ids: list[int] = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks.landmark[id].x * w), int(handLandmarks.landmark[id].y * h)) #type: ignore
    
    
    return (points[4][1] < points[1][1] - 0.05 * h and #type: ignore
    points[8][1] > points[5][1] and #type: ignore
    points[12][1] > points[9][1] and #type: ignore
    points[16][1] > points[13][1] and #type: ignore
    points[20][1] > points[17][1]) #type: ignore

  def _mapSpeak(self, h: float, w: float,  handLandmarks: list[float]) -> bool:
    points: dict[int, float] = {}
    ids: list[int] = [1, 4, 5, 8, 9, 12, 13, 16, 17, 20]

    for id in ids:
      points[id] = (int(handLandmarks.landmark[id].x * w), int(handLandmarks.landmark[id].y * h)) #type: ignore
    
    
    return (points[8][1] < points[5][1] - 0.05 * h and #type: ignore
      points[4][0] > points[1][0] and #type: ignore
      points[12][1] > points[9][1] and #type: ignore
      points[16][1] > points[13][1] and #type: ignore
      points[20][1] > points[17][1]) #type: ignore

  def _mapSquid(self, h: float, w: float,  handLandmarks: list[float]) -> bool:
    points: dict[int, float] = {}
    ids: list[int] = [2, 4, 6, 8, 9, 12, 13, 16, 17, 20]
    
    for id in ids:
      points[id] = (int(handLandmarks.landmark[id].x * w), int(handLandmarks.landmark[id].y * h)) #type: ignore

    
    return (points[8][1] < points[6][1] - 0.05 * h and #type: ignore
      points[4][0] < points[2][0] and #type: ignore
      points[20][1] > points[17][1] and #type: ignore
      points[12][1] > points[9][1] and #type: ignore
      points[16][1] > points[13][1]) #type: ignore

  def _mapRock(self, h: float, w: float,  handLandmarks: list[float]) -> bool:
    points: dict[int, float] = {}
    ids: list[int] = [6, 8, 9, 12, 13, 16, 18, 20]

    for id in ids:
      points[id] = (int(handLandmarks.landmark[id].x * w), int(handLandmarks.landmark[id].y * h)) #type: ignore
    
    
    return (points[8][1] < points[6][1] - 0.05 * h and #type: ignore
        points[20][1] < points[18][1] and #type: ignore
        points[12][1] > points[9][1] and #type: ignore
        points[16][1] > points[13][1]) #type: ignore
