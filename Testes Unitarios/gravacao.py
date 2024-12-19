import cv2
import numpy as np
import time

def save_video():
    cap = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    timesr = time.strftime("%Y%m%d_%H%M%S")
    
    duration_in_seconds = 15
    fps = 30
    
    out = cv2.VideoWriter(f'Video/{timesr}.avi', fourcc, fps, (640, 480))
    
    total_frames = duration_in_seconds * fps

    frame_count = 0
    while frame_count < total_frames:
        
        status, frame = cap.read()
        out.write(frame)
        frame_count+=1
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
save_video()