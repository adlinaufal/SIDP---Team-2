import cv2
import pickle as pkl
import face_recognition
import numpy as np
import os
import platform
import time
import threading
from __funct import img_encoder,download_img,remove_deleted_images
JSON_FILENAME = ""
stop_threads = False
flag = False
def face_rec():
    global stop_threads
    global flag
    T1 = threading.Thread(target=camera)
    T1.start()
    while not stop_threads: 
        if download_img(current_directory,images_directory,JSON_FILENAME):
            flag = True
            img_encoder()
            absolute_path = os.path.dirname(__file__)
            flag = False
        if remove_deleted_images(current_directory,images_directory,JSON_FILENAME):
            flag = True
            img_encoder()
            flag = False
        time.sleep(10)
    T1.join()
    return



def camera():
    time.sleep(8)
    global stop_threads
    global flag
    frame_count = 0
    if platform.system() == 'Windows':
        video_capture = cv2.VideoCapture(0)
                                                    
    else:
        video_capture = cv2.VideoCapture('/dev/video4', cv2.CAP_GSTREAMER)

    video_capture.set(3, 250)
    video_capture.set(4, 250)

    #Load Encoding file
    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
        encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID

    print(individual_ID)# to check id's loaded

    while video_capture.isOpened(): 
        
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            stop_threads = True
            cv2.destroyAllWindows()
            return True

        frame_count +=1
        if flag == False:
            if frame_count % 20 == 0:
                
                imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                faceCurFrame = face_recognition.face_locations(imgS)
                encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

                for encodeFace,faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        print(individual_ID[matchIndex])

            cv2.imshow("Face video_capture",frame)
        else:
            time.sleep(2)
            with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
                encodeListKnown_withID = pkl.load(file)
            encodeListKnown, individual_ID = encodeListKnown_withID


if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    face_rec()
    