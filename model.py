from imutils import face_utils
import numpy as np
import dlib
import cv2

# Constants
EAR_THRESHOLD = 0.3

# Facial landmark indices for eyes
(LEFT_EYE_START, LEFT_EYE_END) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(RIGHT_EYE_START, RIGHT_EYE_END) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Dlib face detector and landmark predictor
Detector = dlib.get_frontal_face_detector()
Predictor = dlib.shape_predictor("68_face_landmarks_shape_predictor.dat")


def compute_distance(point_a, point_b):
    """Compute the Euclidean distance between two points."""
    return np.linalg.norm(point_a - point_b)


def calculate_eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR) for an eye."""
    vertical_1 = compute_distance(eye[1], eye[5])
    vertical_2 = compute_distance(eye[2], eye[4])
    horizontal = compute_distance(eye[0], eye[3])
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear


def calculate_average_ear(face_landmarks):
    """Calculate the average EAR for both eyes."""
    left_eye = face_landmarks[LEFT_EYE_START : LEFT_EYE_END]
    right_eye = face_landmarks[RIGHT_EYE_START : RIGHT_EYE_END]

    left_ear = calculate_eye_aspect_ratio(left_eye)
    right_ear = calculate_eye_aspect_ratio(right_eye)

    return (left_ear + right_ear) / 2


def is_drowsy(ear_value):
    """Detect drowsiness based on EAR value."""
    return ear_value < EAR_THRESHOLD


def draw_landmarks_on_face(face, landmarks):
    """Draw landmarks on the face."""
    face_with_landmarks = face.copy()

    for (x, y) in landmarks:
        cv2.circle(
            img=face_with_landmarks,
            center=(x, y),
            radius=2,
            color=(255, 255, 255),
            thickness=-1
        )

    return face_with_landmarks


def detect_first_face(resized_frame):
    """Process a single video frame to detect the first face."""
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

    faces = Detector(gray_frame)
    return faces[0] if faces else None


def resize_frame(frame, width=320, height=240):
    """Resize the frame to a specific width and height."""
    return cv2.resize(frame, (width, height))


def get_face_landmarks(resized_frame, face):
    """Get facial landmarks for a given face."""
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    landmarks = Predictor(gray_frame, face)
    return face_utils.shape_to_np(landmarks)