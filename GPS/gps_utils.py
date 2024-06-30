# Reference information of the GPGSA format.
GPGSA_dict = {
    "msg_id": 0,
    "mode1": 1,
    "mode2": 2,
    "ch1": 3,
    "ch2": 4,
    "ch3": 5,
    "ch4": 6,
    "ch5": 7,
    "ch6": 8,
    "ch7": 9,
    "ch8": 10,
    "ch9": 11,
    "ch10": 12,
    "ch11": 13,
    "ch12": 14,
}

# Reference information of the GPGGA format.
GPGGA_dict = {
    "msg_id": 0,
    "utc": 1,
    "latitude": 2,
    "NorS": 3,
    "longitude": 4,
    "EorW": 5,
    "pos_indi": 6,
    "total_Satellite": 7,
}

def GetGPSData(gps):
    latitude = None
    longitude = None
    #Iterating through the GPS data
    for data in gps:
        msg_str = data.strip()
        msg_list = msg_str.split(",")
        #Checking if the GPS coordinates are successfully retrieved
        if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
            if msg_list[GPGSA_dict['mode2']] == "1":
                print("!!!!!!!Failed to obtain GPS coordinates.!!!!!!!\n")
                return None, None

            else:
                print("***GPS coordinates successfully retrieved.***\n")
        #Parsing the latitude and longitude from the GPGGA message
        if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
            for key, value in GPGGA_dict.items():
                if key == "latitude":
                    latitude = msg_list[GPGGA_dict[key]]
                elif key == "longitude":
                        longitude = msg_list[GPGGA_dict[key]]
    #Returning the latitude and longitude
    if latitude and longitude:
        return latitude, longitude
    #Returning None if the latitude and longitude are not found
    return None, None
