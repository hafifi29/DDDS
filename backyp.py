from imutils import face_utils
from threading import Thread
import numpy as np
import database
import logging
import buzzer
import dlib
import cv2

CONSECUTIVE_FRAMES = 5
EAR_THRESHOLD = 0.3

(left_eye_start, left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(right_eye_start, right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("68_face_landmarks_shape_predictor.dat")

alarm_status = False
frame_count = 0
counter = 0

logging.basicConfig(filename="drowsiness_history.log", level=logging.INFO)

def compute_distance(point_a, point_b):
    """Compute the Euclidean distance between two points."""

    return np.linalg.norm(point_a - point_b)

def calculate_ear(eye):
    """Calculate the Eye Aspect Ratio (EAR) for an eye."""

    vertical_distance_1 = compute_distance(eye[1], eye[5])
    vertical_distance_2 = compute_distance(eye[2], eye[4])
    horizontal_distance = compute_distance(eye[0], eye[3])

    vertical_distance = vertical_distance_1 + vertical_distance_2
    ear = vertical_distance / (2.0 * horizontal_distance)

    return ear

def get_final_ear(face_landmarks):
    """Calculate the average EAR for both eyes."""

    left_eye = face_landmarks[left_eye_start:left_eye_end]
    right_eye = face_landmarks[right_eye_start:right_eye_end]

    left_ear = calculate_ear(left_eye)
    right_ear = calculate_ear(right_eye)
    return (left_ear + right_ear) / 2

def detect_drowsiness(ear_value):
    """Detect drowsiness based on EAR value."""
    global alarm_status, counter

    if ear_value < EAR_THRESHOLD:
        counter += 1
        if counter >= CONSECUTIVE_FRAMES:
            if not alarm_status:
                alarm_status = True
                Thread(target=buzzer.start_alarm, daemon=True).start()
                logging.info(f"Drowsiness detected at frame {frame_count}")

    else:
        counter = 0
        alarm_status = False
        buzzer.power_buzzer_off()

def draw_face_landmarks(face, landmarks):
    """Draw landmarks on the face."""
    img = face.copy()

    for (x, y) in landmarks:
        cv2.circle(img, (x, y), 2, (255, 255, 255), -1)

    return img

def process_frame(frame):
    """Process a single video frame to detect drowsiness."""
    global frame_count

    resized_frame = cv2.resize(frame, (320, 240))
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)

    if len(faces) > 0:
        face = faces[0]
        landmarks = predictor(gray_frame, face)
        landmarks_np = face_utils.shape_to_np(landmarks)

        ear_value = get_final_ear(landmarks_np)
        frame_count += 1
        print(f"Frame {frame_count}: EAR = {ear_value:.2f}")

        database.insert_drowsiness_event(ear_value, frame_count)
        detect_drowsiness(ear_value)

        face_with_landmarks = draw_face_landmarks(resized_frame, landmarks_np)
        cv2.imshow("Face with Landmarks", face_with_landmarks)

    return resized_frame

def main():
    """Main function to start the drowsiness detection system."""
    database.initialize_drowsiness_events()
    capture = cv2.VideoCapture(0)

    while True:
        (ret, frame) = capture.read()

        if not ret:
            break

        processed_frame = process_frame(frame)

        if frame_count % 10 == 0:
            cv2.imshow("Processed Frame", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()
    buzzer.clean_pins_up()

if __name__ == "__main__":
    main()
