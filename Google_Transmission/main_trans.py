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

def fetch_encode():
    try:
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'  # Your Google Spreadsheet URL
        SHEET_NAME = 'Form Responses 1'  # Name of the specific sheet within your Google Spreadsheet

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = ""
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

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

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)

fetch_encode()
