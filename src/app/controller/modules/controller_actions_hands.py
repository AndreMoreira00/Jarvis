from app.controller.rules.rules_hands import RulesHands
from app.controller.modules.controller_functions_actions import BasicFunctions
import asyncio
import mediapipe as mp
from mediapipe.tasks import python

class ControllerHands:
  def __init__(self):
    self.mpHands = mp.solutions.hands
    self.hands = self.mpHands.Hands(
      static_image_mode=False,
      max_num_hands=2,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5)
    self.mpDrawing = mp.solutions.drawing_utils
    
    self.rulesHands = RulesHands()
    self._action: bool = False
    self.gestureCooldown: int = 0
    
    self.basicFunctions = BasicFunctions()
  
  async def _executeGesture(self, func_exe: object, func_act: object, side: str, hand_label: str, cooldown: int):
    for func_exe, func_act, side, cooldown in self._checks: 
      if func_act() and hand_label == side:
        self.gesture_cooldown = cooldown
        return func_exe
  
  async def checkGesture(self, executor, frame, cap, h, w, hand_landmarks):
    self._checks: tuple = [
      (lambda: executor.submit(self.basicFunctions.capturePhoto, frame, executor), lambda: self.rulesHands.Map_Ok(h, w, hand_landmarks, frame), "Right", 20),
      # (lambda: executor.submit(self.basicFunctions.captureVideo, cap, executor), lambda: self.rulesHands.Map_Positive(h, w, hand_landmarks, frame), "Left", 30),
      # (lambda: executor.submit(self.basicFunctions.audioToAudio, executor), lambda: self.rulesHands.Map_Speak(h, w, hand_landmarks, frame), "Right", 20),
      # (lambda: executor.submit(self.basicFunctions.imageAudio, frame, executor), lambda: self.rulesHands.Map_Squid(h, w, hand_landmarks, frame), "Left", 20), 
      # (lambda: executor.submit(self.basicFunctions.videoAudio, cap, executor), lambda: self.rulesHands.Map_Rock(h, w, hand_landmarks, frame), "Right", 30),
    ]
    
    for func_exe, func_act, side, state, cooldown in self.checks:
      if self._action == False and gesture_cooldown == 0:
        await self._executeGesture(func_exe, func_act, side, hand_label, cooldown)