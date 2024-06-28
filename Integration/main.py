import threading
import time
import cv2
from EncodingGenerator import img_encoder
from FaceRecognition import face_rec
import sys

stop_thread = False
# import time module
def face_reg_runtime():
    while stop_thread != True:
        if face_rec():
            break
        

# creating  threads
T1 = threading.Thread(target=face_reg_runtime)

 
# starting threads
T1.start()
T1.join()
print("Program Terminated")


"""
PROGRESS REPORT
Progress 1:
    Create thread 1 which runs face_rec() function. When the function start it
    will begin to detect the faces of individual that have been encoded in the 
    EncodedFile.p. When q is pressed on the keyboard, the function will exit -
    and wil stop the program. This can be use to stop the whole program execu-
    tion.
"""