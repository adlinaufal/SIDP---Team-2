import os
import time
import re
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder
from PIL import Image, ImageDraw, ImageFont
import traceback
import serial
from gps_utils_ut import GetGPSData, uart_port, CoordinatestoLocation
import cv2
import pickle as pkl
import face_recognition
import numpy as np

# Function to extract file_id from Google Drive URL
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
    deleted_files = previous_file_names - current_file_names
    for file_name in deleted_files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

# Function to get location from user input
def get_location():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = GetGPSData(gps)
        if latitude is not None and longitude is not None:
            location = CoordinatestoLocation(latitude, longitude)
            print("\nLocation: ", location)
            latitude = f"{latitude:.6f}"
            longitude = f"{longitude:.6f}"
            print("Coordinates: {}, {}".format(latitude, longitude))
            return f"{latitude},{longitude}"

# Function to update the location coordinates in Google Sheets
def update_location_in_sheet(name, timestamp, location_coord, client, spreadsheet_url, sheet_name):
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()

        for index, item in enumerate(data, start=2):  # start=2 because row 1 is headers
            if 'Name' in item and 'timestamp_id' in item:
                row_name = item['Name']
                row_timestamp = item['timestamp_id']
                if row_name == name and row_timestamp == timestamp:
                    worksheet.update_cell(index, worksheet.find('Location_coordinate').col, location_coord)
                    print(f"Updated location for {name} in row {index}: {location_coord}")
                    return True

        print(f"No matching row found for {name} with timestamp_id {timestamp}")
        return False

    except Exception as e:
        print("An error occurred while updating the location:", e)
        return False

# Function to perform face recognition
def face_rec(client, spreadsheet_url, sheet_name):
    frame_count = 0
    video_capture = cv2.VideoCapture(0)  # For webcam (HD Pro Webcam C920) connected to VisionFive2 board
    video_capture.set(3, 250)
    video_capture.set(4, 250)

    # Load Encoding file
    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
        encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID

    print(individual_ID)  # to check IDs loaded

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            return True

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
                    identified_id = individual_ID[matchIndex]
                    name, timestamp = identified_id.split('_', 1)  # Split only once at the first underscore

                    location_coord = get_location()
                    print("SHOW ME THIS OUTPUT ADLI")
                    print(f"Location for {identified_id}: {location_coord}")

                    # Update the Google Sheet with the location coordinates
                    if not update_location_in_sheet(name, timestamp, location_coord, client, spreadsheet_url, sheet_name):
                        print(f"Failed to update location for {name} with timestamp {timestamp}")

        cv2.imshow("Face video_capture", frame)

# Main function to fetch data and encode images
def fetch_encode():
    try:
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'
        SHEET_NAME = 'Form Responses 1'

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = ""
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME + '.json')

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        images_directory = os.path.join(current_directory, 'images')
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        previous_file_names = set()

        while True:
            time.sleep(10)
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            data = worksheet.get_all_records()

            current_file_names = set()
            new_images_downloaded = False

            for index, item in enumerate(data, start=2):  # start=2 because row 1 is headers
                if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
                    name = item['Name']
                    image_url = item['Guest_Profile_Picture']
                    timestamp = item['Timestamp']

                    sanitized_name = sanitize_filename(name)
                    sanitized_timestamp = re.sub(r'[/: ]', '', timestamp)
                    file_name = f"{sanitized_name}_{sanitized_timestamp}.jpg"
                    file_path = os.path.join(images_directory, file_name)
                    current_file_names.add(file_name)

                    # Update the Google Sheet with the sanitized timestamp in 'timestamp_id' column
                    worksheet.update_cell(index, worksheet.find('timestamp_id').col, sanitized_timestamp)

                    if not os.path.exists(file_path):
                        download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                        new_images_downloaded = True
                    else:
                        print(f"Data exists: '{file_name}'")

                else:
                    print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                    continue

            remove_deleted_images(current_file_names, previous_file_names, images_directory)
            previous_file_names = current_file_names

            if new_images_downloaded:
                img_encoder()
                face_rec(client, SPREADSHEET_URL, SHEET_NAME)

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
        print(traceback.format_exc())

fetch_encode()
