import multiprocessing
import time
import cv2
import os
import time
import re
import sys
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder  # Assuming transmission_encodegen.py contains img_encoder function
from PIL import Image, ImageDraw, ImageFont  # PIL library for creating placeholder images
import traceback
import threading
import pickle as pkl
import face_recognition
import numpy as np
import serial
from gps_utils import GetGPSData, uart_port, CoordinatestoLocation
import platform
from PIL import Image
import io
from __funct import img_encoder,download_img,remove_deleted_images
from lcd_utils import lcd_display
import os
import sys
import time
import logging
from PIL import Image, ImageDraw, ImageFont

sys.path.append("..")

import LCD2inch4_lib

WHITE = 0xFF
BLACK = 0x00

JSON_FILENAME = "sidp-facialrecognition-21f79db4b512"
          
def face_reg_runtime():
    global stop_threads
    global Flag
    frame_count = 0

    if platform.system() == 'Windows':
        video_capture = cv2.VideoCapture(0)                                         
    else:
        video_capture = cv2.VideoCapture('/dev/video4') 
                                                    
    video_capture.set(3, 250)
    video_capture.set(4, 250)

    absolute_path = os.path.dirname(__file__)

    def load_encoded_file():
        with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
            encodeListKnown_withID = pkl.load(file)
            file.close()
            return encodeListKnown_withID

    encodeListKnown, individual_ID = load_encoded_file()
    print(individual_ID)

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_threads = True
            video_capture.release() 
            cv2.destroyAllWindows()
            break

        frame_count += 1
        if not Flag:
            
            if frame_count % 20 == 0:
                imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                faceCurFrame = face_recognition.face_locations(imgS)
                encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        print(individual_ID[matchIndex])
                        name_idx = individual_ID[matchIndex]
                        lcd_display(individual_ID[matchIndex])

            cv2.imshow("Face video_capture", frame)

        else:
            print(individual_ID)
            time.sleep(10)
            encodeListKnown, individual_ID = load_encoded_file()
            print("Reloaded:", individual_ID)
    
def lcd_display(name_idx):
    global stop_threads
    if name_idx:

        SPI_DEVICE = "/dev/spidev1.0"

        disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)
        disp.lcd_init_2inch4()

        # Retrieve the image
        image_path = os.path.join("images", f"{name_idx}.jpg")

        # Display the obtained image
        image = Image.open(image_path)
        image = image.resize((320, 240))
        disp.lcd_ShowImage(image, 0, 0)
        time.sleep(1.5)

        # Clear the display
        disp.lcd_init_2inch4()
        disp.lcd_clear(BLACK)
        time.sleep(1.5)
        

def fetching_encoding(current_directory,images_directory,JSON_FILENAME):
    print("here 1")
    global stop_threads
    global Flag

    while not stop_threads: 
        if download_img(current_directory,images_directory,JSON_FILENAME):
            Flag = True
            encoded_file = os.path.join(current_directory, "EncodedFile.p")
            os.remove(encoded_file)
            img_encoder()
            Flag = False
        if remove_deleted_images(current_directory,images_directory,JSON_FILENAME):
            Flag = True
            encoded_file = os.path.join(current_directory, "EncodedFile.p")
            os.remove(encoded_file)
            img_encoder()
            Flag = False
        time.sleep(10)
    return

stop_threads = False 
Flag = False
# creating  threads
if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    try:
        

        download_img(current_directory,images_directory,JSON_FILENAME)
        img_encoder()
        
        p1 = multiprocessing.Process(target=face_reg_runtime) 
        p2 = multiprocessing.Process(target=fetching_encoding,args=(current_directory,images_directory,JSON_FILENAME,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except Exception as e:
        print(f"Exception in main: {e}")
        print(traceback.format_exc())

    print("Program Terminated")


"""
PROGRESS REPORT
Progress 1:
    Create thread 1 which runs face_rec() function. When the function start it
    will begin to detect the faces of individual that have been encoded in the 
    EncodedFile.p. When q is pressed on the keyboard, the function will exit -
    and wil stop the program. This can be use to stop the whole program execu-
    tion.

Progress 2:
    Combined main_trans file with main.py file due to thread handling difficulties.
    Successfully terminated the program by pressing Q on keyboard.

Progress 3:
    Successfully make the threads run together. The first problem encountered is
    when a new registration happened and the EncodedFile.p need to be encoded again,
    the threads will stop running due to file access conflict. The first approach is
    to use thread management system. However, the structure of the program itself,
    does not fit with the thread management. The successful approach is to disable
    file reading in the face_recognition function. This allow the EncodedFile.p to
    be able to encode again without interrupting the running threads.
    Next task-> include GPS reading when individual face is detected.

    Update: Opt to use multiprocessing as compared to threads
"""