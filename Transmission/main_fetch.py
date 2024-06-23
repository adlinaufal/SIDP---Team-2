import pymongo
from pymongo.errors import ConnectionFailure
import os
import time
import fetch_data  # Assuming fetch_data.py contains download_image_from_drive function
import transmission_encodegen  # Assuming transmission_encodegen.py contains img_encoder function

def main():
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

        # Directory to store images
        current_directory = os.path.dirname(os.path.abspath(__file__))
        images_directory = os.path.join(current_directory, 'images')
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        while True:
            time.sleep(10)
            # Fetch all documents from collection
            data = collection.find()

            new_images_downloaded = False

            # Process each document
            for item in data:
                if 'Name' in item and 'Guest_Profile_Picture' in item and 'Timestamp' in item:
                    name = item['Name']
                    image_url = item['Guest_Profile_Picture']
                    timestamp = item['Timestamp']

                    # Generate expected file name
                    file_name = f"{name.replace(' ', '_')}_{timestamp.replace(' ', '').replace('/', '').replace(':', '')}.jpg"
                    file_path = os.path.join(images_directory, file_name)

                    # Check if the file already exists
                    if not os.path.exists(file_path):
                        # Download the image
                        fetch_data.download_image_from_drive(image_url, images_directory, name, timestamp)
                        new_images_downloaded = True
                    else:
                        print(f"Data exist: '{file_name}'")

                else:
                    print("Missing 'Name', 'Guest_Profile_Picture' or 'Timestamp' field in document.")
                    continue

            # Encode images if new images were downloaded
            if new_images_downloaded:
                transmission_encodegen.img_encoder()

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except ConnectionFailure as e:
        print("Failed to connect to MongoDB:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
