import threading
import time
import cv2
import os
# from EncodingGenerator import img_encoder
from FaceRecognition import face_rec
from main_trans import fetch_encode
import sys
import os
import time
import re
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder  # Assuming transmission_encodegen.py contains img_encoder function
from PIL import Image, ImageDraw, ImageFont  # PIL library for creating placeholder images
import traceback
from PIL import Image
import threading
import cv2
import pickle as pkl
import face_recognition
import numpy as np
import os

stop_threads = False
# import time module
def extract_file_id(url):
    pattern = r'id=([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("File ID not found in the URL")

# Function to download image from Google Drive URL and rename it
def download_image_from_drive(url, folder_path, name, timestamp):
    try:
        file_id = extract_file_id(url)
        download_url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(download_url)

        name = name.replace(' ', '_')
        timestamp = timestamp.replace(' ', '').replace('/', '').replace(':', '')

        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        with open(file_name, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded and saved file to '{file_name}'")
        return file_name

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        print(traceback.format_exc())
        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        create_placeholder_image(file_name)
        return file_name

# Function to create a placeholder image
def create_placeholder_image(filepath):
    image = Image.new('RGB', (200, 200), color='gray')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 90), "Placeholder", fill='white', font=font)
    image.save(filepath)

def sanitize_filename(name):
    return re.sub(r'[/\\: ]', '_', name)

def remove_deleted_images(current_file_names, previous_file_names, folder_path):
    global Flag
    deleted_files = previous_file_names - current_file_names
    for file_name in deleted_files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
            
            Flag = True
            img_encoder()
            Flag = False

def face_reg_runtime():
    global stop_threads
    global Flag
    frame_count = 0
    video_capture = cv2.VideoCapture(0) #For webcam (HD Pro Webcam C920) connected to VisionFive2 board
                                                    #'/dev/video4'
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
            stop_threads = True
            video_capture.release() 
            cv2.destroyAllWindows()
            break
        
        frame_count +=1
        if Flag == False:
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
        else:
            continue

        cv2.imshow("Face video_capture",frame)

def fetching_encoding():
    print("here 1")
    img_encoder()
    global stop_threads
    global Flag
    try:
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'  # Your Google Spreadsheet URL
        SHEET_NAME = 'Form Responses 1'  # Name of the specific sheet within your Google Spreadsheet

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = "sidp-facialrecognition-21f79db4b512"
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        images_directory = os.path.join(current_directory, 'images')
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        previous_file_names = set()

        while stop_threads != True:
            time.sleep(10)
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            data = worksheet.get_all_records()

            current_file_names = set()
            new_images_downloaded = False

            for item in data:
                if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
                    name = item['Name']
                    image_url = item['Guest_Profile_Picture']
                    timestamp = item['Timestamp']

                    sanitized_name = sanitize_filename(name)
                    sanitized_timestamp = re.sub(r'[/: ]', '', timestamp)
                    file_name = f"{sanitized_name}_{sanitized_timestamp}.jpg"
                    file_path = os.path.join(images_directory, file_name)
                    current_file_names.add(file_name)
                    # print(current_file_names)
                    print(file_path)

                    if not os.path.exists(file_path):
                        download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                        new_images_downloaded = True
                    else:
                        print(f"Data exists: '{file_name}'")

                    image = Image.open(file_path)
                    image = image.convert('RGB')
                    new_image = image.resize((960,720))
                    new_image.save(file_path)

                else:
                    print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                    continue

            remove_deleted_images(current_file_names, previous_file_names, images_directory)
            previous_file_names = current_file_names

            if new_images_downloaded:
                Flag = True
                img_encoder()
                Flag = False

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
    print("here 2")

        
Flag = False
# creating  threads
if __name__=='__main__':
  event_object = threading.Event()

lock = threading.RLock()
T1 = threading.Thread(target=face_reg_runtime)
T2 = threading.Thread(target=fetching_encoding)

 
# starting threads
T1.start()
T2.start()
T1.join()
T2.join()



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
"""


