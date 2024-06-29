# gps_utils.py

import os
import fcntl

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

def open_serial_port(port):
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    # Example: set non-blocking mode
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    return fd

def read_gps_data(fd):
    try:
        data = os.read(fd, 256)  # Read up to 256 bytes (adjust as needed)
        return data.decode('utf-8').strip()
    except OSError as e:
        print(f"Error reading from serial port: {e}")
        return None

def GetGPSData():
    latitude = None
    longitude = None

    serial_port = "/dev/ttyS6"
    serial_fd = open_serial_port(serial_port)
    if serial_fd:
        gps_data = read_gps_data(serial_fd)
        if gps_data:
            lines = gps_data.splitlines()
            for line in lines:
                msg_str = line.strip()
                msg_list = msg_str.split(",")

                if msg_list[GPGSA_dict['msg_id']] == "$GPGSA":
                    if msg_list[GPGSA_dict['mode2']] == "1":
                        print("!!!!!!!Failed to obtain GPS coordinates.!!!!!!!\n")
                        os.close(serial_fd)
                        return None, None
                    else:
                        print("***GPS coordinates successfully retrieved.***\n")

                if msg_list[GPGGA_dict['msg_id']] == "$GPGGA":
                    for key, value in GPGGA_dict.items():
                        if key == "latitude":
                            latitude = msg_list[GPGGA_dict[key]]
                        elif key == "longitude":
                            longitude = msg_list[GPGGA_dict[key]]

            os.close(serial_fd)
            if latitude and longitude:
                return latitude, longitude
        else:
            print("Failed to read GPS data.")
            os.close(serial_fd)
            return None, None
    else:
        print(f"Failed to open serial port {serial_port}")
        return None, None
