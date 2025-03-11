import cv2
import time
def Capture_Video(self, cap, gravando):
    self.ACTION = True
    self.estado = not gravando  # Toggle recording state
    
    if self.estado and self.ACTION:
        print("Iniciando gravação...")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timesr = time.strftime("%Y%m%d_%H%M%S")
        fps = 30
        out = cv2.VideoWriter(f'video/{timesr}.avi', fourcc, fps, (640, 480))
        
        while self.estado:
            status, frame = cap.read()
            if not status:
                break
                
            # Display the frame
            cv2.imshow('Video Recording', frame)
            
            # Add a way to check for hand gesture or key press to stop recording
            # For example, use a key press for now:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Press 'q' to stop recording
                self.estado = False
                
            out.write(frame)
            
        out.release()
        print(f"Gravação salva: video/{timesr}.avi")
        self.ACTION = False
    else:
        print("Gravação finalizada.")