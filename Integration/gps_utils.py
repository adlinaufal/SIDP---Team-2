import time
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
    NumberofRetries = 0
    RetriesLimit = 5

    while NumberofRetries < RetriesLimit:
        try:
            data = gps.readline()
            msg_str = str(data, encoding="utf-8").strip()
            if msg_str:
                break
        except Exception as e:
            NumberofRetries += 1
            time.sleep(1)
    else:
        print("An error occurred while reading GPS data!")
        print("Returning last value of GPS data...")
        return read_gps_data_from_file()

    # Split the message into components
    msg_list = msg_str.split(",")

    latitude = None
    longitude = None

    # Check for GPS data validity
    if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
        print()
        if msg_list[GPGSA_dict['mode2']] == "1":
            print("!!!!!!GPS Device is not ONLINE!!!!!!")
            print("Returning last value of GPS data...")
            return read_gps_data_from_file()

    if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
        lat_str = msg_list[GPGGA_dict["latitude"]]
        lon_str = msg_list[GPGGA_dict["longitude"]]

        if lat_str and lon_str:
            try:
                # Handle latitude conversion
                lat_deg = int(lat_str[:2])  # Latitude degrees
                lat_min = float(lat_str[2:])  # Latitude minutes
                lat_dir = msg_list[GPGGA_dict["NorS"]]

                # Handle longitude conversion
                lon_deg = int(lon_str[:3])  # Longitude degrees
                lon_min = float(lon_str[3:])  # Longitude minutes
                lon_dir = msg_list[GPGGA_dict["EorW"]]
                
                latitude = convert_to_decimal(lat_deg, lat_min, lat_dir)
                longitude = convert_to_decimal(lon_deg, lon_min, lon_dir)
                
                # Save the latitude and longitude to a file
                with open('gps_data.txt', 'w') as file:
                    file.write(f"Latitude: {latitude}\nLongitude: {longitude}\n")

            except:
                print("An error occured while reading GPS data!")
                print("Returning last value of GPS data...")
                return read_gps_data_from_file()
    
    return latitude, longitude

def read_gps_data_from_file(filename='gps_data.txt'):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            latitude_line = lines[0].strip()
            longitude_line = lines[1].strip()
            latitude = float(latitude_line.split(': ')[1])
            longitude = float(longitude_line.split(': ')[1])
            return latitude, longitude
    except (FileNotFoundError, IndexError, ValueError) as e:
        print(f"Error reading GPS data from file: {e}")
        return None, None
        
def CoordinatestoLocation(latitude, longitude):
    location = None
    if 4.385422 < latitude < 4.385959 and 100.979104 < longitude < 100.979822:
        location = "Gate 1" 
    elif 4.372665 < latitude < 4.373278 and 100.969167 < longitude < 100.969711:
        location = "Gate 3"
    else:
        location = "Neither Gate 1 nor Gate 3"

    return location
