from flask import Flask, request, jsonify
import pymongo

app = Flask(__name__)

# Function to insert data into MongoDB
def insert_data_into_mongodb(mongodb_uri, database_name, collection_name, data):
    client = pymongo.MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]
    collection.insert_one(data)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    mongodb_uri = 'mongodb+srv://Exoeon1:adamcoolboy@isdpdb.rgnbvb0.mongodb.net/'
    database_name = 'isdpData'
    collection_name = 'name_image'
    insert_data_into_mongodb(mongodb_uri, database_name, collection_name, data)
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(port=80, debug=True)
