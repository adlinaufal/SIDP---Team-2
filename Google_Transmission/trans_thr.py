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
import threading
import queue
from memory_profiler import profile
import sys
import io

# Global variables
global_frame = None
frame_queue = queue.Queue(maxsize=1)
stop_event = threading.Event()
encode_lock = threading.Lock()

# Set up exception handling
def handle_exception(exc_type, exc_value, exc_traceback):
    print("An uncaught exception occurred:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

# Print library versions
print(f"OpenCV version: {cv2.__version__}")
print(f"face_recognition version: {face_recognition.__version__}")
print(f"numpy version: {np.__version__}")

def extract_file_id(url):
    pattern = r'id=([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("File ID not found in the URL")

def sanitize_filename(name):
    name = name.replace(' ', '-')
    return re.sub(r'[/\\:*?"<>|]', '', name)

def download_image_from_drive(url, folder_path, name, timestamp):
    try:
        file_id = extract_file_id(url)
        download_url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(download_url)

        name = sanitize_filename(name)
        timestamp = timestamp.replace(' ', '').replace('/', '').replace(':', '')

        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        
        # Open the image using PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Resize the image
        img_resized = img.resize((1024, 768), Image.LANCZOS)
        
        # Save the resized image
        img_resized.save(file_name, 'JPEG')

        print(f"Downloaded, resized, and saved file to '{file_name}'")
        return file_name

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        print(traceback.format_exc())
        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        create_placeholder_image(file_name)
        return file_name

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

def open_camera():
    global global_frame
    video_capture = cv2.VideoCapture('/dev/video4')
    video_capture.set(3, 250)
    video_capture.set(4, 250)

    while not stop_event.is_set():
        ret, frame = video_capture.read()
        if ret:
            global_frame = frame
            if frame_queue.full():
                frame_queue.get()
            frame_queue.put(frame)
        else:
            time.sleep(0.1)

    video_capture.release()
    cv2.destroyAllWindows()

def face_rec(client, spreadsheet_url, sheet_name):
    absolute_path = os.path.dirname(__file__)
    with open(os.path.join(absolute_path, "EncodedFile.p"), "rb") as file:
        encodeListKnown_withID = pkl.load(file)
    encodeListKnown, individual_ID = encodeListKnown_withID

    print(individual_ID)  # to check IDs loaded

    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                identified_id = individual_ID[matchIndex]
                print(f"Face recognized - {identified_id}\n")
                detected_name = identified_id.split('_')[0].replace('-', ' ')
                detected_timestamp_id = '_'.join(identified_id.split('_')[1:])

                process_recognized_face(client, spreadsheet_url, sheet_name, detected_name, detected_timestamp_id)

        cv2.imshow("Face video_capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()

def process_recognized_face(client, spreadsheet_url, sheet_name, detected_name, detected_timestamp_id):
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            spreadsheet = client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()

            for index, row in enumerate(data, start=2):
                if row['Name'] == detected_name and str(row['timestamp_id']) == detected_timestamp_id:
                    current_status = row['Status']
                    current_location = row['Location_coordinate']

                    if current_status == "Not yet check-in":
                        location_coord = get_location()
                        print(f"Location for {detected_name} (timestamp_id: {detected_timestamp_id}): {location_coord}")

                        if update_location_in_sheet(index, location_coord, client, spreadsheet_url, sheet_name):
                            print(f"Updated location for {detected_name}")
                        else:
                            print(f"Failed to update location for {detected_name}")
                    else:
                        print(f"Visitor {detected_name} has {current_status} previously. Last location: {current_location}")
                    return
            print(f"{detected_name} with timestamp {detected_timestamp_id} not found in database.")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error processing recognized face: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to process recognized face after {max_retries} attempts: {e}")

def safe_img_encoder():
    with encode_lock:
        try:
            img_encoder()
        except Exception as e:
            print(f"Error in img_encoder: {e}")
            traceback.print_exc()

def check_file_size(file_path, max_size_mb=10):
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > max_size_mb:
        print(f"Warning: Large file detected. {file_path} is {size_mb:.2f} MB")

@profile
def fetch_encode(client, spreadsheet_url, sheet_name):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    previous_file_names = set()

    while not stop_event.is_set():
        try:
            print("Fetching new data...")
            spreadsheet = client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()

            current_file_names = set()
            new_images_downloaded = False

            for index, item in enumerate(data, start=2):
                if all(key in item for key in ['Name', 'Guest_Profile_Picture', 'Timestamp']):
                    name = item['Name']
                    image_url = item['Guest_Profile_Picture']
                    timestamp = item['Timestamp']

                    sanitized_name = sanitize_filename(name)
                    sanitized_timestamp = re.sub(r'[/: ]', '', timestamp)
                    file_name = f"{sanitized_name}_{sanitized_timestamp}.jpg"
                    file_path = os.path.join(images_directory, file_name)
                    current_file_names.add(file_name)

                    worksheet.update_cell(index, worksheet.find('timestamp_id').col, sanitized_timestamp)
                    worksheet.update_cell(index, worksheet.find('Status').col, "Not yet check-in")

                    if not os.path.exists(file_path):
                        download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                        check_file_size(file_path)
                        new_images_downloaded = True
                    else:
                        print(f"Data exists: '{file_name}'")
                else:
                    print("Missing required fields in record.")

            remove_deleted_images(current_file_names, previous_file_names, images_directory)
            previous_file_names = current_file_names

            if new_images_downloaded:
                print(f"New images downloaded. Current files: {current_file_names}")
                print("Starting img_encoder...")
                safe_img_encoder()
                print("img_encoder completed.")

        except Exception as e:
            print(f"An error occurred in fetch_encode: {e}")
            traceback.print_exc()

        print("Sleeping for 5 seconds...")
        time.sleep(5)

def main():
    try:
        SPREADSHEET_URL = ''
        SHEET_NAME = ''

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = ""  # Replace with your actual JSON filename
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME + '.json')

        scope = []
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        # Start camera on Core 2
        camera_thread = threading.Thread(target=open_camera)
        camera_thread.start()

        # Start face recognition on Core 1
        face_rec_thread = threading.Thread(target=face_rec, args=(client, SPREADSHEET_URL, SHEET_NAME))
        face_rec_thread.start()

        # Run fetch_encode on main thread
        fetch_encode(client, SPREADSHEET_URL, SHEET_NAME)

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
        print(traceback.format_exc())
    finally:
        stop_event.set()
        camera_thread.join()
        face_rec_thread.join()

if __name__ == "__main__":
    main()