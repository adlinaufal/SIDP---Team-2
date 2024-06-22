import cv2
import face_recognition
import pickle as pkl
import os
from FaceRecognition import face_rec
from EncodingGenerator import img_encoder
import multiprocessing as MP
import threading

"""
The img_encoder() is the function that is responsible for encoding
of the input picture.

The face_rec() function is responsible for facial recognition mechanism
"""


if __name__ == "__main__":

    t1 = threading.Thread(target = img_encoder(), name= "thread 1")
    t2 = threading.Thread(target = face_rec(), name= "thread 2")

    t1.start()
    t2.start()

    t1.join()
    t2.join()

