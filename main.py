import cv2
import tkinter as tk
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Camera App")

        # Inicia a câmera
        self.cap = cv2.VideoCapture(0)

        # Cria um label para mostrar a imagem
        self.image_label = tk.Label(window)
        self.image_label.pack()

        # Cria um botão para tirar a foto
        self.capture_button = tk.Button(window, text="Tirar Foto", command=self.capture)
        self.capture_button.pack()

        self.update_frame()

    def update_frame(self):
        # Captura a imagem da câmera
        ret, frame = self.cap.read()
        if ret:
            # Converte a imagem para RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Converte a imagem para um formato que o tkinter pode usar
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.image_label.imgtk = imgtk
            self.image_label.configure(image=imgtk)

        # Atualiza a imagem a cada 10ms
        self.image_label.after(10, self.update_frame)

    def capture(self):
        # Captura uma imagem
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite("captura.jpg", frame)  # Salva a imagem
            print("Foto tirada e salva como 'captura.jpg'")

    def __del__(self):
        # Libera a câmera quando a aplicação é fechada
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
