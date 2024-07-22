import multiprocessing
import time
import cv2
import os
import re
import sys
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder
from PIL import Image, ImageDraw, ImageFont
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
from __funct import img_encoder, download_img, remove_deleted_images
from lcd_utils import lcd_display

JSON_FILENAME = "sidp-facialrecognition-21f79db4b512"

def face_reg_runtime(stop_event, reload_event):
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

    while video_capture.isOpened() and not stop_event.is_set():
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            video_capture.release() 
            cv2.destroyAllWindows()
            break

        frame_count += 1
        
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
                    lcd_display(individual_ID[matchIndex])

        cv2.imshow("Face video_capture", frame)

        if reload_event.is_set():
            encodeListKnown, individual_ID = load_encoded_file()
            print("Reloaded:", individual_ID)
            reload_event.clear()

def fetching_encoding(current_directory, images_directory, JSON_FILENAME, stop_event, reload_event):
    while not stop_event.is_set(): 
        if download_img(current_directory, images_directory, JSON_FILENAME) or remove_deleted_images(current_directory, images_directory, JSON_FILENAME):
            encoded_file = os.path.join(current_directory, "EncodedFile.p")
            os.remove(encoded_file)
            img_encoder()
            reload_event.set()
        time.sleep(10)
    return

if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    
    stop_event = multiprocessing.Event()
    reload_event = multiprocessing.Event()

    try:
        download_img(current_directory, images_directory, JSON_FILENAME)
        img_encoder()
        
        p1 = multiprocessing.Process(target=face_reg_runtime, args=(stop_event, reload_event)) 
        p2 = multiprocessing.Process(target=fetching_encoding, args=(current_directory, images_directory, JSON_FILENAME, stop_event, reload_event))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except Exception as e:
        print(f"Exception in main: {e}")
        print(traceback.format_exc())

    print("Program Terminated")
