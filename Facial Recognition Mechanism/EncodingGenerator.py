import cv2
import face_recognition
import pickle as pkl
import os

def img_encoder():
    #Importing images
    absolute_path = os.path.dirname(__file__)
    relative_path = "images"
    folderPath = os.path.join(absolute_path, relative_path)
    PathList = os.listdir(folderPath)

    imgList = []
    individual_ID=[]

    for path in PathList:
        image = cv2.imread(os.path.join(folderPath,path))
        image.astype('uint8')
        imgList.append(image)
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
img_encoder()