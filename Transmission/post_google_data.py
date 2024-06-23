import requests
import pymongo

# Function to fetch data from SheetDB
def fetch_data_from_sheetdb(sheetdb_url):
    response = requests.get(sheetdb_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to insert data into MongoDB
def insert_data_into_mongodb(mongodb_uri, database_name, collection_name, data):
    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]
    
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

# Main function to fetch data from SheetDB and export to MongoDB
def main(sheetdb_url, mongodb_uri, database_name, collection_name):
    data = fetch_data_from_sheetdb(sheetdb_url)
    insert_data_into_mongodb(mongodb_uri, database_name, collection_name, data)
    print("Data successfully exported to MongoDB")

# Replace the following placeholders with your actual values
SHEETDB_URL = 'https://sheetdb.io/api/v1/r1anxxi09w85o'
username = "Exoeon1"
password = "adamcoolboy"
DATABASE_NAME = "isdpData"
COLLECTION_NAME = "name_image"
connection_string = f"mongodb+srv://{username}:{password}@isdpdb.rgnbvb0.mongodb.net/"
MONGODB_URI = connection_string

if __name__ == "__main__":
    main(SHEETDB_URL, MONGODB_URI, DATABASE_NAME, COLLECTION_NAME)
