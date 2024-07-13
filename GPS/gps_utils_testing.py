import serial

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

uart_port = "/dev/ttyS0"

def convert_to_decimal(degrees, minutes, direction):
    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def GetGPSData(gps):
    while True:
        try:
            data = gps.readline()
            msg_str = str(data, encoding="utf-8")
            print("Raw data:", msg_str)  # Debug print
            break
        except (UnicodeDecodeError, serial.serialutil.SerialException):
            pass
        except Exception:
            pass

    msg_list = msg_str.split(",")

    latitude = None
    longitude = None

    print("Parsed message list:", msg_list)  # Debug print

    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
        print("GPGSA detected")
        if msg_list[GPGSA_dict['mode2']] == "1":
            print("!!!!!!Positioning is invalid!!!!!!")
            return None, None

    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        print("GPGGA detected")
        lat_str = msg_list[GPGGA_dict["latitude"]]
        lon_str = msg_list[GPGGA_dict["longitude"]]
        print("Latitude string:", lat_str)  # Debug print
        print("Longitude string:", lon_str)  # Debug print
        if lat_str and lon_str:
            lat_len = len(lat_str.split(".")[0])
            lon_len = len(lon_str.split(".")[0])
            
            lat_deg = int(lat_str[:lat_len-2])
            lat_min = float(lat_str[lat_len-2:])
            lat_dir = msg_list[GPGGA_dict["NorS"]]
            
            lon_deg = int(lon_str[:lon_len-2])
            lon_min = float(lon_str[lon_len-2:])
            lon_dir = msg_list[GPGGA_dict["EorW"]]
            
            latitude = convert_to_decimal(lat_deg, lat_min, lat_dir)
            longitude = convert_to_decimal(lon_deg, lon_min, lon_dir)
    
    return latitude, longitude
