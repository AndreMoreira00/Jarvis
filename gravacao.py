import cv2
import numpy as np

# def gravar(frames):
    # cv2.imwrite(f"Images/Video_Brabo.mp4", frames)



# frames = []


camera = cv2.VideoCapture(0)
rodando = True
# cont = 0
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 60.0, (640,480))

while rodando:

    status, frame = camera.read()
    
    cv2.imshow("Camera", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # cont+=1
    
    # frames.append(frame)
    
    # if cont == 120:
    #     rodando = False
        
# gravar(frames)

# cap.release()
cv2.destroyAllWindows()