import cv2
import face_recognition
import pickle as pkl
import os
import re
import requests
import gspread
import traceback

from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw, ImageFont  # PIL library for creating placeholder images

import numpy as np


def fail_encoding(path, e):
    print(e)

    name, timestamp_id = path[:-4].split('_')
    name = name.replace('-', ' ')
    data = worksheet.get_all_records()

    for index, row in enumerate(data, start=2):
        if row['Name'] == name and str(row['timestamp_id']) == timestamp_id:
            worksheet.update_cell(index, worksheet.find('Image_Encoding_Status').col, "Failed")
            break

def img_encoder(): 
    absolute_path = os.path.dirname(__file__)
    relative_path = "images"
    folderPath = os.path.join(absolute_path, relative_path)
    PathList = os.listdir(folderPath)

    encodeListKnown = []
    individual_ID = []
    print("--------------------------------------------------")
    print("Encoding Started")
    for path in PathList:
        img_path = os.path.join(folderPath, path)
        img = cv2.imread(img_path)
        if img is not None:
            # Resize image to a smaller size for faster processing
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Try to find face locations first
            face_locations = face_recognition.face_locations(img, model="hog")
            
            if face_locations:
                # If face found, compute encoding
                face_encoding = face_recognition.face_encodings(img, face_locations)[0]
                encodeListKnown.append(face_encoding)
                individual_ID.append(path[:-4])
            else:
                e = (f"No faces found in image {path}")
                fail_encoding(path, e)
        else:
            e = (f"Warning: Unable to read image '{path}'.")
            fail_encoding(path, e)

    print("Encoding Complete")

    encodeListKnown_withID = [encodeListKnown, individual_ID]

    with open(os.path.join(absolute_path, "EncodedFile.p"), "wb") as file:
        pkl.dump(encodeListKnown_withID, file)
    print("File Saved")
    print("--------------------------------------------------")

def resize_image(image, target_width, target_height):
    h, w = image.shape[:2]
    aspect_ratio = w / h
    if aspect_ratio > 1:  # Landscape or square image
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:  # Portrait image
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
    
    # Ensure new dimensions are within the target size
    new_width = min(new_width, target_width)
    new_height = min(new_height, target_height)
    
    resized_img = cv2.resize(image, (new_width, new_height))
    
    # Create a new image with target size and place the resized image in the center
    new_image = 255 * np.ones((target_height, target_width, 3), dtype=np.uint8)
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    new_image[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_img

    return new_image

def create_img_file(): #[DONE]
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)
        return os.path.dirname(os.path.abspath(__file__)),os.path.join(current_directory, 'images')

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
    name = name.replace(' ', '-')
    return re.sub(r'[/\\:*?"<>|]', '', name)

def download_img(current_directory,images_directory,JSON_FILENAME):
    global worksheet

    try:
        SPREADSHEET_URL = ''  # Your Google Spreadsheet URL
        SHEET_NAME = ''  # Name of the specific sheet within your Google Spreadsheet

        #current_directory = os.path.dirname(os.path.abspath(__file__))#[done1]
        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

        scope = []
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        #images_directory = os.path.join(current_directory, 'images')#[done1]
        if not os.path.exists(images_directory):#[done1]
            os.makedirs(images_directory)#[done1]

        spreadsheet = client.open_by_url(SPREADSHEET_URL)
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        row_count = len(data)
        print("--------------------------------------------------")
        print("Available data on Data Base:",row_count)

        current_file_names = set()
        new_images_downloaded = False

        # Get the index of the "Location_coordinate" column, create it if it doesn't exist
        headers = worksheet.row_values(1)
        global guest_profile_picture
        guest_profile_picture = 'Guest Profile Picture (If your image is not in the 4:3 ratio, please crop or resize it before uploading)'
        for index, item in enumerate(data, start=2):
            if 'Name' in item and guest_profile_picture in item and 'Timestamp' in item:
                name = item['Name']
                image_url = item[guest_profile_picture]
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
                    print(f"Data exists in local: '{file_name}'")

                image = Image.open(file_path)
                image = image.convert('RGB')
                new_image = image.resize((960,720))
                new_image.save(file_path)

            else:
                print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                continue

        print("--------------------------------------------------")

        if new_images_downloaded:
            return True

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)

def remove_deleted_images(images_directory):
    data = worksheet.get_all_records()
    database_file_names = set()

    for index, item in enumerate(data, start=2):
        if 'Name' in item and guest_profile_picture in item and 'Timestamp' in item:
            name = item['Name']
            image_url = item[guest_profile_picture]
            timestamp = item['Timestamp']

            sanitized_name = sanitize_filename(name)
            sanitized_timestamp = re.sub(r'[/: ]', '', timestamp)
            file_name = f"{sanitized_name}_{sanitized_timestamp}.jpg"
            file_path = os.path.join(images_directory, file_name)
            database_file_names.add(file_name)

    dir_file_names = set()

    all_files = os.listdir(images_directory)

    for image_file in all_files:
        dir_file_names.add(image_file)
        
    deleted_files = dir_file_names - database_file_names
    for file_name in deleted_files:
        file_path = os.path.join(images_directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
            return True

if __name__ == "__main__":
    img_encoder()