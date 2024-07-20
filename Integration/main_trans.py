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
import sys
import serial
from gps_utils import GetGPSData, uart_port, CoordinatestoLocation

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
            img_encoder()

def get_location():
    gps = serial.Serial(uart_port, baudrate=9600, timeout=0.5)
    while True:
        latitude, longitude = GetGPSData(gps)
        if latitude is not None and longitude is not None:
            latitude = round(latitude, 6)
            longitude = round(longitude, 6)
            location = CoordinatestoLocation(latitude, longitude)
            print("\nLocation: ", location)
            print("Coordinates: {:.6f}, {:.6f}".format(latitude, longitude))
            return f"{latitude},{longitude}"
        else:
            print("GPS data not available. Retrying...")

<<<<<<< HEAD
def face_reg_runtime(worksheet, location_col):
    global stop_threads
    global Flag
    frame_count = 0
    video_capture = cv2.VideoCapture(0)  # For webcam

    video_capture.set(3, 250)
    video_capture.set(4, 250)

    # Load encoding file
    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
        encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID

    print(individual_ID)  # to check IDs loaded

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
                imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                faceCurFrame = face_recognition.face_locations(imgS)
                encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        name = individual_ID[matchIndex]
                        print(f"Detected {name}")

                        # Get GPS location when a face is detected
                        location_coord = get_location()
                        print(f"Location for {name}: {location_coord}")

                        # Update the spreadsheet with the location
                        cells = worksheet.findall(name)
                        for cell in cells:
                            worksheet.update_cell(cell.row, location_col, location_coord)
                            print(f"Updated location for {name} in row {cell.row}: {location_coord}")

        cv2.imshow("Face video_capture", frame)

=======
>>>>>>> parent of 0db6d68 (Update main_trans.py)
def fetch_encode():
    global stop_threads
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

        while not stop_threads:
            time.sleep(10)
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            data = worksheet.get_all_records()

            current_file_names = set()
            new_images_downloaded = False

            # Get the index of the "Location_coordinate" column, create it if it doesn't exist
            headers = worksheet.row_values(1)
            if "Location_coordinate" not in headers:
                worksheet.add_cols(1)
                worksheet.update_cell(1, len(headers) + 1, "Location_coordinate")
                location_col = len(headers) + 1
            else:
                location_col = headers.index("Location_coordinate") + 1

            for index, item in enumerate(data, start=2):
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
<<<<<<< HEAD

                        # Ask for location only when new data is detected
                        location_coord = get_location()
=======
                        
                        # Ask for location only when new data is detected
                        location_coord = get_location()

                        # Update location coordinate
>>>>>>> parent of 0db6d68 (Update main_trans.py)
                        worksheet.update_cell(index, location_col, location_coord)
                        print(f"Updated location for {name}: {location_coord}")
                    else:
                        print(f"Data exists: '{file_name}'")

                    image = Image.open(file_path)
                    image = image.convert('RGB')
                    new_image = image.resize((960, 720))
                    new_image.save(file_path)

                else:
                    print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                    continue

            remove_deleted_images(current_file_names, previous_file_names, images_directory)
            previous_file_names = current_file_names

            if new_images_downloaded:
                img_encoder()

        return worksheet, location_col

    except KeyboardInterrupt:
        stop_threads = True
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    event_object = threading.Event()

    worksheet, location_col = fetch_encode()

    # Creating threads
    T1 = threading.Thread(target=face_reg_runtime, args=(worksheet, location_col))
    T2 = threading.Thread(target=fetch_encode)

    # Starting threads
    T1.start()
    T2.start()

    # Waiting for threads to complete
    T1.join()
    T2.join()
