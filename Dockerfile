FROM python:3.9-slim
WORKDIR /JARVIS
COPY . .
RUN pip install --upgrade pip
COPY requirements.txt .
# RUN pip install -r requirements.txt --no-cache-dir 
RUN pip install mediapipe
ENV API_GEMINI=AIzaSyDB8myvxciBXBAbZtspVZuzQua3FYI4hpo
CMD [ "python", "./main.py" ]