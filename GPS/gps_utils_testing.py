import sys
import serial
import time

GPGSA_dict = {
"msg_id": 	0,
"mode1": 	1,
"mode2": 	2,
"ch1":          3,
"ch2":          4,
"ch3":          5,
"ch4":          6,
"ch5":          7,
"ch6":          8,
"ch7":          9,
"ch8":          10,
"ch9":          11,
"ch10":         12,
"ch11":         13,
"ch12":         14,
}

GPGGA_dict = {
"msg_id": 		0,
"utc": 		        1,
"latitude":             2,
"NorS":                 3,
"longitude":            4,
"EorW":                 5,
"pos_indi":             6,
"total_Satellite":      7,
}

def GetGPSData(gps):
    data = gps.readline()
    #Convert the data to string. 
    msg_str = str(data, encoding="utf-8")
    msg_list = msg_str.split(",")
    
    #Parse the GPGSA message.
    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
        if msg_list[GPGSA_dict['mode2']] == "1":
            print("!!!!!!!Failed to obtain GPS coordinates.!!!!!!!\n")
            return None, None
        else:
            print("***GPS coordinates successfully retrieved.***\n")

    #Parse the GPGGA message. 
        if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
            for key, value in GPGGA_dict.items():
                if key == "latitude":
                    latitude = msg_list[GPGGA_dict[key]]
                elif key == "longitude":
                        longitude = msg_list[GPGGA_dict[key]]

    if latitude and longitude:
        return latitude, longitude
            
    return None, None