# This Python code is taking name and Google drive link of individual image (submitted through Google Form)
# Google Form link: https://forms.gle/pUNejqpEGKQCNFc87
# Google Form Editor: https://docs.google.com/forms/d/e/1FAIpQLSdMC_AtGfy27_7XVPqNkB0sR-jVoZ03-tE-KXZ9NbtB_ixXNA/viewform?usp=sharing
# Google Drive where the pictures are stored: https://drive.google.com/drive/folders/14DB1_KeYKi93TXHop5VRFAT-diAExltOBlex5jTaeVmlXBJ5JfpAEUnqgl8REkELeVuQGNn1

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

try:
    # MongoDB connection details
    username = "Exoeon1"
    password = "adamcoolboy"
    database_name = "isdpData"
    coll_name = "name_image"
    connection_string = f"mongodb+srv://{username}:{password}@isdpdb.rgnbvb0.mongodb.net/"

    # Connect to MongoDB
    print(f"Attempting to connect to MongoDB at {connection_string}...")
    client = pymongo.MongoClient(connection_string)
    print("Connected to MongoDB successfully!")

    # Access the database and collection
    db = client[database_name]
    collection = db[coll_name]

    # Fetch all documents from collection
    data = collection.find()

    # Directory to store images
    current_directory = os.path.dirname(os.path.abspath(__file__))
    images_directory = os.path.join(current_directory, 'images')
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    # Process each document
    for item in data:
        if 'name' in item and 'face_image' in item and 'timestamp' in item:
            name = item['name']
            image_url = item['face_image']
            timestamp = item['timestamp']

            # Attempt to download image from Google Drive URL and rename it
            download_image_from_drive(image_url, images_directory, name, timestamp)

        else:
            print("Missing 'name', 'face_image' or 'timestamp' field in document.")
            continue

except ConnectionFailure as e:
    print("Failed to connect to MongoDB:", e)
except Exception as e:
    print("An error occurred:", e)
