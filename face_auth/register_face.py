import cv2
import face_recognition
import pickle
import os

ENCODINGS_FILE = "face_encodings.pkl"

def capture_and_save_face():
    print("\n[Face Setup] Please look into the camera...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open webcam")

    while True:
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image from webcam")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            with open(ENCODINGS_FILE, "wb") as f:
                pickle.dump(face_encoding, f)

            print("✅ Face registered successfully.")
            break
        else:
            print("❌ No face detected. Try again...")

        cv2.imshow("Face Registration - Press 'q' to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Registration canceled.")
            break

    cap.release()
    cv2.destroyAllWindows()
