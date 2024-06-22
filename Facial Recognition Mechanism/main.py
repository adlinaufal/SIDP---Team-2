import cv2
import face_recognition
import pickle as pkl
import os
from FaceRecognition import face_rec
from EncodingGenerator import img_encoder
import multiprocessing as MP

"""
The img_encoder() is the function that is responsible for encoding
of the input picture.

The face_rec() function is responsible for facial recognition mechanism
"""


if __name__ == "__main__":

    p1 = MP.Process(target = img_encoder())
    p2 = MP.Process(target = face_rec())

    p1.start()
    p2.start()

    p1.join()
    p2.join()

