#==========================mongopart============================#   

import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://Exoeon1:adamcoolboy@isdpdb.rgnbvb0.mongodb.net/")                #connecting to mongoDB
db = cluster["isdpData"]
collection = db["name_image"]

post = {
"name": "tryje",
"face_image": "https://drive.google.com/open?id=1XcNKIzvI4U3kaFGAGYJgxRknVCQpy4-n",
"timestamp": "6/23/2024 14:31:10"
}
collection.insert_one(post)

print(" User Data have been uploaded to cloud (MongoDB) successfully! ")