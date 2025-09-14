import cv2
import face_recognition
import pickle
import os

ENCODINGS_FILE = "face_encodings.pkl"

def verify_face():
    print("\n[Face Auth] Please align your face with the camera...")

    if not os.path.exists(ENCODINGS_FILE):
        print("❌ No face encoding found. Please run setup.")
        return False

    with open(ENCODINGS_FILE, "rb") as f:
        saved_encoding = pickle.load(f)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open webcam")

    match_found = False
    attempts = 0

    while attempts < 5:
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image from webcam")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            live_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            result = face_recognition.compare_faces([saved_encoding], live_encoding)
            if result[0]:
                match_found = True
                print("✅ Face match successful.")
                break
            else:
                print("❌ Face did not match. Try again.")

        attempts += 1
        cv2.imshow("Face Authentication - Press 'q' to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Authentication canceled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return match_found
