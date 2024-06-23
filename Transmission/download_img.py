import os
import requests
import re

# Function to extract file_id from Google Drive URL
def extract_file_id(url):
    # Regular expression to extract file_id from URL
    pattern = r'id=([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("File ID not found in the URL")

# Example Google Drive URL
google_drive_url = 'https://drive.google.com/open?id=1VXwPPCQhZGQnqxiHV9SGBZgLAwqWX3Kn'

try:
    # Extract file_id from the URL
    file_id = extract_file_id(google_drive_url)

    # URL template for downloading file from Google Drive
    url = f"https://drive.google.com/uc?id={file_id}"

    # Path to the folder where the image will be saved
    folder_path = os.path.join(os.getcwd(), 'images')

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Send a request to download the file
    response = requests.get(url)

    # Save the downloaded file
    file_name = os.path.join(folder_path, f"image_{file_id}.jpg")  # You can adjust the filename as needed
    with open(file_name, 'wb') as f:
        f.write(response.content)

    print(f"Downloaded and saved file to '{file_name}'")

except ValueError as e:
    print(f"Error: {e}")
