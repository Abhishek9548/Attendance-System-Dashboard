import cv2
import pickle
import numpy as np
import os

# Initialize video capture and face detection model
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("Error: Could not access the camera.")
    exit()

facedetect = cv2.CascadeClassifier(r'C:\Users\HP\Documents\Att project\data\haarcascade_frontalface_default.xml')

# Initialize face data array and counters
faces_data = []
frame_count = 0
name = input("Enter Your Name: ")

# Capture and store face data
while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50))
        
        if len(faces_data) < 100 and frame_count % 10 == 0:
            faces_data.append(resized_img)
        
        frame_count += 1

        # Draw rectangle and count on frame
        cv2.putText(frame, f"Captured: {len(faces_data)}/100", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
    
    # Display frame
    cv2.imshow("Frame", frame)
    
    # Exit conditions
    if cv2.waitKey(1) == ord('q') or len(faces_data) == 100:
        break

# Release resources
video.release()
cv2.destroyAllWindows()

# Save face data
faces_data = np.asarray(faces_data).reshape(100, -1)
data_dir = r'C:\Users\HP\Documents\Att project\data'
os.makedirs(data_dir, exist_ok=True)

# Load existing data or initialize
names_file = os.path.join(data_dir, 'names.pkl')
faces_file = os.path.join(data_dir, 'faces.pkl')

if os.path.exists(names_file) and os.path.exists(faces_file):
    # Load existing faces and labels, ensuring consistency
    with open(names_file, 'rb') as f:
        names = pickle.load(f)
    with open(faces_file, 'rb') as f:
        faces = pickle.load(f)
    
    if faces.shape[0] != len(names):
        raise ValueError("Existing face data and names count do not match. Please fix the files.")
    
    names.extend([name] * 100)
    faces = np.append(faces, faces_data, axis=0)
else:
    names = [name] * 100
    faces = faces_data

# Save updated faces and labels
with open(names_file, 'wb') as f:
    pickle.dump(names, f)
with open(faces_file, 'wb') as f:
    pickle.dump(faces, f)
