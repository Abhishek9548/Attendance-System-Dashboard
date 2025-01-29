import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from win32com.client import Dispatch

# Function to play speech
def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

# Function to log attendance
def log_attendance(name, timestamp, date):
    filename = f"Attendance/Attendance_{date}.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['NAME', 'TIME'])
        writer.writerow([name, timestamp])

# Initialize video capture and face detection model
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("Error: Could not access the camera.")
    exit()

facedetect = cv2.CascadeClassifier(r'C:\Users\HP\Documents\Att project\data\haarcascade_frontalface_default.xml')

# Load face and label data
try:
    with open(r'C:\Users\HP\Documents\Att project\data\names.pkl', 'rb') as w:
        LABELS = pickle.load(w)
    with open(r'C:\Users\HP\Documents\Att project\data\faces.pkl', 'rb') as f:
        FACES = pickle.load(f)

    LABELS = np.array(LABELS).flatten()
    if FACES.shape[0] != len(LABELS):
        raise ValueError("Mismatch between number of face samples and labels. Please verify data files.")
except FileNotFoundError:
    print("Data files not found. Ensure 'names.pkl' and 'faces.pkl' exist in the specified directory.")
    exit()

# Train KNeighbors classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Load background image
imgBackground = cv2.imread(r"C:\Users\HP\Documents\Att project\background.png")

# Main loop for face detection and recognition
confirmed_attendance = set()  # Track confirmed attendance to avoid duplicates

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    recognized_name = None

    if len(faces) == 0:
        cv2.putText(frame, "Face Not Found", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    else:
        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
            output = knn.predict(resized_img)
            recognized_name = output[0]

            # Draw rectangles and name on frame
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            cv2.putText(frame, recognized_name, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

    # Overlay video frame onto background image
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Attendance System", imgBackground)

    # Capture key events
    k = cv2.waitKey(1)
    if k == ord('o') and recognized_name:
        if recognized_name not in confirmed_attendance:
            # Confirm and log attendance only if not already logged
            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            log_attendance(recognized_name, timestamp, date)
            confirmed_attendance.add(recognized_name)
            speak("Attendance Taken.")
            time.sleep(2)
    elif k == ord('q'):
        break

# Release video capture and close windows
video.release()
cv2.destroyAllWindows()


