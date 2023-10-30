import threading
import winsound
import cv2
import imutils
import pyttsx3
import numpy as np

captureD = cv2.VideoCapture(0, cv2.CAP_DSHOW)

captureD.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
captureD.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = captureD.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0

def beep_alarm():
    global alarm
    engine = pyttsx3.init()  # Initialize the text-to-speech engine
    for _ in range(5):
        if not alarm_mode:
            break
        print("ALARM")
        engine.say("Movement detected")  # Text-to-speech output
        engine.runAndWait()  # Wait for the speech to finish
        winsound.Beep(2500, 1000)  # Beep sound
    alarm = False

while True:

    _, frame = captureD.read()
    frame = imutils.resize(frame, width=500)

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (21, 21), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        color_img = np.zeros((threshold.shape[0], threshold.shape[1], 3), dtype=np.uint8)
        color_img[:, :] = (255, 0, 0)  # Background blue
        color_img[threshold == 255] = (0, 255, 255)  # Movement in yellow

        if threshold.sum() > 300000:
            alarm_counter += 1
            # Add text to the color_img when movement is detected
            cv2.putText(color_img, "Movement Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)  # Yellow text
        else:
            if alarm_counter > 0:
                alarm_counter -= 1

        cv2.imshow("cam", color_img)
    else:
        cv2.imshow("cam", frame)

    if alarm_counter > 20:
        if not alarm:
            alarm = True
            threading.Thread(target=beep_alarm).start()

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    if key_pressed == ord("q"):
        alarm_mode = False
        break

captureD.release()
cv2.destroyAllWindows()