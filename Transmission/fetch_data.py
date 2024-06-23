import pymongo
from pymongo.errors import ConnectionFailure
import os
import requests
import re
from PIL import Image, ImageDraw, ImageFont
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
        create_placeholder_image(os.path.join(folder_path, f"image_placeholder.jpg"))

# Function to create a placeholder image
def create_placeholder_image(filepath):
    image = Image.new('RGB', (200, 200), color='gray')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 90), "Placeholder", fill='white', font=font)
    image.save(filepath)

# Function to process each document
def process_document(item, images_directory):
    if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
        name = item['Name']
        image_url = item['Guest_Profile_Picture']
        timestamp = item['Timestamp']

        # Attempt to download image from Google Drive URL and rename it
        download_image_from_drive(image_url, images_directory, name, timestamp)
    else:
        print("Missing 'Name', 'Guest_Profile_Picture' or 'Timestamp' field in document.")
