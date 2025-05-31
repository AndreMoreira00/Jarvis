from app.controller.rules.rules_hands import RulesHands
from app.controller.modules.controller_functions_actions import BasicFunctions
import mediapipe as mp
from mediapipe.tasks import python # type: ignore
import numpy as np

class ControllerHands:
  def __init__(self):
    self.mpHands: object = mp.solutions.hands #type: ignore
    self.hands: object = self.mpHands.Hands( #type: ignore
      static_image_mode=False,
      max_num_hands=2,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5)
    self.mpDrawing: object = mp.solutions.drawing_utils #type: ignore
    
    self.rulesHands: object = RulesHands()
    self.basicFunctions: object = BasicFunctions()
    self._action: bool = False
    self.gestureCooldown: int = 0
  
  def _executeGesture(self, func_exe: object, func_act: object, side: str, hand_label: str, cooldown: int):
    if func_act() and hand_label == side: # type: ignore
      self.gestureCooldown = cooldown
      self._action = True
      func_exe() #type: ignore
      self._action = False
  
  def checkGesture(self, executor: object, frame: np.ndarray, cap: object, h:float, w:float, hand_landmarks:object, hand_label:str)-> None: # type: ignore
    _checks: tuple[function, function] = [
      (lambda: executor.submit(self.basicFunctions.capturePhoto, frame, executor), lambda: self.rulesHands._mapOk(h, w, hand_landmarks), "Right", 20), # type: ignore
      # (lambda: executor.submit(self.basicFunctions.captureVideo, cap, executor), lambda: self.rulesHands._mapPositive(h, w, hand_landmarks), "Left", 30),
      # (lambda: executor.submit(self.basicFunctions.audioToAudio, executor), lambda: self.rulesHands._mapSpeak(h, w, hand_landmarks), "Right", 20),
      # (lambda: executor.submit(self.basicFunctions.imageAudio, frame, executor), lambda: self.rulesHands._mapSquid(h, w, hand_landmarks), "Left", 20), 
      # (lambda: executor.submit(self.basicFunctions.videoAudio, cap, executor), lambda: self.rulesHands._mapRock(h, w, hand_landmarks), "Right", 30),
    ]
    
    for func_exe, func_act, side, cooldown in _checks: # type: ignore
      if self._action == False and self.gestureCooldown == 0:
        self._executeGesture(func_exe, func_act, side, hand_label, cooldown) # type: ignore