import database
import logging
# import buzzer
import model
import cv2
import api
from threading import Thread
import winsound

DROWSY_CONSECUTIVE_FRAMES = 5
SLEEP_CONSECUTIVE_FRAMES = 10
alarm_status = 0
drowsy_frames_counter = 0

logging.basicConfig(filename="drowsiness_history.log", level=logging.INFO)

def alarm():
    #the alarm fuunction can be changed basd on the OS and envoniment
    #this functio will sound the alarm in case of drowsiness
    global alarm_status 

    while alarm_status == 1:

        winsound.Beep(1000,500)

def main():
    """Main function to start the drowsiness detection system."""
    global drowsy_frames_counter

    database.initialize_tables()

    capture = cv2.VideoCapture(0)
    (ret, frame) = capture.read()

    while ret:

        resized_frame = model.resize_frame(frame)
        face = model.detect_first_face(resized_frame)

        if face is not None:

            face_landmarks = model.get_face_landmarks(resized_frame, face)
            ear_value = model.calculate_average_ear(face_landmarks)
            is_drowsy = model.is_drowsy(ear_value)

            if is_drowsy:
                drowsy_frames_counter += 1

                if drowsy_frames_counter >= SLEEP_CONSECUTIVE_FRAMES:
                    winsound.Beep(1000,1500)
                    

                elif drowsy_frames_counter >= DROWSY_CONSECUTIVE_FRAMES:
                    # play long sound
                    winsound.Beep(1000,500)
                    pass

                logged_user_result = api.get_login_status()

                # if logged_user_result["logged_in"]:
                #     database.insert_drowsiness_event(ear_value, logged_user_result["username"])
                #     print(f"Logged in as {logged_user_result["username"]}")

                # else:
                #     print("Logged out")

            else:
                alarm_status = 0
                
                drowsy_frames_counter = 0

            face_with_landmarks = model.draw_landmarks_on_face(resized_frame, face_landmarks)
            cv2.imshow("Face Landmarks", face_with_landmarks)

            print(f"EAR Value: {ear_value}")

        cv2.imshow("Captured Frame", resized_frame)
        (ret, frame) = capture.read()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    capture.release()
    cv2.destroyAllWindows()
    # buzzer.clean_pins_up()

if __name__ == "__main__":
    main()