import os
import time
import re
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gtransmission_encodegen import img_encoder  # Assuming transmission_encodegen.py contains img_encoder function
from PIL import Image, ImageDraw, ImageFont  # PIL library for creating placeholder images
import traceback

# Function to extract file_id from Google Drive URL
def extract_file_id(url):
    # Regular expression to extract file_id from URL
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

        # Send a request to download the file
        response = requests.get(download_url)

        # Replace spaces with underscores in the name
        name = name.replace(' ', '_')

        # Replace spaces, slashes, and colons in the timestamp with no space
        timestamp = timestamp.replace(' ', '').replace('/', '').replace(':', '')

        # Save the downloaded file with the modified name
        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        with open(file_name, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded and saved file to '{file_name}'")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        print(traceback.format_exc())
        create_placeholder_image(os.path.join(folder_path, f"{name}_{timestamp}.jpg"))

# Function to create a placeholder image
def create_placeholder_image(filepath):
    image = Image.new('RGB', (200, 200), color='gray')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 90), "Placeholder", fill='white', font=font)
    image.save(filepath)

def sanitize_filename(name):
    return re.sub(r'[/\\: ]', '_', name)

def fetch_encode():
    try:
        # Replace with your Google Sheets configuration
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'  # Your Google Spreadsheet URL
        SHEET_NAME = 'Form Responses 1'  # Name of the specific sheet within your Google Spreadsheet

        # Get the directory of the current script
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the absolute path to your service account JSON file
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, 'sidp-facialrecognition-97936b0850c8.json')

        # Authenticate with Google Sheets using service account credentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        while True:
            time.sleep(10)

            # Directory to store images
            images_directory = os.path.join(current_directory, 'images')
            if not os.path.exists(images_directory):
                os.makedirs(images_directory)

            # Open the spreadsheet and select the worksheet
            spreadsheet = client.open_by_url(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(SHEET_NAME)

            # Fetch all records from the worksheet
            data = worksheet.get_all_records()

            new_images_downloaded = False

            # Process each record
            for item in data:
                if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
                    name = item['Name']
                    image_url = item['Guest_Profile_Picture']
                    timestamp = item['Timestamp']

                    # Generate expected file name
                    sanitized_name = sanitize_filename(name)
                    sanitized_timestamp = re.sub(r'[/: ]', '', timestamp)
                    file_name = f"{sanitized_name}_{sanitized_timestamp}.jpg"
                    file_path = os.path.join(images_directory, file_name)

                    # Check if the file already exists
                    if not os.path.exists(file_path):
                        # Download the image from Google Drive and rename it
                        download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                        new_images_downloaded = True
                    else:
                        print(f"Data exists: '{file_name}'")

                else:
                    print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                    continue

            # Encode images if new images were downloaded
            if new_images_downloaded:
                img_encoder()

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)

fetch_encode()
