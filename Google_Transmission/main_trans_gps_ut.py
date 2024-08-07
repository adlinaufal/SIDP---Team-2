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

# Function to sanitize filename
def sanitize_filename(name):
    name = name.replace(' ', '-')
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
def update_location_in_sheet(row_number, location_coord, client, spreadsheet_url, sheet_name):
    try:
        print(f"Row number: {row_number}")
        print(f"Location coordinate: {location_coord}")
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.update_cell(row_number, worksheet.find('Location_coordinate').col, location_coord)
        worksheet.update_cell(row_number, worksheet.find('Status').col, "Checked-in")
        print(f"Updated location in row {row_number}: {location_coord}")
        return True
    except Exception as e:
        print("An error occurred while updating the location:", e)
        return False

# Function to perform face recognition
def face_rec(client, spreadsheet_url, sheet_name):
    fetch_encode()
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
                    data = worksheet.get_all_records()

                    identified_id = individual_ID[matchIndex]
                    print(f"Face recognized - {identified_id}\n")
                    detected_name = identified_id.split('_')[0].replace('-', ' ')
                    detected_timestamp_id = '_'.join(identified_id.split('_')[1:])

                    # Check the spreadsheet for matching name and timestamp_id
                    for index, row in enumerate(data, start=2):  # start=2 because row 1 is headers
                        if row['Name'] == detected_name:
                            timestamp_id_data = f"{row['timestamp_id']}"
                            detected_timestamp_id = f"{detected_timestamp_id}"

                            if timestamp_id_data == detected_timestamp_id:
                                print(f"Matching row number: {index}")
                                name = row['Name']
                                timestamp_id = row['timestamp_id']
                                current_status = row['Status']
                                current_location = row['Location_coordinate']

                                if current_status == "Not yet check-in":
                                    location_coord = get_location()
                                    print(f"Location for {name} (timestamp_id: {timestamp_id}): {location_coord}")

                                    if not update_location_in_sheet(index, location_coord, client, spreadsheet_url, sheet_name):
                                        print(f"Failed to update location for {name} with timestamp_id {timestamp_id}")
                                else:
                                    print(f"Our records indicate this visitor has {current_status} previously. Their last recorded location was at {current_location}.")
                                break
                            else:
                                print(f"{timestamp_id_data} is not found in database. Please register again.")
                                break
                            
                        else:
                            print(f"{detected_name} is not found in database. Please register again.")
                            break

                    break

        cv2.imshow("Face video_capture", frame)

# Main function to fetch data and encode images
def fetch_encode():
    try:
        SPREADSHEET_URL = ''
        SHEET_NAME = ''

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = ""
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME + '.json')

        scope = []
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        images_directory = os.path.join(current_directory, 'images')
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        previous_file_names = set()
        last_row_count = 0

        while True:
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            data = worksheet.get_all_records()

            current_row_count = len(data)
            current_file_names = set()
            new_images_downloaded = False

            # Check if there are new rows or if any existing row has been modified
            if current_row_count != last_row_count or any(row != worksheet.row_values(i+2) for i, row in enumerate(data)):
                print("Changes detected in the spreadsheet. Updating...")
                
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
                        
                        # Only update status if it's not already set
                        if not item.get('Status'):
                            worksheet.update_cell(index, worksheet.find('Status').col, "Not yet check-in")

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

                last_row_count = current_row_count
            
            else:
                print("No changes detected in the spreadsheet.")

            # Run face recognition regardless of changes

            # Wait for a short period before checking again
            time.sleep(5)

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
        print(traceback.format_exc())

# Run the main function
if __name__ == "__main__":
    fetch_encode()
