import cv2
import pickle as pkl
import face_recognition
import numpy as np
import os
from PIL import Image
import io
import LCD2inch4_lib  # Adjust this import based on your library's location

WHITE = 0xFF

def face_rec():
    frame_count = 0
    video_capture = cv2.VideoCapture(0)  # For internal webcam, VideoCapture(1) for external webcam
    video_capture.set(3, 500)
    video_capture.set(4, 500)

    # Load Encoding file
    absolute_path = os.path.dirname(__file__)
    file = open(absolute_path + "//" + "EncodedFile.p", "rb")
    encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID
    file.close()

    print(individual_ID)  # to check id's loaded

    # Initialize LCD
    disp = LCD2inch4_lib.LCD_2inch4(44, 0, '/dev/spidev0.0')
    disp.lcd_init_2inch4()
    disp.lcd_clear(WHITE)

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break
        
        imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        frame_count += 1
        if frame_count % 20 == 0:
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    print(individual_ID[matchIndex])

        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Ensure the frame is in RGB
        pil_img = Image.fromarray(frame_rgb)

        # Resize the image to fit the LCD
        pil_img = pil_img.resize((240, 240))  # Adjust the size to match your LCD resolution

        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='BMP')
        img_byte_arr = img_byte_arr.getvalue()

        # Display the image on the LCD
        disp.lcd_ShowImage(img_byte_arr, 0, 0)

        # Also show the video feed on the screen
        cv2.imshow("Face video capture", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    face_rec()
