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
    while True:
        location = input("Enter location (latitude,longitude): ")
        try:
            lat, lng = map(float, location.split(','))
            return f"{lat},{lng}"
        except ValueError:
            print("Invalid format. Please enter as latitude,longitude (e.g., 40.7128,-74.0060)")

def fetch_encode():
    try:
        SPREADSHEET_URL = ''
        SHEET_NAME = ''

        current_directory = os.path.dirname(os.path.abspath(__file__))
        JSON_FILENAME = ""
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

        scope = []
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

            # Get the index of the "Location_coordinate" column, create it if it doesn't exist
            headers = worksheet.row_values(1)
            if "Location_coordinate" not in headers:
                worksheet.add_cols(1)
                worksheet.update_cell(1, len(headers) + 1, "Location_coordinate")
                location_col = len(headers) + 1
            else:
                location_col = headers.index("Location_coordinate") + 1

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

                    if not os.path.exists(file_path):
                        download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                        new_images_downloaded = True

                        # Ask for location only when new data is detected
                        location_coord = get_location()

                        # Update location coordinate
                        worksheet.update_cell(index, location_col, location_coord)
                        print(f"Updated location for {name}: {location_coord}")
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
        print(traceback.format_exc())

fetch_encode()