import multiprocessing
import threading
import time
import cv2
import os
import traceback
import pickle as pkl
import face_recognition
import platform
import gspread
import serial

from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder
from __funct_2 import img_encoder, download_img, remove_deleted_images
from lcd_utils import lcd_display, initialize_lcd
from gps_utils import CoordinatestoLocation, uart_port, GetGPSData

import numpy as np

JSON_FILENAME = "sidp-facialrecognition-21f79db4b512"

# Function to get location from user input
def get_location():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = GetGPSData(gps)
        if latitude is not None and longitude is not None:
            location = CoordinatestoLocation(latitude, longitude)
            break
    
    return latitude, longitude, location

# Function to update the location coordinates in Google Sheets
def update_location_in_sheet(row_number, location_coord, location, client, spreadsheet_url, sheet_name):
    try:
        print(f"Location coordinate: {location_coord}")
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name)
        start_time = time.time()
        worksheet.update_cell(row_number, worksheet.find('Location_coordinate').col, location_coord)
        worksheet.update_cell(row_number, worksheet.find('Location').col, location)
        worksheet.update_cell(row_number, worksheet.find('Status').col, "Checked-in")
        end_time = time.time()
        print(f"Time taken to update location: {end_time - start_time} seconds")
        return True
    except Exception as e:
        print("An error occurred while updating the location:", e)
        return False

# Function to run facial recognition
def face_reg_runtime(stop_event, reload_event, client, spreadsheet_url, sheet_name):
    frame_count = 0

    # Initialize the LCD display once
    initialize_lcd()

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
        return encodeListKnown_withID

    encodeListKnown, individual_ID = load_encoded_file()
    print(individual_ID)

    # Get the spreadsheet data once before starting the loop
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet(sheet_name)

    while video_capture.isOpened() and not stop_event.is_set():
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            video_capture.release()
            cv2.destroyAllWindows()
            break

        frame_count += 1
        
        if frame_count % 20 == 0:
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    print("--------------------------------------------------")
                    userID = individual_ID[matchIndex]
                    print(userID)

                    # Call the lcd_display function to update the display
                    lcd_display(userID)

                    detected_name = userID.split('_')[0].replace('-', ' ')  # Convert hyphens back to spaces
                    detected_timestamp_id = '_'.join(userID.split('_')[1:])

                    # Check the spreadsheet for matching name and timestamp_id
                    data = worksheet.get_all_records()  # Consider optimizing this if data doesn't change often

                    for index, row in enumerate(data, start=2):  # start=2 because row 1 is headers
                        if row['Name'] == detected_name and str(row['timestamp_id']) == detected_timestamp_id:
                            name = row['Name']
                            timestamp_id = row['timestamp_id']
                            current_status = row['Status']
                            current_coordinates = row['Location_coordinate']
                            current_location = row['Location']

                            if current_status == "" or current_status is None:
                                latitude, longitude, location = get_location()
                                location_coord = f"{latitude:.6f}, {longitude:.6f}"
                                print(f"Location for {name} (timestamp_id: {timestamp_id}): {location_coord}")

                                threading.Thread(target=update_location_in_sheet, args=(index, location_coord, location, client, spreadsheet_url, sheet_name)).start()
                            else:
                                print(f"Our records indicate this visitor has {current_status} previously. Their last recorded location was at {current_coordinates}, ({current_location}).")
                            break
                        else:
                            print(f"{detected_name} is not found in database. Please register again.")

                    print("--------------------------------------------------")

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
        time.sleep(30)
    return

if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')

    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'
    SHEET_NAME = 'Form Responses 1'

    current_directory = os.path.dirname(os.path.abspath(__file__))
    JSON_FILENAME = JSON_FILENAME
    SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME + '.json')
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)    

    stop_event = multiprocessing.Event()
    reload_event = multiprocessing.Event()

    try:
        download_img(current_directory, images_directory, JSON_FILENAME)
        img_encoder()
        
        p1 = multiprocessing.Process(target=face_reg_runtime, args=(stop_event, reload_event, client, SPREADSHEET_URL, SHEET_NAME)) 
        p2 = multiprocessing.Process(target=fetching_encoding, args=(current_directory, images_directory, JSON_FILENAME, stop_event, reload_event))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except Exception as e:
        print(f"Exception in main: {e}")
        print(traceback.format_exc())

    print("Program Terminated")
