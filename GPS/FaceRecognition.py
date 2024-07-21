import cv2
import pickle as pkl
import face_recognition
import numpy as np
import os

from lcd_testing import lcd_display

def face_rec():
    frame_count = 0
    video_capture = cv2.VideoCapture(0) #VideoCapture(0)= For internal webcam, VideoCapture(1)= For external webcam
    video_capture.set(3, 500)
    video_capture.set(4, 500)

    #Load Encoding file
    absolute_path = os.path.dirname(__file__)
    file = open(absolute_path + "//" + "EncodedFile.p","rb")
    encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID
    file.close()

    print(individual_ID)# to check id's loaded

    while video_capture.isOpened(): 
        
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

        imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_count +=1
        if frame_count % 20 == 0:

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for encodeFace,faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    print(individual_ID[matchIndex])
                    lcd_display(imgS)

        cv2.imshow("Face video_captureture",frame)

    video_capture.release() 
    cv2.destroyAllWindows()

face_rec()