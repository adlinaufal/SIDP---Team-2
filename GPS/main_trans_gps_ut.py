import os
import sys
import time
import re
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from EncodingGenerator import img_encoder
from PIL import Image, ImageDraw, ImageFont
import traceback
import serial
from gps_utils import GetGPSData, uart_port, CoordinatestoLocation
import cv2
import pickle as pkl
import face_recognition
import numpy as np
from lcd_testing import lcd_display
import LCD2inch4_lib

WHITE = 0xFF
BLACK = 0x00
SPI_DEVICE = "/dev/spidev1.0"

# Function to extract file_id from Google Drive URL
def extract_file_id(url):
    pattern = r'id=([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("File ID not found in the URL")

# Function to sanitize filename
def sanitize_filename(name):
    # Replace spaces with hyphens in the name
    name = name.replace(' ', '-')
    # Remove any other invalid characters
    return re.sub(r'[/\\:*?"<>|]', '', name)

# Function to download image from Google Drive URL and rename it
def download_image_from_drive(url, folder_path, name, timestamp):
    try:
        file_id = extract_file_id(url)
        download_url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(download_url)

        name = sanitize_filename(name)
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
def update_location_in_sheet(name, timestamp_id, location_coord, client, spreadsheet_url, sheet_name):
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()

        for index, item in enumerate(data, start=2):  # start=2 because row 1 is headers
            if 'Name' in item and 'timestamp_id' in item:
                row_name = item['Name']
                row_timestamp_id = item['timestamp_id']
                if row_name == name and row_timestamp_id == timestamp_id:
                    worksheet.update_cell(index, worksheet.find('Location_coordinate').col, location_coord)
                    print(f"Updated location for {name} in row {index}: {location_coord}")
                    return True

        print(f"No matching row found for {name} with timestamp_id {timestamp_id}")
        return False

    except Exception as e:
        print("An error occurred while updating the location:", e)
        return False

#Function to display user image on lcd module
def lcd_display(userId, disp):

    disp.lcd_init_2inch4()

    # Retrieve the image
    image_path = os.path.join("images", f"{userId}.jpg")

    # Display the obtained image
    image = Image.open(image_path)
    image = image.resize((320, 240))
    disp.lcd_ShowImage(image, 0, 0)

# Function to perform face recognition
def face_rec(client, spreadsheet_url, sheet_name, disp):
    frame_count = 0
    video_capture = cv2.VideoCapture('/dev/video4')
    video_capture.set(3, 250)
    video_capture.set(4, 250)

    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
        encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID

    print(individual_ID)  # to check IDs loaded

    # Get the spreadsheet data
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet(sheet_name)
    data = worksheet.get_all_records()

    while video_capture.isOpened():
        disp.lcd_init_2inch4()
        disp.lcd_clear(BLACK)

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
                    print(f"Face recognized - {identified_id}\n")
                    lcd_display(identified_id, disp)

                    detected_name = identified_id.split('_')[0].replace('-', ' ')  # Convert hyphens back to spaces
                    detected_timestamp_id = '_'.join(identified_id.split('_')[1:])

                    # Check the spreadsheet for matching name and timestamp_id
                    matching_row = None
                    for row in data:
                        if row['Name'] == detected_name:
                            if row['timestamp_id'] == detected_timestamp_id:
                                matching_row = row
                                break

                    if matching_row:
                        name = matching_row['Name']
                        timestamp_id = matching_row['timestamp_id']
                        current_location = matching_row['Location_coordinate']

                        if current_location:
                            print(f"{name} (timestamp_id: {timestamp_id}) already has location")
                        else:
                            location_coord = get_location()
                            print(f"Location for {name} (timestamp_id: {timestamp_id}): {location_coord}")

                            if not update_location_in_sheet(name, timestamp_id, location_coord, client, spreadsheet_url, sheet_name):
                                print(f"Failed to update location for {name} with timestamp_id {timestamp_id}")
                    else:
                        print(f"No matching record found for detected face: {detected_name}")

        cv2.imshow("Face video_capture", frame)

# Main function to fetch data and encode images
def fetch_encode():
    try:
        disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)

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
                face_rec(client, SPREADSHEET_URL, SHEET_NAME, disp)

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
        print(traceback.format_exc())

if __name__ == "__main__":
    fetch_encode()