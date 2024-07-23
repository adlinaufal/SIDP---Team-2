import cv2
import face_recognition
import pickle as pkl
import os
import re
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Gtrans_enc import img_encoder  # Assuming transmission_encodegen.py contains img_encoder function
from PIL import Image, ImageDraw, ImageFont  # PIL library for creating placeholder images
import traceback

def img_encoder(): #[DONE]
    #Importing images
    absolute_path = os.path.dirname(__file__)
    relative_path = "images"
    folderPath = os.path.join(absolute_path, relative_path)
    PathList = os.listdir(folderPath)

    imgList = []
    individual_ID=[]

    for path in PathList:
        imgList.append(cv2.imread(os.path.join(folderPath,path)))
        individual_ID.append(path[:-4])
        #print(individual_ID)

    #Creating the encodings
    def findEncodings(imagesList):

        encoded_list = []
        for img in imagesList:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encoded_list.append(encode)

        return encoded_list

    print("Encoding Started")
    encodeListKnown = findEncodings(imgList)
    encodeListKnown_withID = [encodeListKnown, individual_ID]
    print("Encoding Complete")

    file = open(absolute_path + "//" "EncodedFile.p", "wb")
    pkl.dump(encodeListKnown_withID,file)
    file.close()
    print("File Saved")


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

# Function to add padding to make the image 4:3 ratio
def add_padding_to_make_4_3(image):
    width, height = image.size
    target_width = 4
    target_height = 3
    new_width = width
    new_height = height
    if width / height < target_width / target_height:
        new_width = target_height * width / height
        new_height = target_height
    else:
        new_width = target_width
        new_height = target_width * height / width
    new_width = int(new_width)
    new_height = int(new_height)

    result = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    result.paste(image, ((new_width - width) // 2, (new_height - height) // 2))
    return result

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

        # Open the downloaded image and convert to 4:3 ratio
        image = Image.open(file_name)
        image = image.convert('RGB')
        image = add_padding_to_make_4_3(image)
        image.save(file_name)

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

def download_img(current_directory, images_directory, JSON_FILENAME):
    try:
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'  # Your Google Spreadsheet URL
        SHEET_NAME = 'Form Responses 1'  # Name of the specific sheet within your Google Spreadsheet

        SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)

        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        spreadsheet = client.open_by_url(SPREADSHEET_URL)
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        row_count = len(data)
        print("Available data on Data Base ", row_count)

        current_file_names = set()
        new_images_downloaded = False

        headers = worksheet.row_values(1)
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

                worksheet.update_cell(index, worksheet.find('timestamp_id').col, sanitized_timestamp)

                if not os.path.exists(file_path):
                    download_image_from_drive(image_url, images_directory, sanitized_name, sanitized_timestamp)
                    new_images_downloaded = True

                else:
                    print(f"Data exists: '{file_name}'")

                image = Image.open(file_path)
                image = image.convert('RGB')
                new_image = image.resize((960, 720))
                new_image.save(file_path)

            else:
                print("Missing 'Name', 'Guest_Profile_Picture', or 'Timestamp' field in record.")
                continue

        if new_images_downloaded:
            return True

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)

def remove_deleted_images(current_directory, images_directory, JSON_FILENAME):
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1bqCo5PmQVNV7ix_kQarfSCTYC72P1c-qvrmTcu_Xb4E/edit?usp=sharing'  # Your Google Spreadsheet URL
    SHEET_NAME = 'Form Responses 1'  # Name of the specific sheet within your Google Spreadsheet

    JSON_FILENAME = "sidp-facialrecognition-21f79db4b512"
    SERVICE_ACCOUNT_FILE = os.path.join(current_directory, JSON_FILENAME+'.json')

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    data = worksheet.get_all_records()
    database_file_names = set()

    for index, item in enumerate(data, start=2):
        if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
            name = item['Name']
            image_url = item['Guest_Profile_Picture']
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
