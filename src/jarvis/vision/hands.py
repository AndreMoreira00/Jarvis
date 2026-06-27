import mediapipe as mp

from jarvis.vision import gestures


class Hands:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_drawing = mp.solutions.drawing_utils

    # Wrappers de paridade: delegam para as funcoes puras de gestures.py.
    # Mantem a assinatura legada (h, w, hand_landmarks, frame) e o contrato
    # True/None do call-site atual (frame e ignorado). O None some quando o
    # wrapper for removido na reestruturacao (Onda 6).
    def Calculate_Distance(self, point1, point2):
        return gestures.distance(point1, point2)

    def Map_Ok(self, h, w, hand_landmarks, frame):
        return True if gestures.is_ok(h, w, hand_landmarks) else None

    def Map_Positive(self, h, w, hand_landmarks, frame):
        return True if gestures.is_positive(h, w, hand_landmarks) else None

    def Map_Speak(self, h, w, hand_landmarks, frame):
        return True if gestures.is_speak(h, w, hand_landmarks) else None

    def Map_Squid(self, h, w, hand_landmarks, frame):
        return True if gestures.is_squid(h, w, hand_landmarks) else None

    def Map_Rock(self, h, w, hand_landmarks, frame):
        return True if gestures.is_rock(h, w, hand_landmarks) else None
